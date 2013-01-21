from abc import ABCMeta, abstractmethod


class BucketFile(object):
    """
    This class defines the contract for a file, that is used across
    all buckets

    """
    def __init__(self, path, name, folder, contentType=None):
        self._path = path
        self._name = name
        self._folder = folder
        self._contentType = contentType

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def isFolder(self):
        return self._folder

    @property
    def contentType(self):
        return self._contentType


class AbstractBucket:
    """
    This class defines a contract for all our different storage sources
    e.g: Amazon S3, Local Files, Openstack Swift etc. etc.
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def delete_object(self, path):
        return NotImplemented

    @abstractmethod
    def list_dir(self, path):
        return NotImplemented

    @abstractmethod
    def authenticate(self):
        """
        Return True is it works, False if it fails
        """
        return False
