import setuptools

from substream import __version__

setuptools.setup(
    name='substream',
    version=__version__,
    description='Transcribes audio files to .srt',
    long_description='Uses Google Cloud Speech to Text API to transcribe '
                     'audio files to the .srt format subtitles.',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',

        'Topic :: Multimedia :: Sound/Audio :: Speech',
        'Topic :: Multimedia :: Sound/Audio :: Analysis',
        'Topic :: Text Processing :: Linguistic',
        'Topic :: Software Development :: Internationalization',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    python_requires='>=3.6',
    install_requires=[
        'google-api-python-client',
        'google-cloud-speech',
        'google-cloud-storage',
    ],
    packages=['substream', 'substream.tempbucket'],
    entry_points={
        'console_scripts': ['substream=substream.main:cli_main']
    },
    author='Michael de Gans',
    project_urls={
        'Bug Reports': 'https://github.com/mdegans/substream/issues',
        'Say Thanks!': 'By complaining loudly on Twitter at lazy companies who'
                       "didn't subtitle your media in the first place.",
        'Source': 'https://github.com/mdegans/substream/',
    },
)
