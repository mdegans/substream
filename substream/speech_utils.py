import json
import logging
import os
import time
import urllib.parse
from typing import (
    Any,
    Iterable,
    Iterator,
    MutableMapping,
    Text,
    TextIO,
)

from google.cloud import exceptions
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import types
from google.cloud.speech_v1p1beta1.gapic import enums

# sample_word = {
#     'word': (word as Text),
#     'start_time': (time in seconds as float),
#     'end_time': (time in seconds as float),
# }  # type: Word
Word = MutableMapping[Text, Any]

__all__ = ['Word', 'audio_to_words', 'read_words']


def audio_to_words(gs_path: Text,
                   language_code='en-US',
                   credentials=None,
                   jsonl_dump_file=None,
                   ) -> Iterator[Word]:
    """
    :yields: Word objects with word timing information

    :arg gs_path: gs:// uri of audio file
    :param language_code: language code to try
    :param credentials: credentials to pass to SpeechClient and storage.Client
    :param jsonl_dump_file: .jsonl file to dump word timings to as Words
    """
    logger = logging.getLogger('audio_to_words')

    _, ext = os.path.splitext(urllib.parse.urlparse(gs_path).path)
    config = types.RecognitionConfig(
        encoding=_detect_audio_encoding(ext),
        language_code=language_code,
        model='video',
        profanity_filter=False,
        enable_word_time_offsets=True,
        enable_automatic_punctuation=True,
    )
    client = speech.SpeechClient(credentials=credentials)

    logger.info(f'Starting transcription of {gs_path} '
                f'using language {language_code}.')
    operation = client.long_running_recognize(
        config, types.RecognitionAudio(uri=gs_path))

    # Google doesn't implement a bunch of stuff on the specific audio long
    # running operation, but the operation api supports all of this. When
    # they implement it, all this /may/ just work, only needing a new msg.

    def poll_operation():
        while not operation.done():
            logger.info('Still running...')
            # TODO: Re-enable when progress_report actually works.
            # logger.info('{operation.metadata.progress_percent}% Complete.')
            time.sleep(5)

    try:
        poll_operation()
    except KeyboardInterrupt:
        logger.warning('Caught interrupt. Requesting cancellation.')
        try:
            operation.cancel()
            if not operation.cancelled():
                logger.warning('Operation not cancelled.')
        except exceptions.MethodNotImplemented as err:
            logger.error(
                'Cancellation not yet fully implemented by long running API.',
                err)
        logger.warning(
            'Waiting for results...  Send interrupt a second time to kill the '
            'program and destroy the temporary storage bucket. ***Whether this '
            'destruction cancels the long running recognition job is untested.***')
        logger.warning(
            "It is recommended to wait if you care about the results.")
    poll_operation()  # once more, (if there was a first attempt at cancellation
    # the job might not be done, but we want to avoid putting it above since an
    # unexpected error will say it's "while handling KeyboardInterrupt" and
    # that's a confusing error message.

    response = operation.result()  # this blocks, waiting for the result from G
    logger.info('Recognition complete.')
    if not response.results:
        raise RuntimeError(
            f'Got no results for file using language {language_code}')
    logger.debug('Yielding word timings from results...')

    words = _results_to_words(response.results)  # type: Iterator[Word]

    if jsonl_dump_file:
        words = _dump_words(words, jsonl_dump_file)  # type: Iterator[Word]

    return words


def _detect_audio_encoding(ext):
    """
    guesses a Google speech.enums.RecognitionConfig.AudioEncoding from a file
    extension.

    :param ext: file extension as str with the leading '.' (eg. '.flac')
    :returns: enum from speech.enums.RecognitionConfig.AudioEncoding
    """
    # TODO: add a proper library to do this and maybe convert from more formats.
    #  One necessarily exists.
    #  Justification: uploading files that aren't audio will still cost money
    #   so it makes sense to check before upload if a file is valid audio.
    if ext == '.flac':
        encoding = enums.RecognitionConfig.AudioEncoding.FLAC
    elif ext == '.opus':
        encoding = enums.RecognitionConfig.AudioEncoding.OGG_OPUS
    else:
        logger = logging.getLogger('detect_audio_encoding')
        logger.warning(
            f'Cannot detect audio encoding from extension "{ext}".')
        encoding = enums.RecognitionConfig.AudioEncoding.ENCODING_UNSPECIFIED
    return encoding


def _results_to_words(results: Iterable) -> Iterator[Word]:
    """
    :yields: a srt_utils.Word for every result in the input Iterable.
    :param results: results from google, (eg. from operation.result().results)
    """
    for result in results:
        if not result.alternatives:
            continue

        alternative = result.alternatives[0]

        if not alternative.words:
            continue

        for word in alternative.words:
            yield {
                'word': word.word,
                'start_time': float(word.start_time.seconds) +
                              word.start_time.nanos / 1000000000,
                'end_time': float(word.end_time.seconds) +
                            word.end_time.nanos / 1000000000,
            }  # type: Word


def read_words(json_file: TextIO) -> Iterator[Word]:
    """
    :yields: Words from a .jsonl file
    :arg json_file: a .jsonl file object in text mode
    """
    for line in json_file:
        yield json.loads(line.strip())


def _dump_words(words: Iterable[Word], json_file: TextIO,
                ) -> Iterator[Word]:
    """
    Dumps Words to .jsonl while passing them straight through.

    :yields: Word objects (dicts in the correct format)
    :arg words: Iterable[Word]
    :arg json_file: a .jsonl file object in text mode
    """
    for word in words:
        json_file.write(json.dumps(word) + '\n')
        yield word
