import os
import os.path
import ConfigParser
import version
#import logging


AUTH_SECTION = 'auth'
ADVANCED_SECTION = 'advanced'
USERNAME = 'username'
PASSWORD = 'password'
URL = 'url'
STORAGE_PROVIDER = 'storage_provider'
UPGRADE_URL = 'www.digitalpanda.co.za'
"""BRANCH_STABLE = 'stable'
BRANCH_DEV = 'dev'
BRANCH_TEST = 'test'"""


class Config(object):
    def __init__(self):
        appDataFolder = os.environ['APPDATA']
        self.configFolder = os.path.join(appDataFolder, 'Digital Panda')
        self.configFilePath = os.path.join(self.configFolder, 'settings')
        self._providers = {self._get_default_provider():
                           'https://store-it.mweb.co.za/auth/v1.0',
                           self.get_custom_provider(): None}
        if not os.path.isdir(self.configFolder):
            os.mkdir(self.configFolder)

    def _get_key(self, section, key):
        config = ConfigParser.RawConfigParser()
        config.read(self.configFilePath)
        try:
            return config.get(section, key)
        except:
            return ''

    def _set_key(self, section, key, value):
        config = ConfigParser.RawConfigParser()
        config.read(self.configFilePath)
        if not section in config.sections():
            config.add_section(section)
        config.set(section, key, value)
        with open(self.configFilePath, 'wb') as configFile:
            config.write(configFile)

    def _get_providers(self):
        return self._providers.keys()

    def _get_username(self):
        return self._get_key(AUTH_SECTION, USERNAME)

    def _set_username(self, username):
        print('set username to %r' % username)
        self._set_key(AUTH_SECTION, USERNAME, username)

    def _get_password(self):
        # TODO: need to figure out how we're going to do encryption here
        return self._get_key(AUTH_SECTION, PASSWORD)

    def _set_password(self, password):
        print('set password to %r' % password)
        self._set_key(AUTH_SECTION, PASSWORD, password)

    def _get_authUrl(self):
        return self._get_key(AUTH_SECTION, URL)

    def _set_authUrl(self, url):
        print('set url to %r' % url)
        return self._set_key(AUTH_SECTION, URL, url)

    def _get_storage_provider(self):
        return self._get_key(AUTH_SECTION, STORAGE_PROVIDER)

    def _set_storage_provider(self, value):
        return self._set_key(AUTH_SECTION, STORAGE_PROVIDER, value)

    def _get_default_provider(self):
        return 'MWEB : Store-It'

    def _get_default_auth_url(self):
        return self._providers[self._get_default_provider()]

    authUrl = property(_get_authUrl, _set_authUrl)
    defaultAuthUrl = property(_get_default_auth_url)
    defaultProvider = property(_get_default_provider)
    username = property(_get_username, _set_username)
    password = property(_get_password, _set_password)
    storageProvider = property(_get_storage_provider, _set_storage_provider)
    providers = property(_get_providers)

    def get_provider_url(self, provider):
        defaultUrl = self._get_default_auth_url()
        providerUrls = {self.providers[0]: defaultUrl,
                        self.providers[1]: None}
        if provider in self.providers:
            return providerUrls[provider]
        else:
            return None

    def get_provider_by_url(self, url):
        for provider in self._providers:
            if url == self._providers[provider]:
                return provider
        return None

    def get_custom_provider(self):
        return 'Custom'

    def get_home_folder(self):
        tmp = os.path.join(os.environ['USERPROFILE'],
                           'Digital Panda',
                           self.username)
        #logging.info('home folder = %r' % tmp)
        return tmp

    def get_database_path(self):
        # in order to avoid crazy version problems - we restrict
        # database to software version
        filename = 'sync_%s.db' % (version.version)
        return os.path.join(self.configFolder, filename)

    def get_log_file_folder(self):
        return self.configFolder

    def get_log_file_name(self):
        return os.path.join(self.configFolder, 'logging.log')

    def get_config_folder(self):
        return self.configFolder

    def get_temporary_folder(self):
        return self.configFolder

    def get_trash_folder(self):
        return "Trash"

    def get_update_interval(self):
        interval = self._get_key(ADVANCED_SECTION, 'update_interval')
        if not interval:
            # interval in seconds
            interval = 20
        return int(interval)

    """ removed in favour of upgrade url
    def get_upgrade_branch(self):
        upgrade_branch = self._get_key(ADVANCED_SECTION, 'upgrade_branch')
        if not upgrade_branch:
            upgrade_branch = BRANCH_STABLE
        return upgrade_branch
    """

    def get_upgrade_url(self):
        upgrade_url = self._get_key(ADVANCED_SECTION, 'upgrade_url')
        if not upgrade_url:
            upgrade_url = UPGRADE_URL
        return upgrade_url
