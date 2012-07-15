import ConfigParser

class Config(object):
	"""
	This class is the configuration authority

	"""
	def __init__(self):
		self._config = ConfigParser.RawConfigParser()
		self._config.read('digital_panda.cfg')

	@property
	def config(self):
		return self._config
