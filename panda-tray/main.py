#!/usr/bin/python2.7
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import taskbar
import os
# right now, this requires python setup.py develop to be run on digitalpanda
from bucket.swift import SwiftBucket
#.bucket.swift import SwiftBucket
import mediator
import config
import Queue
import logging
import esky
import sys


def check_for_update():
    if getattr(sys,"frozen",False):
        updateUrl = 'http://www.digitalpanda.co.za/updates/'
        logging.info('checking for update...')
        try:
            app = esky.Esky(sys.executable, updateUrl)
            logging.info('currently running %s' % app.active_version)
            try:
                app.auto_update()
            except Exception, e:
                logging.error('error updating app: %r' % e)
            finally:
                app.cleanup()
        except Exception, e:
            logging.error('error updating app: %r' % e)
        logging.info('update check complete')
    else:
        logging.info('not running in frozen mode - no update check')


def main():
    check_for_update()
    useWxTaskBarIcon = True

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
        responseQueue = Queue.Queue()
        app = wx.PySimpleApp()
        taskbar.TaskBar(requestQueue, responseQueue)

        cfg = config.Config()
        m = mediator.Mediator(SwiftBucket(cfg.get_authUrl(),
                                          cfg.get_username(),
                                          cfg.get_password()),
                              requestQueue,
                              responseQueue)
        m.start()
        try:
            app.MainLoop()
        finally:
            m.stop()
    else:
        logging.error('Wups - we''re trying to get Ubuntu 12.10 to work!')

#if __name__ == '__main__':
    # rather call exe.py (for py2exe) or dev.py
#    main()
