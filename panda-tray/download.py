from bucket.local import LocalBucket
import config
import statestore
import logging
import os
import threading


class Download(object):
    def __init__(self, objectStore):
        self.objectStore = objectStore
        self.localStore = LocalBucket()
        c = config.Config()
        self.localSyncPath = c.get_home_folder()
        self.tempDownloadFolder = c.get_temporary_folder()
        self.state = statestore.StateStore()
        self.lock = threading.Lock()

    def stop(self):
        pass

    def perform(self):
        logging.debug('Download::perform - begin')
        # get the current directory
        files = self.objectStore.list_dir(None)
        for f in files:
            if f.isFolder:
                self.download_folder(f)
            else:
                self.download_file(f)
        logging.debug('Download::perform - end')

    def download_file(self, f):
        localPath = self.get_local_path(f.path)
        if not os.path.exists(localPath):
            logging.debug('does not exist: %s' % localPath)
            if self.already_synced_file(f.path):
                # if we've already downloaded this file,
                # it means we have to delete it remotely!
                logging.info('delete remote version of %s' % localPath)
                self.delete_remote_file(f.path)
            else:
                # lets get the file
                tmpFile = self.get_tmp_filename()
                if os.path.exists(tmpFile):
                    os.remove(tmpFile)
                self.objectStore.download_object(f.path, tmpFile)
                os.rename(tmpFile, localPath)
                localMD = self.localStore.get_last_modified_date(localPath)
                self.state.markObjectAsSynced(f.path, f.hash, localMD)
        else:
            # the file already exists - do we overwrite it?
            syncInfo = self.state.getObjectSyncInfo(f.path)
            if syncInfo:
                localMD = self.localStore.get_last_modified_date(localPath)
                if syncInfo.dateModified != localMD:
                    # the dates differ! we need to calculate the hash!
                    localFileInfo = self.localStore.get_file_info(localPath)
                    if localFileInfo.hash != f.hash:
                        # hmm - ok, if the online one, has the same hash
                        # as I synced, then it means the local file
                        # has changed!
                        if syncInfo.hash == f.hash:
                            # online and synced have the same version!
                            # that means the local one has changed
                            # so we're not downloading anything
                            # the upload process should handle this
                            pass
                        else:
                            logging.warn('TODO: the files differ - which '
                                         'one do I use?')
                    else:
                        # all good - the files are the same
                        # we can update our local sync info
                        self.state.markObjectAsSynced(f.path,
                                                      localFileInfo.hash,
                                                      localMD)
                else:
                    # dates are the same, so we can assume the hash
                    # hasn't changed
                    if syncInfo.hash != f.hash:
                        # if the sync info is the same as the local file
                        # then it must mean the remote file has changed!
                        get_file_info = self.localStore.get_file_info
                        localFileInfo = get_file_info(localPath)
                        if localFileInfo.hash == syncInfo.hash:
                            self.replace_file(f, localPath)
                        else:
                            logging.info('remote hash: %r' % f.hash)
                            logging.info('local hash: %r' % localFileInfo.hash)
                            logging.info('sync hash: %r' % syncInfo.hash)
                            logging.warn('sync hash differs from local hash!')
                    else:
                        # sync hash is same as remote hash, and the file date
                        # hasn't changed. we assume this to mean, there have
                        # been no changes
                        pass
            else:
                logging.info('TODO: what to do when there is no sync info!')
            pass

    def replace_file(self, f, localPath):
        tmpFile = self.get_tmp_filename()
        if os.path.exists(tmpFile):
            os.remove(tmpFile)
        self.objectStore.download_object(f.path, tmpFile)
        os.remove(localPath)
        os.rename(tmpFile, localPath)
        localMD = self.localStore.get_last_modified_date(localPath)
        self.state.markObjectAsSynced(f.path,
                                      f.hash,
                                      localMD)

    def get_tmp_filename(self):
        return os.path.join(self.tempDownloadFolder, 'tmpfile')

    def download_folder(self, folder):
        # does the folder exist locally?
        #logging.debug('download_folder(%s)' % folder.path)
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
                logging.info('creating %r..' % localPath)
                os.makedirs(localPath)
                logging.info('done creating %r' % localPath)
        if downloadFolderContents:
            files = self.objectStore.list_dir(folder.path)
            #logging.debug('got %r files' % len(files))
            for f in files:
                if folder.path.strip('/') != f.path.strip('/'):
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
        logging.warn('TODO: implement check to see '
                     'if %s has already been downloaded' % path)
        return False

    def already_synced_file(self, path):
        """ See: already_downloaded_folder
        """
        syncInfo = self.state.getObjectSyncInfo(path)
        if syncInfo:
            remoteFileInfo = self.objectStore.get_file_info(path)
            if remoteFileInfo.hash == syncInfo.hash:
                # the hash of the file we synced, is the
                # same as the one online.
                # this means, we've already synced this file!
                return True
            return False
        else:
            return False

    def delete_remote_folder(self):
        logging.warn('delete_remote_folder - not implemented')

    def delete_remote_file(self, path):
        self.objectStore.delete_object(path)
        self.state.removeObjectSyncRecord(path)