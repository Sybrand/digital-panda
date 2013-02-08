# digital-panda

Cloud storage client - the endgoal is to have a tray application that syncs your local files into the cloud.

Target cloud solutions to begin with are: Swift (Openstack) and Amazon S3

## License

This Software is licensed under the MIT License (MIT), please refer to LICENSE for details

## How to run

Currently runs on Windows 7
With a little work/luck it might run on Ubuntu 12.04

There's not much to see right now... especially if you don't have a swift server to connect to!

## Milestones

* TODO: refactor panda-commander into own project
* TODO: refactor panda-daemon into own project
* TODO: port panda-daemon to Python 3
* (busy implementing tray client)
* (busy implementing) Classic commander style interface (left pane local file structure, right page remote file structure)
* (busy implementing) Rackspace - OpenStack Swift integration
* (next step) Amazon - S3 integration 
* Synchronization capabilities - e.g. "sync folder"
* Configuration GUI
* Minimal GUI that does syncing in background

## Dependancies

python (ubuntu: 2.7, windows 2.7 32bit (64 bit is an issue, because of WinSparkle))

python-wx (for ubuntu: apt-get install python-wxgtk2.8, for windows: wxPython2.8-win32-unicode-2.8.12.1-py27.exe)

setuptools (for ubunutu: should just work, for windows: http://pypi.python.org/pypi/setuptools)

install the digitalpanda module (python setup.py develop)

install py2exe

install esky (https://github.com/cloudmatrix/esky)

using innosetup for installer (windows)

## Known issues
Panda-Tray:
- In settings dialog, Apply doesn't disable after clicking cancel
- Tabbing in settings dialog doesn't work right (not jumping to buttons after text)
- In settings dialog, first textbox should be selected by default
- Event handling is just bloody crazy right now! Need to refactor UI code
- Downloads don't resume - doesn't show upload/download status
- Quitting the panda - background downloads keep going
- Not working with Unity on Ubuntu
- Password is being stored in clear text!
- Installer fails if already installed and running
- If you quit the panda - while it's upgrading - it keeps running in the background until
	the upgrade is complete. If you try to start up the panda while it's upgrading, it
	won't start. You have to wait until the update is complete, and then start the panda.
	That's a silly yourney - the users shouldn't have to worry about that!
- If you delete the local directory, but have placed new files in that directory remotely,
	then the remote files get removed. Appropriate action would be to retain files that
	have not been downloaded yet, by downloading them - and retaining directory structure as
	far as is valid
- The setup program isn't signed - so Windows 8 complains
- The autoupdate feature, on Windows 8 requires promping to complete
- On first run, on windows 8, security issue causes prompting


## Missing features
Panda-Tray:
- Cool feature would be to open digital panda folder, if you click on the digital panda icon, when digital panda is already running in the tray.
- Favourites (link to digital panda should be added)
- I think the panda should ask before updating - but that can wait until we have something more stable
- Status updates (downloading, uploading etc.)
- Look if there's a better way to detect online changes than iterating through everything
