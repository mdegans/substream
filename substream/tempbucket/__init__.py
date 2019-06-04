import contextlib
import logging
import uuid

import six
from google.cloud import storage, exceptions

name = 'substream.tempbucket'


class TemporaryBucket(contextlib.AbstractContextManager):
    """Functions much like tempfile.TemporaryDirectory() context manager, only
    it returns a google.storage.Bucket instead of a directory name."""

    logger = logging.getLogger(__name__ + ':TemporaryBucket')
    bucket = None

    def __init__(self, credentials=None):
        self.credentials = credentials

    def __enter__(self):
        self.logger.debug('__enter__')

        storage_client = storage.Client(credentials=self.credentials)
        del self.credentials

        def random_bucket():
            uuid_str = str(uuid.uuid4())
            self.logger.info(f'Creating temporary bucket with name {uuid_str}')
            return storage_client.create_bucket(uuid_str)

        try:
            self.bucket = random_bucket()
        except exceptions.Conflict as err:
            # bucket already exists
            self.logger.error(
                f'Bucket possibly already exists. See above error. Retrying...',
                err)
            self.bucket = random_bucket()
            # just try twice. Otherwise something is broken.

        self.logger.debug(f'Setting storage class to COLDLINE')
        self.bucket.storage_class = 'COLDLINE'

        return self.bucket

    def __exit__(self, *err):
        self.logger.debug('__exit__')
        self.logger.debug(f'Deleting bucket {self.bucket.name}')
        self.bucket.delete(force=True)
        if err[0] is not None:
            logging.error(
                'TemporaryBucket context manager cleaned up after errors. '
                'Re-raising now...')
            six.reraise(*err)
