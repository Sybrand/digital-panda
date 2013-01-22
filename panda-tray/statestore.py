#!/usr/bin/python2.7
'''
Created on January 22, 2013

@author: Sybrand Strauss
'''

import sqlite3
import config
import logging


class StateStore:

    def __init__(self):
        c = config.Config()
        self.databasePath = c.get_database_path()
        logging.debug('database path = %r' % self.databasePath)
        conn = self.getConnection()
        conn.execute('create table if not exists container '
                     '(path)')
        conn.execute('create table if not exists object'
                     '(path, hash, datemodified)')

    def getConnection(self):
        return sqlite3.connect(self.databasePath)

    def markObjectAsSynced(self, path, objectHash, dateModified):
        logging.info('mark %s with hash %s modified '
                     '@ %s as synced' %
                     (path, objectHash, dateModified))
        conn = self.getConnection()
        c = conn.cursor()

        t = (path,)
        c.execute('''select hash from object where path = ?''', t)
        data = c.fetchone()
        if (data is None):
            t = (path, objectHash, dateModified)
            c.execute('''insert into object
                      (path, hash, dateModified)
                      values (?,?,?)''', t)
        else:
            t = (objectHash, dateModified, path)
            c.execute('''update object set hash = ?, datemodified = ?
                      where path = ?''', t)
        conn.commit()
        c.close()
