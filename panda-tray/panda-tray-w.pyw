import sys
import config
import os
import main

if __name__ == '__main__':
    c = config.Config()
    logFileFolder = c.get_log_file_folder()
    sys.stdout = open(os.path.join(logFileFolder, 'tray_stdout.log'), 'w')
    sys.stderr = open(os.path.join(logFileFolder, 'tray_stderr.log'), 'w')
    print('exe starting in: %s' % os.getcwd())
    main.main()
