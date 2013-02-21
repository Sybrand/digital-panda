#!/usr/bin/python2.7
'''
Created on January 18, 2013

@author: Sybrand Strauss
'''

import threading
import logging
import sys
import Queue
import messages
import config
import bucket.swift
import traceback
import update
from upload import Upload
from download import Download
from worker import BaseWorker


class Sleep(BaseWorker):
    def __init__(self, sleepTime):
        self._sleepTime = sleepTime
        self.queue = Queue.Queue()

    def perform(self):
        #logging.debug('Sleep::perform')
        try:
            self.queue.get(timeout=self._sleepTime)
        except:
            # we don't really care if our sleep is
            # interrupted
            pass
        #logging.debug('Sleep::perform - end')

    def stop(self):
        self.queue.put(1)


class Authenticate(BaseWorker):
    def __init__(self, objectStore, outputQueue):
        self.outputQueue = outputQueue
        self.objectStore = objectStore
        self.isAuthenticated = False
        self.retryWait = 1

    def can_authenticate(self):
        return (self.objectStore.credentials.authUrl and
                self.objectStore.credentials.username and
                self.objectStore.credentials.password)

    def perform(self):
        #logging.debug('Authenticate::perform')
        if self.can_authenticate():
            self.outputQueue.put(messages.Status('Authenticating...'))
            if self.objectStore.authenticate():
                self.outputQueue.put(messages.Status('Authenticated'))
                self.isAuthenticated = True
                self.retryWait = 1
            else:
                self.isAuthenticated = False
                self.outputQueue.put(messages.Status('Connection failed'))
                self.retryWait = min(120, self.retryWait * 2)
        else:
            status = 'Waiting for settings'
            self.outputQueue.put(messages.Status(status))
            self.retryWait = 1
        #else:
        #    self.outputQueue.put(messages.Status('Server url '
        #                                             'not set'))

    def get_retry_wait(self):
        return self._retryWait

    def set_retry_wait(self, value):
        self._retryWait = value

    def get_authenticated(self):
        return self._authenticated

    def set_authenticated(self, value):
        self._authenticated = value

    retryWait = property(get_retry_wait, set_retry_wait)
    isAuthenticated = property(get_authenticated, set_authenticated)

    def stop(self):
        pass


class Mediator(threading.Thread):
    def __init__(self, objectStore, inputQueue, outputQueue):
        """
        objectStore: probably swift
        inputQueue: requests originating from something
        outputQueue: responses to something
        """
        threading.Thread.__init__(self)
        self.objectStore = objectStore
        self.inputQueue = inputQueue
        self.outputQueue = outputQueue
        self.taskList = Queue.Queue()
        self.running = True
        self.currentTask = None
        self.lock = threading.Lock()
        self.inputQueueThread = threading.Thread(target=self.inputQueueWatcher)
        self.inputQueueThread.start()
        c = config.Config()
        self.updateInterval = c.get_update_interval()

    def inputQueueWatcher(self):
        while (self.running):
            message = self.inputQueue.get()
            if isinstance(message, messages.Stop):
                logging.debug('stop message recieved')
                logging.debug('attempting lock')
                if self.lock.acquire(True):
                    logging.debug('got the lock')
                    try:
                        if self.currentTask:
                            logging.debug('telling current task to stop')
                            self.currentTask.stop()
                    finally:
                        self.lock.release()
                break
            elif isinstance(message,
                            messages.SettingsChanged):
                logging.debug('handling settings changed')
                c = config.Config()
                # TODO: get rid of this explicit reference to swift :(
                credentials = bucket.swift.SwiftCredentials(c.authUrl,
                                                            c.username,
                                                            c.password)
                self.objectStore.credentials = credentials

                logging.debug('locking...')
                if self.lock.acquire(True):
                    try:
                        logging.debug('stopping the current task...')
                        self.currentTask.stop()
                        logging.debug('clearing pending tasks...')
                        self.clearPendingTasks()
                        logging.debug('putting auth on queue...')
                        self.taskList.put(Authenticate(self.objectStore,
                                                       self.outputQueue))
                    finally:
                        self.lock.release()
                        logging.debug('released lock')
            else:
                logging.info('unhandeled message type recieve: %r' % message)

    def run(self):
        # the first thing we try to do, is connect
        self.taskList.put(update.Update(self.outputQueue))
        self.taskList.put(Authenticate(self.objectStore,
                                       self.outputQueue))
        self._starting = True
        while self.running:
            if self.lock.acquire(True):
                try:
                    self.currentTask = self.getNextTask()
                finally:
                    self.lock.release()

            if self.currentTask:
                try:
                    self.currentTask.perform()
                except:
                    logging.info('exception processing: %r' %
                                 sys.exc_info()[0])
                    traceback.print_exc(file=sys.stdout)
                finally:
                    self.addNewTasks()
        logging.info('done running the mediator')

    def addNewTasks(self):

        if self.lock.acquire(True):
            try:
                if self.running:
                    #logging.debug("task complete! time for next task!")
                    if isinstance(self.currentTask, Upload):
                        #logging.debug('we completed a download')
                        # after downloading - we check for uploads
                        # but first we relax for 5 seconds
                        # it's important to relax - to give swfit a few
                        # seconds to catch up
                        if not self.currentTask.hadWorkToDo:
                            # if you didn't have any work to do - take a break!
                            if not self._starting:
                                self.taskList.put(Sleep(self.updateInterval))
                        else:
                            #logging.info('there was work to do - no resting!')
                            pass
                        download = Download(self.objectStore, self.outputQueue)
                        self.taskList.put(download)
                        self._starting = False
                    elif isinstance(self.currentTask, Download):
                        #logging.debug('we completed a upload')
                        if not self.currentTask.hadWorkToDo:
                            # if you didn't have any work to do - take a break!
                            if not self._starting:
                                self.taskList.put(Sleep(self.updateInterval))
                        else:
                            #logging.info('there was work to do - no resting!')
                            pass
                        upload = Upload(self.objectStore, self.outputQueue)
                        self.taskList.put(upload)
                        self._starting = False
                    elif isinstance(self.currentTask, Authenticate):
                        if self.currentTask.isAuthenticated:
                            #upload = Upload(self.objectStore,
                            #    self.outputQueue)
                            #self.taskList.put(upload)
                            download = Download(self.objectStore,
                                                self.outputQueue)
                            self.taskList.put(download)
                        else:
                            sleep = Sleep(self.currentTask.retryWait)
                            #logging.info('failed to auth'
                            #             ' - sleeping for %r'
                            #             % self.currentTask.retryWait)
                            self.taskList.put(sleep)
                            self.taskList.put(self.currentTask)
                    elif isinstance(self.currentTask, Sleep):
                        pass
                    elif isinstance(self.currentTask, update.Update):
                        if self.currentTask.hadWorkToDo:
                            self.scheduleRestart()
                    else:
                        logging.warn('unhandeled task completion!')
            finally:
                self.lock.release()

    def scheduleRestart(self):
        # ideally - we should check that the config setting aren't open!
        update.restart_this_app()

    def isRunning(self):
        return self.running

    def clearPendingTasks(self):
        self.taskList = Queue.Queue()

    def getNextTask(self):
        return self.taskList.get()
        #if len(self.taskList) > 0:
        #    return self.taskList.pop(0)
        #return None

    def stop(self):
        logging.debug('mediator stoppping...')
        try:
            if self.lock.acquire(True):
                self.running = False
                self.clearPendingTasks()
        finally:
                self.lock.release()
        self.inputQueue.put(messages.Stop)
        self.inputQueueThread.join()
        if self.lock.acquire(True):
            try:
                self.clearPendingTasks()
                self.running = False
                if self.currentTask:
                    logging.debug('stopping the current task...')
                    self.currentTask.stop()
                    self.currentTask = None
            finally:
                self.lock.release()
