#!/usr/bin/python2.7
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import taskbar
import os
# right now, this requires python setup.py develop to be run on digitalpanda
from bucket.swift import SwiftProvider, SwiftCredentials
from tooling.instance import SingleInstance
#.bucket.swift import SwiftBucket
import mediator
import config
import Queue
import logging
import messages
import version
import platform
import urllib2
import gtxtaskbar


def main():
    myapp = SingleInstance('{4A475CB1-CDB5-46b5-B221-4E36602FC47E}')
    useWxTaskBarIcon = True
    if myapp.alreadyRunning():
        logging.info('another instance of the sync tool as already running')
        # already running! i'm out of here!
        return

    if os.name == 'posix':
        # running on posix? is it ubuntu?
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
        sys, node, r, v, m, processor = platform.uname()
        userAgent = "DigitalPandaSync/%s (%s %s %s; %s)" % (version.version,
                                                            sys, r, v, m)
        # an attempt to insert the user agent on all open requests
        # i don't actually know if this works!
        opener = urllib2.build_opener()
        opener.addheaders = [('User-agent', userAgent)]
        urllib2.install_opener(opener)

        swiftProvider = SwiftProvider(swiftCredentials, userAgent,
                                      messageQueue)
        mediatorThread = mediator.Mediator(swiftProvider,
                                           requestQueue,
                                           messageQueue)

        if (not swiftCredentials.authUrl or
                not swiftCredentials.username or
                not swiftCredentials.password):
            # no auth url? this must be the first time it's running
            messageQueue.put(messages.ShowSettings())

        mediatorThread.start()
        try:
            app.MainLoop()
        finally:
            mediatorThread.stop()
    else:
        gtxtaskbar.run()

    del myapp

#if __name__ == '__main__':
    # rather call exe.py (for py2exe) or dev.py
#    main()
