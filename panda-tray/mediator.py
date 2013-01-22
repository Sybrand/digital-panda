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
import statestore


class Upload(object):
    def __init__(self, objectStore):
        self.objectStore = objectStore
        c = config.Config()
        self.localSyncPath = c.get_home_folder()

    def perform(self):

        files = os.listdir(self.localSyncPath)
        for f in files:
            fullPath = os.path.join(self.localSyncPath, f)
            logging.debug(f)
            if os.path.isdir(fullPath):
                #logging.debug('is directory')
                self.upload_directory(f)
            elif os.path.isfile(fullPath):
                self.processFile(fullPath, f)
        return True

    def upload_directory(self, remotePath):
        fullPath = os.path.join(self.localSyncPath, remotePath)
        files = os.listdir(fullPath)
        for f in files:
            # we want everything in unicode!
            if isinstance(f, str):
                # strings we encode to iso-8859-1 (on windows)
                f = f.decode('iso-8859-1')
                # then we push it into unicode
                f = unicode(f)
            newLocalPath = os.path.join(fullPath, f)
            newRemotePath = '%s/%s' % (remotePath, f)
            if os.path.isdir(newLocalPath):
                self.upload_directory(newRemotePath)
            elif os.path.isfile(newLocalPath):
                self.processFile(newLocalPath, newRemotePath)

    def processFile(self, localPath, remotePath):
        """ Depending on a number of factors - we do different
        things with files. Maybe we upload the local file,
        maybe we delete it. Maybe we delete the remote file!
        Maybe there's some kind of conflict and we need to rename
        the local file?
        """
        #logging.info('process %s to %s' % (localPath, remotePath))
        remoteFileInfo = self.objectStore.get_file_info(remotePath)
        if remoteFileInfo:
            # we compare local file, with remote file
            # if they are the same - we do nothing
            localFileInfo = self.getLocalFileInfo(localPath)
            if not self.compareFile(localFileInfo, remoteFileInfo):
                # the files are NOT the same - so either the local
                # one is new, or the remote on is new
                # this is a nasty nasty problem with no perfect solution!
                # lots of thinking to be done here - but in the end
                # it will be some kind of compromise
                # we can however reduce the number of problems:
                # 1) look at the hash we last uploaded
                # 1.1) if the local hash and historic hash are the same
                #      then it means that the remote file is newer, download
                # 1.2) if the historic hash is the same as the remote hash
                #      then we know the local file has changed
                # 1.3) if the historic hash differs from both the remote hash
                #      and the local hash, then we have no way of knowing which
                #      is newer - our only option is to rename the local one
                logging.warn('figure out files! not implemented')
        else:
            # woah - the file isn't online!
            # do we upload the local file? or do we delete it???
            if self.fileHasBeenUploaded(localPath):
                # we uploaded this file - but it's NOT online!!
                # this can only mean that it's been deleted online
                # so we need to delete it locally!
                logging.warn('delete local file, not implemented')
            else:
                # the file hasn't been uploaded before, so we upload it now
                self.objectStore.upload_object(localPath, remotePath)

    def fileHasBeenUploaded(self, path):
        return False

    def getLocalFileInfo(self, path):
        return None

    def compareFile(self, fileInfoA, fileInfoB):
        return True


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
            if self.already_downloaded_file(f.path):
                # if we've already downloaded this file,
                # it means we have to delete it remotely!
                self.delete_remote_file(f.path)
            else:
                # lets get the file
                self.objectStore.download_object(f.path, localPath)
                state = statestore.StateStore()
                state.markObjectAsSynced(f.path, f.hash, f.dateModified)
        else:
            # the file already exists - do we overwrite it?
            # is the file we have newer?
            # is the file we have older?
            pass

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
        """ Establish if this folder was downloaded before
        typical use: the folder doesn't exist locally, but it
        does exist remotely - that would imply that if we'd already
        downloaded it, it can only be missing if it was deleted, and
        thusly, we delete it remotely.
        """
        logging.warn('already_downloaded_folder - not implemented')
        return False

    def already_downloaded_file(self, path):
        """ See: already_downloaded_folder
        """
        logging.warn('already_downloaded_file - not implemented')
        return False

    def delete_remote_folder(self):
        logging.warn('delete_remote_folder - not implemented')

    def delete_remote_file(self):
        logging.warn('delete_remote_file - not implemented')


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
                    #self.scheduleDownloadTask()
                    self.scheduleUploadTask()
            else:
                nextTask = self.getNextTask()
                if nextTask:
                    if nextTask.perform():
                        logging.debug("task complete! time for next task!")
                        if isinstance(nextTask, Download):
                            logging.debug('we completed a download')
                            # after downloading - we check for uploads
                            self.scheduleUploadTask()
                        elif isinstance(nextTask, Upload):
                            logging.debug('we completed a upload')
                            #self.scheduleDownloadTask()
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

    def scheduleUploadTask(self):
        upload = Upload(self.objectStore)
        self.taskList.append(upload)

    def getNextTask(self):
        if len(self.taskList) > 0:
            return self.taskList.pop(0)
        return None

    def stop(self):
        self.running = False
