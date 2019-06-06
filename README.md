# Substream #

Transcribes an audio file to .srt subtitle format using word timings from
Google's Speech-to-Text API.

## Requirements: ##

* A Google account, [signed up for cloud](https://cloud.google.com/).

## Installing: ##

```shell
pip install substream
```

Cloud setup:

* [Create a *new* service account](https://cloud.google.com/iam/docs/creating-managing-service-accounts)
    for a ***new*** project dedicated to your recognition job. It must have the 
    following permissions:
    
    * _Cloud Speech Service Agent_
    * _Storage Admin_ OR
    * _Storage Object Viewer_ if supplying a `gs://` URI to the script.
 
    You can set the location to the .json credentials file you downloaded in the
    current environment like:
    
    ```shell
    export GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloud_credentials.json
    ```
    
    __(OR)__ you can set it just before the substream command like:
    
    ```shell
    GOOGLE_APPLICATION_CREDENTIALS=/path/to/cloud_credentials.json substream ...
    ```
    
    On run, a temporary bucket will be created, the file uploaded, and
    on completion or error, a [context manager](https://github.com/mdegans/substream/blob/master/substream/tempbucket/__init__.py)
    ensures bucket deletion.
    
    Please be careful with these credentials as cloud resources can be expensive,
    so make to store them securely if you do store them at all, and make sure all
    project buckets are deleted manually _even if the app reports they have been
    successfully deleted_.

Full Usage:
```shell
usage: substream [-h] -i INPUT -o SRT_FILENAME [--language CODE] [-v]

Transcribes an audio file or .jsonl dump to .srt using the Google Cloud
Speech-to-Text API

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        mono audio file (flac, opus, 16 bit pcm) (or) gs://
                        uri to audio file (or) intermediate .jsonl dump
                        (default: None)
  -o SRT_FILENAME, --output SRT_FILENAME
                        .srt filename (default: None)
  --language CODE       https://cloud.google.com/speech-to-text/docs/languages
                        (default: en-US)
  -v, --verbose         extra logging (default: False)
```

Sample Usage with a local file:
```shell
substream -v -i test.flac -o test.srt --language en-US
```

Sample usage with a URI:
```shell
substream -v -i gs://my-bucket/test.flac -o test.srt
```

## Uninstalling: ##
```shell
pip uninstall substream
```

## FAQ ##
* __Why the long-running API rather than the streaming API?__
    
    The long running API is more accurate.

* __What is the .jsonl file?__

    Each stripped line in the file is a string containing a json representation
    of a word with it's start and end timings. Later versions of this program
    may accept the .jsonl file to format the sentences in a better way without
    having to re-run the audio transcription.

* __Known Issues:__

    * 'walls of text' caused by people speaking without interruption. Some 
    subtitles may have to be manually split using a .srt editor.
    
    * Speaker identification is currently broken in the long running 
    api for long files, so splitting on this is curently disabled.
    (this exacerbates the above point)

    * Progress report is unimplemented by the long running API currently.
