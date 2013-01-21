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


def main():
    logging.basicConfig(level=logging.DEBUG)
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

if __name__ == '__main__':
    main()
