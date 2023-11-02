from storages.backends.s3boto import S3BotoStorage
from django.db import models


def MediaS3BotoStorageTest(): return S3BotoStorage(location='test/media')


def MediaS3BotoStorageDemo(): return S3BotoStorage(location='demo/media')


def MediaS3BotoStorageRelease(): return S3BotoStorage(location='release/media')


def MediaS3BotoStorage(): return S3BotoStorage(location='production/media')


class S3PrivateFileField(models.FileField):
    def __init__(self, verbose_name=None, name=None, upload_to='', storage=None, **kwargs):
        super(S3PrivateFileField, self).__init__(verbose_name=verbose_name, name=name, upload_to=upload_to, storage=storage, **kwargs)
        self.storage.default_acl = "private"
