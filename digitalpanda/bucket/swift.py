from urlparse import urlparse
import json
import urllib
import logging
import httplib
#from ..digitalpanda import Config
import abstract
import threading
import os
import tempfile
import mmap
import time
import hashlib
#import math
#from internet import Downloader


ENCODING = 'utf8'
FOLDER_TYPE = 'application/directory'
TRASH_CONTAINER = 'Trash'


class SwiftCredentials(object):
    def __init__(self, auth_url, username, password):
        self._auth_url = auth_url
        self._username = username
        self._password = password

    def _get_auth_url(self):
        return self._auth_url

    def _get_username(self):
        return self._username

    def _get_password(self):
        return self._password

    authUrl = property(_get_auth_url)
    username = property(_get_username)
    password = property(_get_password)


class SwiftProvider(abstract.AbstractProvider):
    def __init__(self, credentials, user_agent, output_queue):
        """ this class pulls swift into a common interface
        as defined in AbstractBucket

        """
        #config = Config().config
        if credentials:
            self._swift = SwiftAPI(auth_url=credentials.authUrl,
                                   username=credentials.username,
                                   password=credentials.password,
                                   user_agent=user_agent,
                                   output_queue=output_queue)

        # use / convention to indicate root
        # in swift context - we will take this to mean that
        # no container has yet been selected
        self._credentials = credentials

    def delete_object(self, path, moveToTrash=False):
        container, name = self._split_path(path)
        if moveToTrash:
            logging.info('before deleting %r - we move it to trash' %
                         path)
            if name:
                self._swift.copy_object(container,
                                        name,
                                        TRASH_CONTAINER,
                                        name)
            else:
                self._copy_container(container,
                                     TRASH_CONTAINER)
        self._swift.delete_object(container, name)

    def _copy_container(self, sourceContainer, targetContainer):
        # one can't actually copy a container - it's just not possible, but we
        # can create a directory with the same name
        logging.info('doing a fake container copy')
        targetPath = '%s/%s' % (targetContainer, sourceContainer)
        self.create_folder(targetPath)

    def list_dir(self, path):
        #logging.debug('list_dir(path = %r)' % path)
        # default to empty array
        files = []
        if path:
            # if not at "root" - we list everything in the current
            # get the container
            end = path.find('/')
            container = None
            pseudoFolder = None
            if end > 0:
                container = path[:end]
                pseudoFolder = path[end:]
            else:
                container = path
            # WE DON'T encode here - because we don't want to double encode
            # by accident!
            #encodedContainer = urllib.quote(container.encode(ENCODING))
            swift = self._swift
            objects = swift.get_container_objects(container,
                                                  delimiter='/',
                                                  pseudoFolder=pseudoFolder)
            if objects:
                for o in objects:
                    #print(o)
                    f = None
                    if 'subdir' in o:
                        remotePath = '%s/%s' % (container,
                                                o['subdir'])
                        fileName = o['subdir']
                        f = abstract.BucketFile(remotePath,
                                                fileName,
                                                True,
                                                'application/directory')
                    else:
                        remotePath = '%s/%s' % (container,
                                                o['name'])
                        fileName = o['name']
                        if '/' in fileName:
                            last = fileName.rfind('/')
                            if last > 0:
                                fileName = fileName[last:]
                        isFolder = self.is_folder(o)
                        f = abstract.BucketFile(remotePath,
                                                fileName,
                                                isFolder,
                                                o['content_type'])
                        if not isFolder:
                            f.hash = o['hash']
                            f.dateModified = o['last_modified']

                    files.append(f)

        else:
            # at our "root" - we list containers
            containers = self._swift.get_containers()
            if containers:
                for container in containers:
                    f = abstract.BucketFile(container['name'],
                                            container['name'],
                                            True)
                    files.append(f)
        return files

    def is_folder(self, swiftObject):
        return swiftObject['content_type'] == FOLDER_TYPE

    def create_folder(self, targetPath):
        container, name = self._split_path(targetPath)
        self._swift.put_empty_object(container, name, FOLDER_TYPE)

    def download_object(self, sourcePath, targetPath):
        # create a temporary path (we only move the file to the
        # targetPath, once it's been completely downloaded)
        #logging.info('going to download %s to %s' %
        #             (sourcePath, targetPath))
        container, name = self._split_path(sourcePath)
        #logging.info('container=%s;name=%s' % (container, name))
        self._swift.get_object(container, name, targetPath)

    def upload_object(self, sourcePath, targetPath, md5Hash=None,
                      moveToTrash=True):
        container, name = self._split_path(targetPath)
        #logging.info('looking to see if object already exists')
        # if the object already exists, we copy it to trash, before
        # overwriting it
        targetMetaData = self._swift.get_object_meta_data(container,
                                                          name)
        if targetMetaData:
            etag = self._get_header_by_key(targetMetaData, 'etag')
            logging.info('the file you want to write already exist')
            if etag[0] != md5Hash:
                # lets copy the old file to trash 1st
                if moveToTrash:
                    copyName = '%s/%s' % (container, name)
                    self._swift.copy_object(container,
                                            name,
                                            TRASH_CONTAINER,
                                            copyName)
            else:
                logging.warn(('trying to upload identical file?'
                              ' are you being silly?'))

        #logging.info('going to upload %s to %s' %
        #             (sourcePath, targetPath))
        headers = self._swift.put_object(container,
                                         name,
                                         sourcePath,
                                         md5Hash)
        fileInfo = None
        if headers:
            self._headers_to_fileInfo(headers, targetPath, name)
        return fileInfo

    def authenticate(self):
        self._swift.authenticate()
        return True

    def get_file_info(self, path):
        #logging.info('get file info for: %s' % path)
        container, name = self._split_path(path)
        metaData = self._swift.get_object_meta_data(container, name)
        fileInfo = None
        if metaData:
            fileInfo = self._headers_to_fileInfo(metaData, path, name)
        return fileInfo

    def _set_credentials(self, credentials):
        self._credentials = credentials
        logging.debug('credentials changed to:')
        logging.debug('username: %s' % credentials.username)
        logging.debug('password: %s' % credentials.password)
        logging.debug('authUrl: %s' % credentials.authUrl)
        self._swift.username = credentials.username
        self._swift.password = credentials.password
        self._swift.authUrl = credentials.authUrl

    def _get_credentials(self):
        return self._credentials

    def _split_path(self, path):
        path = path.strip('/')
        end = path.find('/')
        if end == -1:
            container = path[0:]
            name = None
        else:
            container = path[0:end]
            name = path[end + 1:]
        return (container, name)

    def _get_header_by_key(self, headers, key):
        key = key.lower()
        value = None
        for data in headers:
            tmp = data[0].lower()
            if key == tmp:
                value = data[1]
                break
        return value

    def _headers_to_fileInfo(self, headers, path, name):
        fileInfo = abstract.BucketFile(path, name, None)
        for data in headers:
            key = data[0].lower()
            if key == 'etag':
                fileInfo.hash = data[1]
            elif key == 'last-modified':
                fileInfo.dateModified = data[1]
            elif key == 'content-type':
                fileInfo.contentType = data[1]
        return fileInfo

    def stop(self):
        logging.info('SwiftProvider::stop')
        self._swift.stop()

    credentials = property(_get_credentials, _set_credentials)


class SwiftAPI(object):
    """ class that wraps OpenStack Swift REST API
    as specfied @ http://docs.openstack.org/api/openstack-object-storage/
                         1.0/content/

    """
    def __init__(self, auth_url, username, password, user_agent, output_queue):
        """
        auth_url: string representing authentication url

        we need to remember authentication details,
        so that if we ever get a 401, we can retry

        """
        self._auth_url = urlparse(auth_url)
        self._username = username
        self._password = password
        self._user_agent = user_agent
        self._lock = threading.Lock()
        self._isRunning = True
        self._mappedFile = None
        self._output_queue = output_queue

    def _open_connection(self, url):
        """ return HTTPConnection/HTTPSConnection depending
        on protocol specified in authentication url

        """
        if url.port:
            host = "%s:%d" % (url.hostname, url.port)
        else:
            host = url.hostname
        if (url.scheme == 'https'):
            return httplib.HTTPSConnection(host)
        else:
            return httplib.HTTPConnection(host)

    def authenticate(self):
        """ authenticate against swift, store X-Auth-Token and
        X-Storage-Url

        """
        headers = {'X-Storage-User': self._username,
                   'X-Storage-Pass': self._password,
                   'User-Agent': self._user_agent}

        connection = self._open_connection(self._auth_url)
        connection.request('GET', self._auth_url.path, None, headers)
        result = connection.getresponse()

        if result.status == 200:
            self._auth_token = result.getheader('X-Auth-Token')
            self._storage_url = urlparse(result.getheader('X-Storage-Url'))
        else:
            raise Exception('login failed ; status = %r' % result.status)

    def get_auth_token(self):
        return self._auth_token

    def get_storage_url(self):
        return self._storage_url

    def put_container(self, container, retry_on_unauthorized=True):
        """ create a swift container

        """

        path = "%s/%s" % (self._storage_url.path,
                          urllib.quote(container))
        connection = self._open_connection(self._storage_url)
        connection.request('PUT', path, None, self._create_headers())
        result = connection.getresponse()
        if (result.status == 201 or result.status == 202):
            logging.info('created %s ok' % (path))
        elif result.status == 401 and retry_on_unauthorized:
            self.authenticate()
            self.put_container(container, False)
        else:
            raise Exception('failed to put container %s ; status = %r' %
                            (container, result.status))

    def get_container_objects(self, container, pseudoFolder=None,
                              delimiter=None):
        """ return list of objects in pseudoFolder

        """
        #logging.debug('get_container_objects(container=%r, pseudoFolder=%r'
        #              ', delimiter=%r)' %
        #              (container, pseudoFolder, delimiter))
        container = urllib.quote(container.encode(ENCODING))
        if pseudoFolder:
            pseudoFolder = pseudoFolder.strip('/')
            pseudoFolder = urllib.quote(pseudoFolder.encode(ENCODING))
            if delimiter:
                path = ('%s/%s?prefix=%s/&delimiter=%s'
                        '&format=json' %
                        (self._storage_url.path, container,
                        pseudoFolder, delimiter))
                #logging.info('i have created %r' % path)

            else:
                path = '%s/%s?prefix=%s/' % (self._storage_url.path,
                                             container,
                                             pseudoFolder)
        else:
            if delimiter:
                path = ('%s/%s?delimiter=%s'
                        '&format=json' %
                        (self._storage_url.path, container,
                        delimiter))
            else:
                path = '%s/%s' % (self._storage_url.path,
                                  container)

        connection = self._open_connection(self._storage_url)
        connection.request('GET', path, None, self._create_headers())
        result = connection.getresponse()

        objects = None
        if result.status == 200:
            jsonString = result.read()
            if jsonString:
                objects = json.loads(jsonString)
        elif result.status == 404:
            logging.info('404 not found for %r' % path)
            pass
        else:
            raise Exception('failed to get object list - status = %r'
                            'for path = %r' %
                            (result.status, path))
        return objects

    def get_containers(self, retry_on_unauthorized=True):
        """ return a list of containers

        """

        path = "%s?format=json" % (self._storage_url.path)
        connection = self._open_connection(self._storage_url)
        connection.request('GET', path, None, self._create_headers())
        result = connection.getresponse()
        #logging.debug('get containers returned %r' % result.status)

        containers = None
        if result.status == 200:
            containers = json.loads(result.read())
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_containers(False)
        else:
            raise Exception('failed get catalogue; status = - %r' %
                            (result.status))
        return containers

    def get_container_meta_data(self, container, retry_on_unauthorized):
        """ return container meta data
        """
        path = "%s/%s" % (self._storage_url.path, urllib.quote(container))
        connection = self._open_connection(self._storage_url)
        connection.request('HEAD', path, None, self._create_headers())
        result = connection.getresponse()

        if result.status == 204 or result.status == 200:
            return result.getheaders()
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_container_meta_data(container, False)
        else:
            raise Exception('failed to get container meta data; status = %r' %
                            (result.status))

    def get_object_meta_data(self, container, name,
                             retry_on_unauthorized=True):
        """ return object meta data

        """
        #logging.debug('get object meta data for container = %r ; name = %r' %
        #              (container, name))
        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('HEAD', path, None, self._create_headers())
        result = connection.getresponse()
        response = None

        if result.status == 204 or result.status == 200:
            response = result.getheaders()
            return response
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_object_meta_data(container, name, False)
        elif result.status == 404:
            return None
        else:
            raise Exception('failed to get container meta data; status = %r' %
                            (result.status))

    def copy_object(self, containerFrom, nameFrom, containerTo, nameTo):
        logging.info('trying to copy %s/%s to %s/%s'
                     % (containerFrom, nameFrom, containerTo, nameTo))
        connection = self._open_connection(self._storage_url)
        # we want to copy to a container - but we need to know if that
        # container exists!
        path = "%s/%s" % (self._storage_url.path, urllib.quote(containerTo))
        connection.request('HEAD', path, None, self._create_headers())
        result = connection.getresponse()
        if result.status == 404:
            # we need to create the container!
            logging.info('creating container - %r' % containerTo)
            self.put_container(containerTo)
        elif result.status == 204 or result.status == 200:
            pass
        else:
            raise Exception('failed to get container meta data; status = %r' %
                            (result.status))
        # hold on - does the source object even exist?
        objectMeta = self.get_object_meta_data(containerFrom, nameFrom)
        if objectMeta:
            # ok - we have a container, and we're ready to go
            connection = self._open_connection(self._storage_url)
            fromPath = self._prepare_object_path(containerFrom, nameFrom)
            toPath = "/%s/%s" % (urllib.quote(containerTo),
                                 self._escape_string(nameTo))
            logging.info('Destination = %r' % (toPath))
            headers = self._create_headers()
            headers['Content-Length'] = 0
            headers['Destination'] = toPath
            connection.request('COPY', fromPath, None, headers)
            result = connection.getresponse()
            if result.status == 201:
                pass
            else:
                raise Exception('failed to copy from %r to %r with code %r'
                                %
                                (fromPath, toPath, result.status))
            logging.info('copy result: %r' % (result.status))
        else:
            logging.info('we can\'t move something, if it\'s not there')

    def delete_object(self, container, name,
                      retry_on_unauthorized=True):
        """ delete a swift object - given the container
        and object name
        """
        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('DELETE', path, None, self._create_headers())
        logging.info('DELETE: %r' % path)
        result = connection.getresponse()
        if result.status == 200 or result.status == 204:
            logging.info('deleted %s ok' % (path))
        elif result.status == 401 and retry_on_unauthorized:
            # it might be that our authtoken has expired
            # we authenticate, and try again
            self.authenticate()
            self.delete_object(container, name, False)
        elif result.status == 404:
            # couldn't find the file to delete - no worries!
            # you wanted it gone - it's gone!
            logging.info('could not find %s' % path)
        else:
            raise Exception('failed to delete %s ; status = %r' %
                            (path, result.status))

    def put_empty_object(self, container, name, content_type):
        #logging.debug('put_empty_object(%r, %r, %r)' %
        #              (container, name, content_type))
        connection = self._open_connection(self._storage_url)
        path = self._prepare_object_path(container, name)
        headers = self._create_headers()
        headers['Content-Length'] = 0
        headers['Content-Type'] = content_type
        connection.request('PUT', path, None, headers)
        result = connection.getresponse()
        if (result.status != 201):
            raise Exception('failed to put empty object upload %r ;'
                            ' status = %r' %
                            (path, result.status))

    def put_object(self, container, name, localPath, md5Hash=None):
        connection = self._open_connection(self._storage_url)
        sourceFile = open(localPath, 'rb')
        fileNo = sourceFile.fileno()
        fileSize = os.path.getsize(localPath)
        path = self._prepare_object_path(container, name)
        self._mappedFile = None
        if (fileSize > 0):
            # TODO: this has to change - we need to be able interrupt the
            # request
            self._lock.acquire()
            try:
                if self._isRunning:
                    self._mappedFile = mmap.mmap(fileNo,
                                                 fileSize,
                                                 access=mmap.ACCESS_READ)
            finally:
                self._lock.release()
            headers = self._create_headers()
            if md5Hash:
                headers['ETag'] = md5Hash
            # potentially NOT thread safe here!
            # if self._mappedFile is accessed while we
            # are setting up this object - things could go badly
            # wrong - it's a risk we take
            connection.request('PUT', path, self._mappedFile, headers)
        else:
            logging.debug("file is empty - so going to write an empty string")
            headers = self._create_headers()
            headers['Content-Length'] = 0
            connection.request('PUT', path, '', headers)
        result = connection.getresponse()
        self._lock.acquire()
        try:
            if self._mappedFile:
                self._mappedFile.close()
                self._mappedFile = None
        finally:
            self._lock.release()
        sourceFile.close()
        if (result.status != 201):
            raise Exception('failed to upload %r ; status = %r' %
                            (path, result.status))
        return result.getheaders()

    def get_object(self, container, name, targetPath):
        return self.get_object_url_lib(container, name, targetPath)

    """
    def get_object_twisting(self, container, name, targetPath):

        metaData = self.get_object_meta_data(container, name, True)
        for data in metaData:
            if data[0] == 'content-length':
                expectedBytes = int(data[1])
                break
        # we download to a temporary path
        tmpPath = os.path.join(tempfile.gettempdir(), '~tmp')
        if os.path.exists(tmpPath):
            os.remove(tmpPath)

        url = self._storage_url
        if url.port:
            host = "%s:%d" % (url.hostname, url.port)
        else:
            host = url.hostname
        path = '%s://%s%s' % (url.scheme,
                              host,
                              self._prepare_object_path(container, name))

        headers = {'X-Auth-Token': [self._auth_token],
                   'User-Agent': [self._user_agent]}
        self._lock.acquire()
        try:
            self._downloader = Downloader()
        finally:
            self._lock.release()
        self._downloader.download(path, tmpPath, headers)
        bytesWritten = self._downloader.getBytesWritten()
        self._lock.acquire()
        try:
            self._downloader = None
        finally:
            self._lock.release()
        if bytesWritten != expectedBytes:
            raise Exception('for %r, was expecting %r bytes, but only got %r' %
                            (path, expectedBytes, bytesWritten))
        os.rename(tmpPath, targetPath)
        """

    def _update_progress(self,
                         path,
                         bytesPerSecond,
                         totalBytesRead,
                         expectedBytes):
        self._output_queue.put(abstract.ProgressMessage(path,
                                                        bytesPerSecond,
                                                        totalBytesRead,
                                                        expectedBytes))

    def get_object_url_lib(self, container, name, targetPath):
        """
        get an object using the urllib import
        """
        # we download to a temporary path
        tmpPath = os.path.join(tempfile.gettempdir(), '~tmp')
        if os.path.exists(tmpPath):
            os.remove(tmpPath)

        metaData = self.get_object_meta_data(container, name, True)
        for data in metaData:
            #logging.info('key = %r' % data[0])
            if data[0] == 'content-length':
                expectedBytes = int(data[1])
            elif data[0] == 'etag':
                expectedHash = data[1]

        """logging.info('the expected hash for %s/%s is %r' %
                     (container, name, expectedHash))"""

        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('GET', path, None, self._create_headers())
        result = connection.getresponse()
        if result.status == 200:
            t = time.time()
            targetFile = open(tmpPath, 'wb')
            chunkSize = 1048576
            md5 = hashlib.md5()
            data = result.read(chunkSize)
            if len(data) > 0:
                targetFile.write(data)
                md5.update(data)
                totalBytesRead = len(data)
                delta = time.time() - t
                if delta > 0:
                    bytesPerSecond = totalBytesRead / delta
                    self._update_progress(path,
                                          bytesPerSecond,
                                          totalBytesRead,
                                          expectedBytes)
            #megaBytesPerSecond = math.floor(bytesPerSecond / 1024 / 1024)
            while (len(data) > 0) and self._isRunning:
                t = time.time()
                data = result.read(chunkSize)
                bytesRead = len(data)
                delta = time.time() - t
                if delta > 0:
                    bytesPerSecond = bytesRead / delta
                    self._update_progress(path,
                                          bytesPerSecond,
                                          totalBytesRead,
                                          expectedBytes)
                if bytesRead > 0:
                    targetFile.write(data)
                    md5.update(data)
                totalBytesRead += bytesRead
            targetFile.flush()
            targetFile.close()
            localHash = md5.hexdigest()

            """ some version of swift don't report expectedBytes correctly!
            as such - we can't use this as a test - we have to rather check
            the md5 hash
            if expectedBytes != totalBytesRead:
                raise Exception('was expecting %r bytes for %r'
                                ', but only read %r' %
                                (expectedBytes, path, totalBytesRead))"""
            # file download is complete - so we
            # replace it
            if localHash == expectedHash:
                os.rename(tmpPath, targetPath)
            else:
                raise Exception('expected hash tag %r, recieved hash tag %r' %
                                (expectedHash, localHash))
        else:
            raise Exception('failed to download %s/%s to %s ; status = %r' %
                            (container, name,
                             targetPath, result.status))

    def _escape_string(self, value):
        """ input string is escaped and returned in format
        acceptable to swift

        """
        value = urllib.quote(value.encode(ENCODING))
        return value.replace('/', '%2F')

    def _create_headers(self):
        """ all swift request (subsequent to authentication)
        require an authentication token
        """
        return {'X-Auth-Token': self._auth_token,
                'User-Agent': self._user_agent}

    def _prepare_object_path(self, container, name):
        """ format an object name correctly for swift

        """
        container = container.strip('/')
        if name:
            # Q: why: urllib.quote(container) ?
            # A: ????
            # Q: why not: self._escape_string(container)
            # A: ????
            return "%s/%s/%s" % (self._storage_url.path,
                                 urllib.quote(container),
                                 self._escape_string(name))
        else:
            return "%s/%s" % (self._storage_url.path,
                              urllib.quote(container))

    def _get_username(self):
        return self._username

    def _set_username(self, value):
        self._username = value

    def _get_password(self):
        return self._password

    def _set_password(self, value):
        self._password = value

    def _get_auth_url(self):
        return self._auth_url

    def _set_auth_url(self, value):
        self._auth_url = urlparse(value)

    def stop(self):
        logging.info('SwiftAPI::stop()')
        self._lock.acquire()
        self._isRunning = False
        try:
            if self._mappedFile:
                self._mappedFile.close()
                self._mappedFile = None
        finally:
            self._lock.release()

    username = property(_get_username, _set_username)
    password = property(_get_password, _set_password)
    authUrl = property(_get_auth_url, _set_auth_url)
