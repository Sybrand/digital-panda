from abc import ABCMeta

class AbstractBucket:
    __metaclass__ = ABCMeta

    @abstractmethod
    def delete_object(path):
        return NotImplemented