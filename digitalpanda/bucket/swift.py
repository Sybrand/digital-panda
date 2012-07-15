from urlparse import urlparse
import json
import urllib
import logging
import httplib
from ..digitalpanda import Config
from abstract import AbstractBucket


class SwiftBucket(AbstractBucket):
    def __init__(self):
        """ this class pulls swift into a common interface - as defined in AbstractBucket

        """
        config = Config().config;
        self._swift = SwiftAPI(auth_url = config.get('Swift', 'swift_auth_url'),
            username = config.get('Swift', 'swift_username'),
            password = config.get('Swift', 'swift_password'))
        try:
            self._swift.authenticate()
        except:
            # TODO: feed this error to the user - nicely
            logging.error('could not authenticate!')
        # use / convention to indicate root
        # in swift context - we will take this to mean that 
        # no container has yet been selected
        self._current_path = '/';

    def delete_object(self, path):
        raise NotImplemented

    def list_current_dir(self):
        # default to empty array
        files = []
        if self._current_path == '/':
            # at our "root" - we list containers
            containers = self._swift.get_containers()
            if containers:
                for container in containers:
                    files.append(container, container)
        else:
            # if not at "root" - we list everything in the current "directory"
            raise NotImplemented

        return files


class SwiftAPI(object):
    """ class that wraps OpenStack Swift REST API 
    as specfied @ http://docs.openstack.org/api/openstack-object-storage/1.0/content/

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
        logging.debug('host = %r' % host)
        if (url.scheme=='https'):
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

        if result.status==200:
            self._auth_token = result.getheader('X-Auth-Token')
            self._storage_url = urlparse(result.getheader('X-Storage-Url'))
        else:
            raise Exception('login failed ; status = %r' % result.status)

    def get_auth_token(self):
        return self._auth_token

    def put_container(self, container, retry_on_unauthorized = True):
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

    def get_containers(self, retry_on_unauthorized = True):
        """ return a list of containers

        """
        
        path = "%s?format=json" % (self._storage_url.path)
        connection = self._open_connection(self._storage_url)
        connection.request('GET', path, None, self._create_headers())
        result = connection.getresponse()
        logging.debug('get containers returned %r' % result.status)

        containers = None
        if result.status == 200:            
            containers = json.loads(result.read())
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_containers(False)
        else:
            raise Exception('failed get catalogue; status = - %r' % (result.status))

    def get_container_meta_data(self, container, retry_on_unauthorized):
        """ return container meta data
        
        """
        path = "%s/%s" % (self._storage_url.path, urllib.quote(container))
        connection = self._open_connection(self._storage_url)
        connection.request('HEAD', path, None, headers)
        result = connection.getresponse()
        response = None

        if result.status == 204 or result.status == 200:
            response = result.getheaders()
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_container_meta_data(container, False)
        else:
            raise Exception('failed to get container meta data; status = %r' % (result.status))

    def get_object_meta_data(self, container, name, retry_on_unauthorized = True):
        """ return object meta data

        """
        path = self._prepare_object_path(container, name)
        connection = self._open_connection(self._storage_url)
        connection.request('HEAD', path, None, headers)
        result = connection.getresponse()
        response = None

        if result.status == 204 or result.status == 200:
            response = result.getheaders()
        elif result.status == 401 and retry_on_unauthorized:
            return self.get_object_meta_data(container, name, False)
        else:
            raise Exception('failed to get container meta data; status = %r' % (result.status))



    def delete_object(self, container, name, retry_on_unauthorized = True):
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

    def _escape_string(self, value):
        """ input string is escaped and returned in format
        acceptable to swift

        """
        value = urllib.quote(value)
        return value.replace('/', '%2F')

    def _create_headers(self):
        """ all swift request (subsequent to authentication)
        require an authentication token

        """
        return {'X-Auth-Token' : self._auth_token}

    def _prepare_object_path(self, container, name):
        """ format an object name correctly for swift

        """
        return "%s/%s/%s" % (self._storage_url.path, 
            urllib.quote(container),
            self._escape_string(name))