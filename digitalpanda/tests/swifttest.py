import unittest
from ..bucket import swift
import ConfigParser
import logging

class SwiftApi(unittest.TestCase):

	def test_authenticate(self):
		"""
		we assume that if an auth token is available after
		authentication - everything went ok

		this is a system test - it is NOT a unit test

		"""

		config = ConfigParser.RawConfigParser()
		config.read('test.cfg')
		auth_url = config.get('Swift', 'swift_auth_url')
		username = config.get('Swift', 'swift_username')
		password = config.get('Swift', 'swift_password')

		api = swift.SwiftAPI(auth_url, username, password)
		api.authenticate()
		self.assertIsNotNone(api.get_auth_token())