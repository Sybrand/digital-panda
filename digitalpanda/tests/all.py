import unittest
import ConfigParser
import logging
from swifttest import SwiftApi

if __name__ == '__main__':
	config = ConfigParser.RawConfigParser()
	config.read('test.cfg')
	log_level = getattr(logging, config.get('Logging', 'log_level').upper())

	logging.basicConfig(level=log_level)
	unittest.main()
