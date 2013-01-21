import os
import os.path
import ConfigParser


AUTH_SECTION = 'auth'
USERNAME = 'username'
PASSWORD = 'password'
URL = 'url'


class Config(object):
    def __init__(self):
        appDataFolder = os.environ['APPDATA']
        appConfigFolder = os.path.join(appDataFolder, 'digitalpanda')
        self.configFilePath = os.path.join(appConfigFolder, 'settings')
        print('config file is %r' % self.configFilePath)
        if not os.path.isdir(appConfigFolder):
            print('creating config dir')
            os.mkdir(appConfigFolder)

    def get_key(self, section, key):
        config = ConfigParser.RawConfigParser()
        config.read(self.configFilePath)
        try:
            return config.get(section, key)
        except:
            return ''

    def set_key(self, section, key, value):
        config = ConfigParser.RawConfigParser()
        config.read(self.configFilePath)
        if not section in config.sections():
            config.add_section(section)
        config.set(section, key, value)
        with open(self.configFilePath, 'wb') as configFile:
            config.write(configFile)

    def get_username(self):
        return self.get_key(AUTH_SECTION, USERNAME)

    def set_username(self, username):
        print('set username to %r' % username)
        self.set_key(AUTH_SECTION, USERNAME, username)

    def get_password(self):
        # TODO: need to figure out how we're going to do encryption here
        return self.get_key(AUTH_SECTION, PASSWORD)

    def set_password(self, password):
        print('set password to %r' % password)
        self.set_key(AUTH_SECTION, PASSWORD, password)

    def get_authUrl(self):
        return self.get_key(AUTH_SECTION, URL)

    def set_authUrl(self, url):
        print('set url to %r' % url)
        return self.set_key(AUTH_SECTION, URL, url)

    def get_home_folder(self):
        return os.path.join(os.environ['USERPROFILE'], 'Digital Panda')
