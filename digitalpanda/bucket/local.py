from abstract import AbstractBucket 
import os

class LocalFile(object):
    def __init__(self, path, name):
        self._path = path
        self._name = name

    @property
    def path(self):
        return self._path

    @property
    def name(self):
        return self._name
        

class LocalBucket(AbstractBucket):
    def __init__(self):
        """
        """

    def delete_object(self, path):
        raise NotImplemented

    def list_current_dir(self):
        entries = os.listdir(os.getcwd())
        entries.sort()
        # first entry is one dir down (e.g. ..)
        files = [LocalFile(path=os.path.dirname(os.getcwd()), name='..')]
        # list directories first
        for entry in entries:
            if os.path.isdir(entry):
                files.append(LocalFile(os.path.abspath(entry), entry))
        # list files next
        for entry in entries:
            if not os.path.isdir(entry):
                files.append(LocalFile(os.path.abspath(entry), entry))
        
        return files

