# oi - this class is just plain NOT working out for me...

from twisted.web.client import Agent
from twisted.web.http_headers import Headers
from twisted.internet.protocol import Protocol
from twisted.internet.defer import Deferred
from twisted.internet import reactor
import threading
import logging


class DownloadProtocol(Protocol):
    def __init__(self, finished, filename):
        self.finished = finished
        self.targetFile = open(filename, 'wb')
        self.running = True
        self.lock = threading.Lock()
        self.bytesWritten = 0

    def dataReceived(self, bytes):
        if bytes:
            self.targetFile.write(bytes)
            self.bytesWritten += len(bytes)
            #logging.info('%r' % self.bytesWritten)
        else:
            logging.info('no bytes received!')
            self.stopRunning()

    def stopRunning(self):
        self.lock.acquire()
        try:
            if self.running:
                self.running = False
                self.finished.callback(None)
        finally:
            self.lock.release()

    def connectionLost(self, reason):
        # flush and close file
        self.targetFile.flush()
        self.targetFile.close()
        self.stopRunning()

    def signalStop(self):
        logging.debug('DownloadProtocol::signalStop')
        self.stopRunning()

    def getBytesWritten(self):
        return self.bytesWritten


class Downloader(object):
    def __init__(self):
        self.running = True
        self.protocol = None
        self.lock = threading.Lock()

    def handleResponse(self, response, targetPath):
        logging.debug('Downloader::handleResponse')
        finished = Deferred()
        self.lock.acquire()
        logging.debug('handleResponse - lock acquired')
        try:
            if response.code == 200 and self.running:
                self.protocol = DownloadProtocol(finished, targetPath)
                response.deliverBody(self.protocol)
                return finished
        finally:
            self.lock.release()
        logging.debug('returning none')
        return None

    def download(self, sourcePath, targetPath, headers):
        agent = Agent(reactor)
        sourcePath = sourcePath.encode('utf-8')
        #logging.debug('going to download %r' % sourcePath)
        req = agent.request('GET',
                            sourcePath,
                            Headers(headers),
                            None)
        req.addCallback(self.handleResponse, (targetPath))
        #req.addBoth(self.shutDown)
        # we can't install signal handlers, because we don't
        # know if this is running on the main thread!
        if not reactor.running:
            logging.debug('now going to call run...')
            reactor.run(installSignalHandlers=0)
            logging.debug('done calling run')
        else:
            logging.debug('reactor already running')

    def getBytesWritten(self):
        if self.protocol:
            return self.protocol.getBytesWritten()
        return 0

    def _stop(self):
        logging.debug('Downloader::_stop')
        # this is supposed to be run in the same thread as
        # everything else, but since I don't fully
        # understand how twisted works, I'm locking just
        # to be safe
        self.lock.acquire()
        try:
            self.running = False
            if self.protocol:
                logging.debug('self.protocol.signalStop()')
                self.protocol.signalStop()
        finally:
            self.lock.release()

    def interrupt(self):
        reactor.callInThread(self._stop)
        #self._stop()

    #def shutDown(self, ignored):
        # one can't restart a reactor!
        #reactor.stop()
