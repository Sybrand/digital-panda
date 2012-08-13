from abc import ABCMeta, abstractmethod

class BucketFile(object):
    """
    This class defines the contract for a file, that is used across
    all buckts

    """
    def __init__(self, path, name):
        self._path = path
        self._name = name

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name

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
    def list_current_dir(self):
        return NotImplemented

    @abstractmethod
    def get_current_dir(self):
        return NotImplemented