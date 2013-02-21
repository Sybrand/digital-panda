#!/usr/bin/python2.7
'''
Created on January 22, 2013
(Sybrand: based on code I wrote Feb 20, 2012)

@author: Sybrand Strauss
'''

import sqlite3
import config
import logging


class SyncInfo(object):
    def __init__(self, hash, dateModified):
        self._hash = hash
        self._dateModified = dateModified

    @property
    def hash(self):
        return self._hash

    @property
    def dateModified(self):
        return self._dateModified


class StateStore(object):

    def __init__(self, account):
        c = config.Config()
        self.databasePath = c.get_database_path()
        self.createDatabase()
        self.account = account

    def createDatabase(self):
        """ Create the database if it doesn't exist
        """
        #logging.debug('database path = %r' % self.databasePath)
        conn = self.getConnection()
        #conn.execute('create table if not exists container '
        #             '(path)')
        conn.execute('create table if not exists object'
                     '(account, path, hash, datemodified)')

    def getConnection(self):
        return sqlite3.connect(self.databasePath)

    def markObjectAsSynced(self, path, objectHash, dateModified):
        path = path.strip('/')
        #logging.info('mark %s with hash %s modified '
        #             '@ %s as synced' %
        #             (path, objectHash, dateModified))
        conn = self.getConnection()
        c = conn.cursor()

        t = (path,)
        c.execute('''select hash from object where path = ?''', t)
        data = c.fetchone()
        if (data is None):
            t = (self.account, path, objectHash, dateModified)
            c.execute('''insert into object
                      (account, path, hash, dateModified)
                      values (?,?,?,?)''', t)
        else:
            t = (objectHash, dateModified, path, self.account)
            c.execute('''update object set hash = ?, datemodified = ?
                      where path = ? and account = ?''', t)
        conn.commit()
        c.close()

    def getObjectSyncInfo(self, path):
        path = path.strip('/')
        conn = self.getConnection()
        c = conn.cursor()
        t = (path, self.account)
        c.execute('''select hash, datemodified from object
                  where path = ? and account = ?''', t)
        data = c.fetchone()
        c.close()
        syncInfo = None
        if data:
            syncInfo = SyncInfo(data[0], data[1])
        return syncInfo

    def removeObjectSyncRecord(self, path):
        path = path.strip('/')
        conn = self.getConnection()
        c = conn.cursor()
        t = (path, self.account)
        logging.info('removing sync info for for %s' % path)
        c.execute('delete from object where path = ? and account = ?', t)
        conn.commit()
        c.close()
