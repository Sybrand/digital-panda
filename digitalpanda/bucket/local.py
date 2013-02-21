from abstract import AbstractProvider, BucketFile
import os
import hashlib
import datetime
#import logging


class LocalProvider(AbstractProvider):
    def __init__(self):
        """ this class pulls local file io into the contract defined in
        AbstractBucket
        """

    def delete_object(self, path):
        raise NotImplemented

    """
    def list_current_dir(self):
        entries = os.listdir(os.getcwd())
        entries.sort()
        # first entry is one dir down (e.g. ..)
        files = [BucketFile(path=os.path.dirname(os.getcwd()), name='..')]
        # list directories first
        for entry in entries:
            if os.path.isdir(entry):
                files.append(BucketFile(os.path.abspath(entry), entry))
        # list files next
        for entry in entries:
            if not os.path.isdir(entry):
                files.append(BucketFile(os.path.abspath(entry), entry))
        return files
    """

    def get_current_dir(self):
        return os.getcwd()

    def download_object(self, sourcePath, targetPath):
        raise NotImplemented

    def list_dir(self, path):
        raise NotImplemented

    def get_last_modified_date(self, path):
        """ Return a string representing the date and time in ISO 8601 format
        """
        mt = os.path.getmtime(path)
        dt = datetime.datetime.fromtimestamp(mt)
        return dt.isoformat()

    def get_file_info(self, path):
        # this is a computationally expensive call!
        #logging.info('calculating md5 hash for %s' % path)
        fileInfo = BucketFile(path, None, None)
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            while True:
                data = f.read(1048576)
                if not data:
                    break
                md5.update(data)
        fileInfo.hash = md5.hexdigest()
        return fileInfo

    def authenticate(self):
        raise NotImplemented
