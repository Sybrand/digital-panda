from bucket.local import LocalBucket
from bucket.abstract import BucketFile
import config
import statestore
import logging
import os


class Upload(object):
    def __init__(self, objectStore):
        self.objectStore = objectStore
        self.localStore = LocalBucket()
        c = config.Config()
        self.localSyncPath = c.get_home_folder()
        self.state = statestore.StateStore()

    def stop(self):
        pass

    def perform(self):
        logging.debug('Upload::perform - begin')

        if not os.path.exists(self.localSyncPath):
            os.makedirs(self.localSyncPath)
        files = os.listdir(self.localSyncPath)
        for f in files:
            fullPath = os.path.join(self.localSyncPath, f)
            #logging.debug(f)
            if os.path.isdir(fullPath):
                #logging.debug('is directory')
                self.upload_directory(f)
            elif os.path.isfile(fullPath):
                self.processFile(fullPath, f)

        logging.debug('Upload::perform - end')

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
            cmpResult, syncInfo, dm = self.compareFile(localPath,
                                                       remotePath,
                                                       remoteFileInfo)
            if cmpResult:
                # the files are the same!
                # but wait - did we have syncinfo?
                if not syncInfo:
                    # we didn't have sync info!
                    # or it's been invalidated so we
                    # need to store it
                    logging.info('sync info for %s updated' % localPath)
                    self.state.markObjectAsSynced(remotePath,
                                                  remoteFileInfo.hash,
                                                  dm)
            else:
                localFileInfo = self.localStore.get_file_info(localPath)
                syncInfo = self.state.getObjectSyncInfo(remotePath)

                logging.info('remote hash: %r' % remoteFileInfo.hash)
                logging.info('local hash: %r' % localFileInfo.hash)
                logging.info('sync hash: %r' % syncInfo.hash)

                if remoteFileInfo.hash == syncInfo.hash:
                    # the remote file, and our sync record are the same
                    # that means the local version hash changed
                    self.objectStore.upload_object(localPath,
                                                   remotePath,
                                                   localFileInfo.hash)
                    self.state.markObjectAsSynced(remotePath,
                                                  localFileInfo.hash,
                                                  dm)
                elif localFileInfo.hash == syncInfo.hash:
                    # the local file hasn't changed - so it must be the
                    # remote file! the download process should pick this up
                    pass
                else:
                    logging.warn('not implemented!')
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
        else:
            # woah - the file isn't online!
            # do we upload the local file? or do we delete it???
            if self.fileHasBeenUploaded(localPath, remotePath):
                # we uploaded this file - but it's NOT online!!
                # this can only mean that it's been deleted online
                # so we need to delete it locally!
                logging.warn('delete local file %s' % localPath)
                os.remove(localPath)
                self.state.removeObjectSyncRecord(remotePath)
            else:
                # the file hasn't been uploaded before, so we upload it now
                self.uploadFile(localPath, remotePath)

    def uploadFile(self, localPath, remotePath):
        logging.warn('upload local file %s' % localPath)
        # before we upload it - we calculate the hash
        localFileInfo = self.localStore.get_file_info(localPath)
        self.objectStore.upload_object(localPath,
                                       remotePath,
                                       localFileInfo.hash)
        localMD = self.localStore.get_last_modified_date(localPath)
        self.state.markObjectAsSynced(remotePath,
                                      localFileInfo.hash,
                                      localMD)

    def fileHasBeenUploaded(self, localPath, remotePath):
        syncInfo = self.state.getObjectSyncInfo(remotePath)
        if syncInfo:
            # we have info for the file - lets check that it's the same info!
            localMD = self.localStore.get_last_modified_date(localPath)
            if syncInfo.dateModified != localMD:
                # the modification date has changed - so it might not be the
                # same file we logged!
                localFileInfo = self.localStore.get_file_info(localPath)
                # if the hash of the local file, is the same as the one we
                # stored then the file hasn't changed since we synced, so
                # we have uploaded this file
                return localFileInfo.hash == syncInfo.hash
            else:
                # the file date hasn't modified, so we assume it hasn't changed
                # if it hasn't changed - it means we've uploaded it
                return True
        else:
            # we don't have any local sync info - so our assumption
            # is that this file has not been uploaded
            return False

    def compareFile(self, localFilePath, remoteFilePath, remoteFileInfo):
        """
        return (True if files are the same, local sync info (if valid/present),
                local last modified date)
        """
        # get sync info for the file
        syncInfo = self.state.getObjectSyncInfo(remoteFilePath)
        localFileInfo = None
        if syncInfo:
            # we have local sync info
            # if the sync modified date, and file modified date are the same
            # then we know for a fact the file is unchanged
            localMD = self.localStore.get_last_modified_date(localFilePath)
            if syncInfo.dateModified != localMD:
                # the dates differ! we need to calculate the hash
                localFileInfo = self.localStore.get_file_info(localFilePath)
                # invalidate the sync info!
                syncInfo = None
            else:
                # the dates are the same, so the hash from the syncInfo
                # should be good
                localFileInfo = BucketFile(remoteFilePath, None, None)
                localFileInfo.hash = syncInfo.hash
        else:
            # we don't have sync info! this means we HAVE to do a hash compare
            localFileInfo = self.localStore.get_file_info(localFilePath)
            localMD = self.localStore.get_last_modified_date(localFilePath)

        return (localFileInfo.hash == remoteFileInfo.hash,
                syncInfo,
                localMD)
