#import logging
#import sys
import messages
import config
import logging
import sys
import exceptions
from worker import BaseWorker
from updater import AutoUpdate


class Update(BaseWorker):
    def __init__(self, outputQueue):
        BaseWorker.__init__(self)
        self._outputQueue = outputQueue

    def _get_working_message(self):
        return messages.Status('Checking for updates')

    def perform(self):
        c = config.Config()
        autoUpdate = AutoUpdate(self, c.get_upgrade_url())
        try:
            if autoUpdate.UpdateAvailable():
                availableVersion = autoUpdate.GetAvailableVersion()
                if autoUpdate.DownloadUpdate(availableVersion):
                    if autoUpdate.InstallUpdate(availableVersion):
                        pass
        except Exception as e:
            logging.warn(e.message)
        except:
            logging.warn('problem with updater: %r' % sys.exc_info()[0])


    def stop(self):
        pass
