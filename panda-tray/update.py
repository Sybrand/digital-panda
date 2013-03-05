#import logging
#import sys
import messages
#import config
from worker import BaseWorker
from updater import AutoUpdate


class Update(BaseWorker):
    def __init__(self, outputQueue):
        BaseWorker.__init__(self)
        self._outputQueue = outputQueue

    def _get_working_message(self):
        return messages.Status('Checking for updates')

    def perform(self):
        autoUpdate = AutoUpdate(self)
        if autoUpdate.UpdateAvailable():
            availableVersion = autoUpdate.GetAvailableVersion()
            if autoUpdate.DownloadUpdate(availableVersion):
                if autoUpdate.InstallUpdate(availableVersion):
                    pass

    def stop(self):
        pass
