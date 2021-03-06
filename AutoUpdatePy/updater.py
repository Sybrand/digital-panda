import os
import urllib
import httplib
import json
import hashlib
import logging
import time
import zipfile
import pythoncom
import ConfigParser
from win32com.client import Dispatch


class AutoUpdate:
    def __init__(self, parent, upgradeHost):
        self.parent = parent

        # TODO: the config stuff is very much stolen from panda-tray - need,
        # to pull this into a common place!
        appDataFolder = os.environ['APPDATA']
        configFolder = os.path.join(appDataFolder, 'Digital Panda')
        configFilePath = os.path.join(configFolder, 'settings')
        if not upgradeHost:
            self.upgradeHost = self._get_config_key(configFilePath, "advanced", "upgrade_url")
            if not self.upgradeHost:
                # we default to the normal place to get this
                self.upgradeHost = 'www.digitalpanda.co.za'
        else:
            self.upgradeHost = upgradeHost
        logging.debug('AutoUpdate.__init__: self.upgradeHost is %s' % self.upgradeHost)

    def _get_config_key(self, configFilePath, section, key):
        config = ConfigParser.RawConfigParser()
        config.read(configFilePath)
        try:
            return config.get(section, key)
        except:
            return ''

    def IsInstalled(self):
        # check to see if digital panda is installed
        versionPath = self.GetCurrentVersionPath()
        if os.path.exists(versionPath):
            # is the application installed?
            applicationPath = self.GetPandaPath()
            return os.path.exists(applicationPath)
        return False

    def GetCurrentVersionPath(self):
        return os.path.join(self.GetApplicationPath(), "version.txt")

    def GetPandaExeName(self):
        return "panda-tray-w.exe"

    def GetPandaPath(self):
        currentVersion, currentLocation = self.GetCurrentVersion()
        return os.path.join(self.GetApplicationPath(), currentLocation,
                            self.GetPandaExeName())

    def GetApplicationPath(self):
        return os.path.join(os.environ['APPDATA'], 'Digital Panda')

    # we have a rather elaborate way of figuring out the current version
    # there are two way to run this class - from within an application - in which case
    # using the compiled version number would make sense
    # or - from an auto-update application, in which case the compiled version number
    # doesn't make sense - since we're asking about another application!
    def GetCurrentVersion(self):
        versionPath = self.GetCurrentVersionPath()
        version = 0
        location = None
        if os.path.exists(versionPath):
            f = open(versionPath, 'rt')
            data = f.read()
            versionJson = json.loads(data)
            f.close()
            logging.info('%r' % versionJson['version'])
            version = versionJson['version']
            location = versionJson['location']
        return (version, location)

    def GetAvailableVersion(self):
        logging.debug('creating http connection to %s' % self.upgradeHost)
        connection = httplib.HTTPConnection(host=self.upgradeHost, port=80, strict=False)
        infoLocation = '/update/win7_32.txt'
        logging.debug('looking for update info @ %s' % infoLocation)
        connection.request('GET', infoLocation)
        result = connection.getresponse()
        if result.status != 200:
            raise Exception('unexpected response: %r' % result.status)
        data = result.read()
        return json.loads(data)

    def GetUpdatePath(self, version):
        return os.path.join(self.GetApplicationPath(),
                            "updates",
                            os.path.basename(version['location']))

    def GetHashFromFile(self, path):
        md5 = hashlib.md5()
        with open(path, 'rb') as f:
            while True:
                data = f.read(1048576)
                if not data:
                    break
                md5.update(data)
        return md5.hexdigest()

    def IsFileOk(self, filePath, expectedHash):
        if os.path.exists(filePath):
            logging.info('%r already exists!' % (filePath))
            fileHash = self.GetHashFromFile(filePath)
            logging.debug('comparing %r with %r' % (fileHash, expectedHash))
            return fileHash == expectedHash
        return False

    def GetFileResumePosition(self, path):
        if os.path.exists(path):
            return os.path.getsize(path)
        return 0

    def DownloadUpdate(self, version):
        filePath = self.GetUpdatePath(version)
        if self.IsFileOk(filePath, version['hash']):
            # file is there - and ok - no need to download
            return True
        logging.debug('going to download file...')
        # download the file...
        logging.debug('version info: %r' % version)
        fileSize = version['fileSize']
        logging.debug('getting the resume position...')
        totalBytesRead = self.GetFileResumePosition(filePath)
        logging.debug('current file size = %r' % totalBytesRead)
        if totalBytesRead >= fileSize:
            logging.info('deleting the existing file - it''s too big!')
            # if the total bytes read is more than the expected
            # file size - we need to get rid of the existing file
            os.remove(filePath)
            totalBytesRead = 0
        makingProgress = True

        while totalBytesRead < fileSize and makingProgress:
            makingProgress = False
            resumePosition = self.GetFileResumePosition(filePath)
            totalBytesRead = resumePosition
            connection = httplib.HTTPConnection(version['host'])
            resume = 'bytes=%d-%d' % (resumePosition, fileSize)
            logging.info('Range: %s' % resume)
            headers = {'Range': resume}
            location = urllib.quote(version['location'])
            logging.info(location)
            connection.request('GET', location, None, headers)
            result = connection.getresponse()
            logging.info('request status: %r' % result.status)
            if not (result.status == 200 or result.status == 206):
                raise Exception(result.status)
            if totalBytesRead < fileSize:
                # if the file is greater than 0, and smaller than the file size,
                # we read it appended
                targetFile = open(filePath, 'a+b')
            else:
                # make sure totalBytes read is reset to 0!
                targetFileDir = os.path.dirname(filePath)
                if not os.path.exists(targetFileDir):
                    os.makedirs(targetFileDir)
                targetFile = open(filePath, 'wb')
            chunkSize = 1048576
            data = result.read(chunkSize)
            bytesRead = len(data)
            logging.info('read %r bytes' % bytesRead)
            while totalBytesRead < fileSize:
                if data:
                    bytesRead = len(data)
                    totalBytesRead += bytesRead
                    logging.info('read %d / %d bytes' %
                                 (totalBytesRead, fileSize))
                    makingProgress = True
                    targetFile.write(data)
                    self.UpdateProgress(totalBytesRead, fileSize)
                else:
                    time.sleep(1)
                data = result.read(chunkSize)
            logging.debug('done reading file!')

        targetFile.flush()
        targetFile.close()
        fileHash = self.GetHashFromFile(filePath)

        logging.info('done downloading file - comparing hash: %r == %r' %
                     (fileHash, version['hash']))

        return fileHash == version['hash']

    def GetShortcutPath(self):
        return os.path.join(self.GetApplicationPath(), "Digital Panda.lnk")

    def InstallUpdate(self, version):
        updatePath = self.GetUpdatePath(version)
        applicationPath = self.GetApplicationPath()
        fileName = os.path.basename(updatePath)
        end = fileName.rfind('.')
        if not (end > 0):
            end = len(fileName)
        directoryName = fileName[0: end]
        targetPath = os.path.join(applicationPath, directoryName)
        if not os.path.exists(targetPath):
            os.makedirs(targetPath)

        zfile = zipfile.ZipFile(updatePath)
        for name in zfile.namelist():
            (dirname, filename) = os.path.split(name)
            targetDir = os.path.join(targetPath, dirname)
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            if filename:
                logging.info('filename = %r' % filename)
                targetFile = os.path.join(targetPath, dirname, filename)
                fd = open(targetFile, 'wb')
                fd.write(zfile.read(name))
                fd.close()

        pandaPath = os.path.join(targetPath, self.GetPandaExeName())
        logging.info('pandaPath = %r' % pandaPath)
        workingDirectory = os.path.dirname(pandaPath)
        shortcutPath = self.GetShortcutPath()
        pythoncom.CoInitialize()
        shell = Dispatch('WScript.Shell')
        shortcut = shell.CreateShortCut(shortcutPath)
        shortcut.Targetpath = pandaPath
        shortcut.WorkingDirectory = workingDirectory
        shortcut.Description = 'The Digital Panda'
        shortcut.IconLocation = pandaPath
        shortcut.save()

        fd = open(self.GetCurrentVersionPath(), 'w')
        versionFile = ('{"version": %r, "location":"%s"}' %
                       (version['version'], directoryName))
        fd.write(versionFile)
        fd.flush()
        fd.close()

        return True

    def Install(self):
        version = self.GetAvailableVersion()
        if self.DownloadUpdate(version):
            return self.InstallUpdate(version)
        return False

    def UpdateProgress(self, bytesRead, expectedBytes):
        if self.parent:
            self.parent.SignalDownloadProgress(bytesRead, expectedBytes)

    def UpdateAvailable(self):
        version, location = self.GetCurrentVersion()
        availableVersion = self.GetAvailableVersion()
        logging.debug('current version: %r, available version: %r' % (version, availableVersion['version']))
        return availableVersion['version'] > version

