from urlparse import urlparse
import unittest
from bucket import swift
#import logging


class SwiftApi(unittest.TestCase):
    """
    TODO: write many more tests
    """

    """ this is a system test - it is NOT a unit test!
    def test_authenticate(self):

        we assume that if an auth token is available after
        authentication - everything went ok

        this is a system test - it is NOT a unit test


        config = ConfigParser.RawConfigParser()
        config.read('test.cfg')
        auth_url = config.get('Swift', 'swift_auth_url')
        username = config.get('Swift', 'swift_username')
        password = config.get('Swift', 'swift_password')

        api = swift.SwiftAPI(auth_url, username, password)
        api.authenticate()
        self.assertIsNotNone(api.get_auth_token())
        """

    def test_split_path_container_1(self):
        provider = swift.SwiftBucket(None)
        container, name = provider._split_path('Home')
        self.assertEqual('Home', container)
        self.assertIsNone(name)

    def test_split_path_container_2(self):
        provider = swift.SwiftBucket(None)
        container, name = provider._split_path('/Home')
        self.assertEqual('Home', container)
        self.assertIsNone(name)

    def test_split_path_container_3(self):
        provider = swift.SwiftBucket(None)
        container, name = provider._split_path('Home/')
        self.assertEqual('Home', container)
        self.assertIsNone(name)

    def test_split_path_container_4(self):
        provider = swift.SwiftBucket(None)
        container, name = provider._split_path('/Home/')
        self.assertEqual('Home', container)
        self.assertIsNone(name)

    def test_split_path_container_path(self):
        provider = swift.SwiftBucket(None)
        container, name = provider._split_path('Home/Android')
        self.assertEqual('Home', container)
        self.assertEqual('Android', name)

    def test_prepare_object_path_1(self):
        provider = swift.SwiftAPI('http://url', None, None)
        provider._storage_url = urlparse('http://url')
        fullPath = provider._prepare_object_path('/Home/', None)
        self.assertEqual('/Home', fullPath)

if __name__ == '__main__':
    unittest.main()
