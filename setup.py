import os

import setuptools

THIS_DIR = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(THIS_DIR, 'README.md')) as readme:
    long_description = readme.read()

setuptools.setup(
    name='substream',
    version='0.1.1',
    description='Transcribes audio files to .srt',
    long_description=long_description,
    long_description_content_type='text/markdown',
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
    install_requires=[  # todo: tune as low as will go
        'google-api-python-client>=1.7.9',
        'google-cloud-core>=1.0.1',
        'google-cloud-speech>=1.0.0',
        'google-cloud-storage>=1.16.0',
        'grpcio>=1.21.1',
    ],
    packages=['substream', 'substream.tempbucket'],
    entry_points={
        'console_scripts': ['substream=substream.main:cli_main']
    },
    author='Michael de Gans',
    project_urls={
        'Bug Reports': 'https://github.com/mdegans/substream/issues',
        'Source': 'https://github.com/mdegans/substream/',
    },
)
