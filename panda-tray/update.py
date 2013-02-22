import esky
import logging
import sys
import messages
import os
import config
from esky.util import appdir_from_executable
from worker import BaseWorker


### BEGIN - taken from https://github.com/cloudmatrix/esky/wiki/FAQ
def restart_this_app():
    appexe = appexe_from_executable(sys.executable)
    logging.info(appexe)
    os.execv(appexe, [appexe] + sys.argv[1:])


def appexe_from_executable(exepath):
    appdir = appdir_from_executable(exepath)
    exename = os.path.basename(exepath)
    #  On OSX we might be in a bundle
    if sys.platform == "darwin":
        if os.path.isdir(os.path.join(appdir, "Contents", "MacOS")):
            return os.path.join(appdir, "Contents", "MacOS", exename)
    return os.path.join(appdir, exename)
### END - taken from https://github.com/cloudmatrix/esky/wiki/FAQ


class Update(BaseWorker):
    def __init__(self, outputQueue):
        BaseWorker.__init__(self)
        self._outputQueue = outputQueue

    def _get_working_message(self):
        return messages.Status('Checking for updates')

    def perform(self):
        if getattr(sys, "frozen", False):
            c = config.Config()
            updateUrl = ('http://www.digitalpanda.co.za/updates_%s/' %
                        (c.get_upgrade_branch()))
            # IMPORTANT: please never remove the logging entry below
            # it's very usefull for debugging, to know where the panda is
            # looking for updates!
            logging.info('checking for update @ %r...' % updateUrl)
            try:
                logging.info('sys.executable = %r' % sys.executable)
                app = esky.Esky(sys.executable, updateUrl)
                logging.info('currently running %s' % app.active_version)
                try:
                    #app.auto_update()
                    # look for a new verion
                    message = messages.Status(self._get_working_message())
                    self._outputQueue.put(message)
                    v = app.find_update()
                    if v:
                        logging.info('found new version: %s' % v)
                        # there is a new version
                        if not app.has_root():
                            logging.info('trying to get root')
                            # we need root to update versions!
                            app.get_root()
                        if app.has_root():
                            # if we got root - we do the update
                            message = messages.Status('Downloading update')
                            self._outputQueue.put(message)
                            logging.info('fetching new version...')
                            app.fetch_version(v)
                            logging.info('installing new version...')
                            message = messages.Status('Installing update')
                            app.install_version(v)
                            logging.info('doing cleanup...')
                            app.cleanup()
                            logging.info('dropping root...')
                            app.drop_root()
                            logging.info('done update')
                            self._set_hadWorkToDo(True)
                        else:
                            logging.info('failed to get root')
                    else:
                        logging.info('no new versions found')
                except Exception, e:
                    logging.error('error updating app: %r' % e)
                finally:
                    """ no - we ONLY do a cleanup after an update
                    otherwise we have to get sudo all the damn time
                    try:
                        app.cleanup()
                    finally:
                        logging.error('error cleaning up app')
                    """
            except Exception, e:
                logging.error('error updating app: %r' % e)
            logging.info('update check complete')
        else:
            # not running in frozen mode - no update check
            pass

    def stop(self):
        pass
