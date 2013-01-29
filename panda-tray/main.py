#!/usr/bin/python2.7
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import taskbar
import os
# right now, this requires python setup.py develop to be run on digitalpanda
from bucket.swift import SwiftBucket, SwiftCredentials
#.bucket.swift import SwiftBucket
import mediator
import config
import Queue
import logging
import messages


if os.name == 'nt':
    from win32event import CreateMutex
    from win32api import CloseHandle, GetLastError
    from winerror import ERROR_ALREADY_EXISTS


class SingleInstance(object):
    def __init__(self):
        if os.name == 'nt':
            mutexName = '{4A475CB1-CDB5-46b5-B221-4E36602FC47E}'
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


def main():
    myapp = SingleInstance()
    useWxTaskBarIcon = True
    if myapp.alreadyRunning():
        logging.info('another instance of the sync tool as already running')
        # already running! i'm out of here!
        return

    if os.name == 'posix':
        # running on posix? is it ubuntu?
        import platform
        # get back a tuple: (distname, version, id)
        tuple = platform.linux_distribution('Ubuntu')
        if tuple[1] >= '12.10':
            useWxTaskBarIcon = False

    if useWxTaskBarIcon:
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)

        requestQueue = Queue.Queue()
        messageQueue = Queue.Queue()
        app = wx.PySimpleApp()
        taskbar.TaskBar(requestQueue, messageQueue)

        cfg = config.Config()
        swiftCredentials = SwiftCredentials(cfg.authUrl,
                                            cfg.username,
                                            cfg.password)
        mediatorThread = mediator.Mediator(SwiftBucket(swiftCredentials),
                                           requestQueue,
                                           messageQueue)

        if not swiftCredentials.authUrl or len(swiftCredentials.authUrl) == 0:
            # no auth url? this must be the first time it's running
            messageQueue.put(messages.ShowSettings())

        mediatorThread.start()
        try:
            app.MainLoop()
        finally:
            mediatorThread.stop()
    else:
        logging.error('Wups - we''re trying to get Ubuntu 12.10 to work!')

    del myapp

#if __name__ == '__main__':
    # rather call exe.py (for py2exe) or dev.py
#    main()
