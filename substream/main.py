import logging
import os
import time

from substream.speech_utils import audio_to_words
from substream.srt_utils import (
    records_to_srt, jsonl_to_srt
)
from substream.tempbucket import TemporaryBucket

__all__ = ['main', 'cli_main']


def main(filename_or_gs_path: str, srt_filename,
         language_code='en-US') -> None:
    """
    Substream python main

    :param filename_or_gs_path: filename or gs:// uri
    :param srt_filename: filename to write out to (should end with .srt)
    :param language_code: https://cloud.google.com/speech-to-text/docs/languages
    """
    logger = logging.getLogger('substream.main')

    def backup_if_exists(filename):
        if os.path.isfile(filename):
            timestamp = int(time.time())
            os.rename(filename, f'{filename}.{timestamp}.bak')

    backup_if_exists(srt_filename)

    val_err = False  # switch this to true if there is a value error inside
    # the context, so it can be raised outside (after managers __exit__s).
    with open(srt_filename, 'w') as srt_file:
        if filename_or_gs_path.startswith('gs://'):
            json_filename = srt_filename + '.jsonl'
            backup_if_exists(json_filename)
            with open(json_filename, 'w') as json_file:
                records_to_srt(
                    audio_to_words(
                        filename_or_gs_path,
                        language_code=language_code,
                        jsonl_dump_file=json_file),
                    srt_file)
        elif os.path.isfile(filename_or_gs_path):
            if filename_or_gs_path.endswith('.jsonl'):
                with open(filename_or_gs_path) as json_file:
                    logger.info(
                        f'Converting {json_file.name} to {srt_file.name}')
                    jsonl_to_srt(json_file, srt_file)
            else:
                # Trying audio file. Open json for writing, create a temporary
                # bucket, upload the audio, and start transcription to .srt
                json_filename = srt_filename + '.jsonl'
                backup_if_exists(json_filename)
                with open(json_filename, 'w') as json_file, \
                        TemporaryBucket() as bucket:
                    basename = os.path.basename(filename_or_gs_path)
                    logger.info(f'creating blob with name {basename}')
                    blob = bucket.blob(basename)
                    logger.info(f'Uploading {filename_or_gs_path}')
                    blob.upload_from_filename(filename_or_gs_path)

                    gs_path = f'gs://{blob.bucket.name}/{blob.name}'
                    records_to_srt(
                        audio_to_words(
                            gs_path,
                            language_code=language_code,
                            jsonl_dump_file=json_file),
                        srt_file)
        else:
            val_err = True

    if val_err:
        os.remove(srt_filename)
        raise ValueError(
            f'{filename_or_gs_path} not a file or valid gs:// uri.')


def cli_main():
    import argparse
    import substream

    ap = argparse.ArgumentParser(
        description='Transcribes an audio file or .jsonl dump to .srt using the '
                    'Google Cloud Speech-to-Text API',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    ap.add_argument(
        '-i', '--input',
        help='mono audio file (flac, opus, 16 bit pcm) (or) gs:// uri to audio '
             'file (or) intermediate .jsonl dump',
        required=True)
    ap.add_argument(
        '-o', '--output',
        help='.srt filename',
        dest='srt_filename',
        required=True)
    ap.add_argument(
        '--language',
        help='https://cloud.google.com/speech-to-text/docs/languages',
        default='en-US',
        dest='code')
    ap.add_argument(
        '-v', '--verbose',
        help='extra logging',
        action='store_true')

    args = ap.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    substream.main(
        args.input, args.srt_filename,
        language_code=args.code,
    )
