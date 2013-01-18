#!/usr/bin/python2.7
'''
Created on January 18, 2013

@author: Sybrand Strauss
'''

import threading
import time


class Mediator(threading.Thread):
    def __init__(self, objectStore, uiRequestQueue, uiResponseQueue):
        """
        objectStore: probably swift
        uiRequestQueue: requests originating from something
        uiResponsQueue: responses to something
        """
        threading.Thread.__init__(self)
        self.objectStore = objectStore
        self.uiRequestQueue = uiRequestQueue
        self.uiResponseQueue = uiResponseQueue
        self.running = True

    def run(self):
        # the first thing we try to do, is connect
        print("going to put authentication...")
        self.uiResponseQueue.put('Authenticating...')
        print("authenticating...")
        if self.objectStore.authenticate():
            self.uiResponseQueue.put('Authenticated')
        else:
            self.uiResponseQueue.put('Connection failed')
        while self.running:
            time.sleep(0.1)
        print("done running mediator")

    def stop(self):
        self.running = False
