import main
import os
import sys


def redirect_std():
    # we don't want nasty surprises with windows app trying to write things
    # to consoles that don't exist! or files they don't have priveleges to!
    appDataFolder = os.environ['APPDATA']
    logFolder = os.path.join(appDataFolder, 'Digital Panda')
    if not os.path.exists(logFolder):
        os.makedirs(logFolder)
    #sys.stdout = open(os.devnull, 'w')
    #sys.stderr = open(os.devnull, 'w')
    sys.stdout = open(os.path.join(logFolder, 'tray_stdout.log'), 'w')
    sys.stderr = open(os.path.join(logFolder, 'tray_stderr.log'), 'w')


if __name__ == '__main__':
    redirect_std()
    main.main()
