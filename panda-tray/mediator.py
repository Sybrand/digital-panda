    #!/usr/bin/python2.7
'''
Created on January 18, 2013

@author: Sybrand Strauss
'''

import threading
import time
import logging
import os
import config


class Download(object):
    def __init__(self, objectStore):
        self.objectStore = objectStore
        c = config.Config()
        self.localSyncPath = c.get_home_folder()

    def perform(self):
        # get the current directory
        files = self.objectStore.list_dir(None)
        logging.debug('got %r files' % len(files))
        for f in files:
            if f.isFolder:
                self.download_folder(f)
            else:
                self.download_file(f)
        return True

    def download_file(self, f):
        localPath = self.get_local_path(f.path)
        if not os.path.exists(localPath):
            # should we download this file?
            # should we delete this file?
            logging.debug('download_file, path: %s' % f.path)
            logging.debug('download_file, name: %s' % f.name)
            logging.debug('download_file, contentType: %s' % f.contentType)

    def download_folder(self, folder):
        # does the folder exist locally?
        localPath = self.get_local_path(folder.path)
        downloadFolderContents = True
        if not os.path.exists(localPath):
            # the path exists online, but NOT locally
            # we do one of two things, we either
            # a) delete it remotely
            #     if we know for a fact we've already downloaded this folder,
            #     then it not being here, can only mean we've deleted it
            # b) download it
            #     if we haven't marked this folder as being downloaded,
            #     then we get it now
            if self.already_downloaded_folder(folder.path):
                logging.info('we need to delete %r!' % localPath)
                self.delete_remote_folder(folder.path)
                downloadFolderContents = False
            else:
                logging.info('creating %r' % localPath)
                os.makedirs(localPath)
        if downloadFolderContents:
            files = self.objectStore.list_dir(folder.path)
            for f in files:
                if f.isFolder:
                    self.download_folder(f)
                else:
                    self.download_file(f)

    def get_local_path(self, remote_path):
        return os.path.join(self.localSyncPath, remote_path)

    def already_downloaded_folder(self, path):
        logging.warn('already_downloaded_folder - not implemented')
        return False

    def delete_remote_folder(self):
        logging.warn('delete_remote_folder - not implemented')


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
        self.taskList = list()
        self.running = True
        # retry wait in seconds
        self.retryWait = 1
        self.authenticated = False

    def run(self):
        # the first thing we try to do, is connect

        while self.running:
            if not self.authenticated:
                # not connected? start over! clear all pending tasks
                self.clearPendingTasks()
                # if for some reason we're not connected - connect!
                self.authenticate()
                # if for some reason we failed to connect - sleep
                if not self.authenticated:
                    time.sleep(self.retryWait)
                else:
                    self.scheduleDownloadTask()
            else:
                nextTask = self.getNextTask()
                if nextTask:
                    if nextTask.perform():
                        logging.debug("download complete! time for next task!")
                else:
                    time.sleep(0.1)
        logging.info('done running the mediator')

    def authenticate(self):
        logging.debug("going to put authentication...")
        self.uiResponseQueue.put('Authenticating...')
        logging.info('authenticating...')
        if self.objectStore.authenticate():
            self.uiResponseQueue.put('Authenticated')
            self.authenticated = True
            self.retryWait = 1
        else:
            self.authenticated = False
            self.uiResponseQueue.put('Connection failed')
            self.retryWait = self.retryWait * 2

    def clearPendingTasks(self):
        self.taskList = list()

    def scheduleDownloadTask(self):
        download = Download(self.objectStore)
        self.taskList.append(download)

    def getNextTask(self):
        if len(self.taskList) > 0:
            return self.taskList.pop(0)
        return None

    def stop(self):
        self.running = False
