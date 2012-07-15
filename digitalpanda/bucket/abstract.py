from abc import ABCMeta, abstractmethod

class AbstractBucket:
    """
    This class defines a contract for all our different storage sources
    """

    __metaclass__ = ABCMeta

    @abstractmethod
    def delete_object(self, path):
        return NotImplemented

    @abstractmethod
    def list_current_dir(self):
        return NotImplemented