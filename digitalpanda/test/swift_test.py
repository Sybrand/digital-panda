import unittest
from digitalpanda import swift

class SwiftApi(unittest.TestCase):

	def test_authenticate(self):
		"""
		we assume that if an auth token is available after
		authentication - everything went ok

		"""
		auth_url = ""
		username = ""
		password = ""

		swift = digitalpanda.bucket.Swift(auth_url, username, password)
		swift.authenticate()
		self.assertIsNotNone(swift.get_auth_token())

if __name__ == '__main__':
	unittest.main()