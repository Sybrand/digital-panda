from abc import ABCMeta, abstractmethod


class ProgressMessage(object):
    def __init__(self, path, bytes_per_second, bytes_read, bytes_expected):
        self._path = path
        self._bytes_per_second = bytes_per_second
        self._bytes_read = bytes_read
        self._bytes_expected = bytes_expected

    @property
    def path(self):
        return self._path

    @property
    def bytes_per_second(self):
        return self._bytes_per_second

    @property
    def bytes_read(self):
        return self._bytes_read

    @property
    def bytes_expected(self):
        return self._bytes_expected


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
        self._hash = None
        self._dateModified = None

    def get_hash(self):
        return self._hash

    def set_hash(self, value):
        self._hash = value

    def get_dateModified(self):
        return self._dateModified

    def set_dateModified(self, value):
        self._dateModified = value

    def get_content_type(self):
        return self._contentType

    def set_content_type(self, value):
        self._contentType = value

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

    @property
    def isFolder(self):
        return self._folder

    contentType = property(get_content_type, set_content_type)

    hash = property(get_hash, set_hash)

    dateModified = property(get_dateModified, set_dateModified)


class AbstractProvider:
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

    @abstractmethod
    def download_object(self, sourcePath, targetPath):
        """
        Download source to target
        """
        return NotImplemented
