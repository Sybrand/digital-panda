'''
Created on January 25, 2013

@author: Sybrand Strauss

entry point for windows executable
'''

import sys
import config
import os
import main
import logging


def redirect_std(logFileFolder):
    # we don't want nasty surprises with windows app trying to write things
    # to consoles that don't exist! or files they don't have priveleges to!
    sys.stdout = open(os.path.join(logFileFolder, 'tray_stdout.log'), 'w')
    sys.stderr = open(os.path.join(logFileFolder, 'tray_stderr.log'), 'w')

if __name__ == '__main__':
    c = config.Config()
    logFileFolder = c.get_log_file_folder()
    redirect_std(logFileFolder)
    logging.basicConfig(filename=c.get_log_file_name(), level=logging.DEBUG)
    print('exe starting in: %s' % os.getcwd())
    main.main()
