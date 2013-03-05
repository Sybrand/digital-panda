import os
import logging


if os.name == 'nt':
    from win32event import CreateMutex
    from win32api import CloseHandle, GetLastError
    from winerror import ERROR_ALREADY_EXISTS


class SingleInstance(object):
    def __init__(self, instanceName):
        if os.name == 'nt':
            mutexName = instanceName
            self.mutex = CreateMutex(None, False, mutexName)
            self.lasterror = GetLastError()

    def alreadyRunning(self):
        if os.name == 'nt':
            return (self.lasterror == ERROR_ALREADY_EXISTS)
        else:
            logging.warn('alreadyRunning not implemented')
            return False

    def __del__(self):
        if os.name == 'nt':
            if self and self.mutex:
                CloseHandle(self.mutex)
