import unittest
from ..bucket import swift

class SwiftApi(unittest.TestCase):

	def test_authenticate(self):
		"""
		we assume that if an auth token is available after
		authentication - everything went ok

		"""
		auth_url = ""
		username = ""
		password = ""

		api = swift.SwiftAPI(auth_url, username, password)
		api.authenticate()
		self.assertIsNotNone(swift.get_auth_token())