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


ENCODING = 'utf8'


# BUCKET? really? that's a bad name
class SwiftBucket(abstract.AbstractBucket):
    def __init__(self, auth_url, username, password):
        """ this class pulls swift into a common interface
        as defined in AbstractBucket

        """
        #config = Config().config
        self._swift = SwiftAPI(auth_url=auth_url,
                               username=username,
                               password=password)

        # use / convention to indicate root
        # in swift context - we will take this to mean that
        # no container has yet been selected
        self._current_path = None
        self.lock = threading.Lock()

    def delete_object(self, path):
        try:
            if self.lock.acquire(True):
                container, name = self._split_path(path)
                self._swift.delete_object(container, name)
        finally:
            self.lock.release()

    def list_dir(self, path):
        #logging.debug('list_dir(path = %s)' % path)
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
        folderType = 'application/directory'
        return swiftObject['content_type'] == folderType

    """
    def get_current_dir(self):
        storageUrl = self._swift.get_storage_url()
        return '%s://%s%s%s' % (storageUrl.scheme,
                                storageUrl.netloc,
                                storageUrl.path,
                                self._current_path)"""

    def download_object(self, sourcePath, targetPath):
        try:
            if self.lock.acquire(True):
                # create a temporary path (we only move the file to the
                # targetPath, once it's been completely downloaded)
                logging.info('going to download %s to %s' %
                             (sourcePath, targetPath))
                container, name = self._split_path(sourcePath)
                logging.info('container=%s;name=%s' % (container, name))
                self._swift.get_object(container, name, targetPath)
            else:
                raise Exception('unable to lock')
        finally:
            self.lock.release()

    def upload_object(self, sourcePath, targetPath):
        try:
            if self.lock.acquire(True):
                logging.info('going to upload %s to %s' %
                             (sourcePath, targetPath))
                container, name = self._split_path(targetPath)
                self._swift.put_object(container, name, sourcePath)
            else:
                raise Exception('unable to lock')
        finally:
            self.lock.release()

    def authenticate(self):
        try:
            if self.lock.acquire(True):
                self._swift.authenticate()
                self._current_path = '/'
                return True
            else:
                return False
        except:
            return False
        finally:
            self.lock.release()

    def get_file_info(self, path):
        try:
            if self.lock.acquire(True):
                container, name = self._split_path(path)
                metaData = self._swift.get_object_meta_data(container, name)
                fileInfo = None
                if metaData:
                    fileInfo = abstract.BucketFile(path, name, None)
                    for data in metaData:
                        key = data[0].lower()
                        if key == 'etag':
                            fileInfo.hash = data[1]
                        elif key == 'last-modified':
                            fileInfo.dateModified = data[1]
                        elif key == 'content-type':
                            fileInfo.contentType = data[1]
                        #else:
                        #    logging.debug('not handling %s' % key)
                return fileInfo
            else:
                raise Exception('failed to lock')
        finally:
            self.lock.release()

    def _split_path(self, path):
        end = path.find('/')
        container = path[0:end]
        name = path[end + 1:]
        return (container, name)


class SwiftAPI(object):
    """ class that wraps OpenStack Swift REST API
    as specfied @ http://docs.openstack.org/api/openstack-object-storage/
                         1.0/content/

    """
    def __init__(self, auth_url, username, password):
        """
        auth_url: string representing authentication url

        we need to remember authentication details,
        so that if we ever get a 401, we can retry

        """
        logging.debug('auth_url: %s ; username = %s'
                      % (auth_url, username))
        self._auth_url = urlparse(auth_url)
        logging.debug('self._auth_url = %s' % (self._auth_url.scheme))
        self._username = username
        self._password = password

    def _open_connection(self, url):
        """ return HTTPConnection/HTTPSConnection depending
        on protocol specified in authentication url

        """
        if url.port:
            host = "%s:%d" % (url.hostname, url.port)
        else:
            host = url.hostname
        #logging.debug('host = %r' % host)
        if (url.scheme == 'https'):
            return httplib.HTTPSConnection(host)
        else:
            return httplib.HTTPConnection(host)

    def authenticate(self):
        """ authenticate against swift, store X-Auth-Token and
        X-Storage-Url

        """
        headers = {'X-Storage-User': self._username,
                   'X-Storage-Pass': self._password}

        connection = self._open_connection(self._auth_url)
        connection.request('GET', self._auth_url.path, None, headers)
        result = connection.getresponse()

        if result.status == 200:
            self._auth_token = result.getheader('X-Auth-Token')
            self._storage_url = urlparse(result.getheader('X-Storage-Url'))
            print('storage token is %r' % self._auth_token)
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
        if pseudoFolder:
            pseudoFolder = pseudoFolder.strip('/')
            pseudoFolder = urllib.quote(pseudoFolder.encode(ENCODING))
            if delimiter:
                path = ('%s/%s?prefix=%s/&delimiter=%s'
                        '&format=json' %
                        (self._storage_url.path, container,
                        pseudoFolder, delimiter))

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
        else:
            raise Exception('failed to get object list %r' %
                            result.status)
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

    def delete_object(self, container, name,
                      retry_on_unauthorized=True):
        """ delete a swift object - given the container
        and object name


        """

        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('DELETE', path, None, self._create_headers())
        result = connection.getresponse()
        if result.status == 200 or result.status == 204:
            logging.info('deleted %s ok' % (path))
        elif result.status == 401 and retry_on_unauthorized:
            # it might be that our authtoken has expired
            # we authenticate, and try again
            self.authenticate()
            self.delete_object(container, name, False)
        else:
            raise Exception('failed to delete %s ; status = %r' %
                            (path, result.status))

    def put_object(self, container, name, localPath):
        connection = self._open_connection(self._storage_url)
        sourceFile = open(localPath, 'rb')
        fileNo = sourceFile.fileno()
        fileSize = os.path.getsize(localPath)
        path = self._prepare_object_path(container, name)
        if (fileSize > 0):
            # TODO: this has to change - we need to be able interrupt the
            # request
            mappedFile = mmap.mmap(fileNo, fileSize, access=mmap.ACCESS_READ)
            connection.request('PUT', path, mappedFile, self._create_headers())
        else:
            logging.debug("file is empty - so going to write an empty string")
            headers = self._create_headers()
            headers['Content-Length'] = 0
            connection.request('PUT', path, '', headers)
        result = connection.getresponse()
        if (mappedFile is not None):
            mappedFile.close()
        sourceFile.close()
        if (result.status != 201):
            raise Exception('failed to upload %r ; status = %r' %
                            (path, result.status))

    def get_object(self, container, name, targetPath):
        # we download to a temporary path
        tmpPath = os.path.join(tempfile.gettempdir(), '~tmp')
        if os.path.exists(tmpPath):
            os.remove(tmpPath)

        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('GET', path, None, self._create_headers())
        result = connection.getresponse()
        if result.status == 200:
            targetFile = open(tmpPath, 'wb')
            chunkSize = 524288
            data = result.read(chunkSize)
            targetFile.write(data)
            while (len(data) == chunkSize):
                data = result.read(chunkSize)
                targetFile.write(data)
            targetFile.flush()
            targetFile.close()
            # file download is complete - so we
            # replace it
            os.rename(tmpPath, targetPath)
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
        return {'X-Auth-Token': self._auth_token}

    def _prepare_object_path(self, container, name):
        """ format an object name correctly for swift

        """
        return "%s/%s/%s" % (self._storage_url.path,
                             urllib.quote(container),
                             self._escape_string(name))
