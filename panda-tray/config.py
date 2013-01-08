import os
import os.path
import ConfigParser


class Config(object):
    def __init__(self):
        appDataFolder = os.environ['APPDATA']
        appConfigFolder = os.path.join(appDataFolder, 'digitalpanda')
        self.configFilePath = os.path.join(appConfigFolder, 'settings.json')

        if not os.path.isdir(appConfigFolder):
            os.mkdir(appConfigFolder)

    def get_username(self):
        #config = ConfigParser.RawConfigParser()
        #config.read(self.configFilePath)
        #return config.get('auth', 'username')
        return ''

    def set_username(self):
        pass

    def get_password(self):
        pass

    def set_password(self):
        pass

    def get_authUrl(self):
        pass

    def set_authUrl(self):
        pass
