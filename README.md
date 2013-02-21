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
* Consider refactoring to using Twisted http://twistedmatrix.com/trac/
* Refactor upload/download decision making (generate a list of actions, apply actions)

## Dependancies

python (ubuntu: 2.7, windows 2.7 32bit (64 bit is an issue, because of WinSparkle))

python-wx (for ubuntu: apt-get install python-wxgtk2.8, for windows: wxPython2.8-win32-unicode-2.8.12.1-py27.exe)

setuptools (for ubunutu: should just work, for windows: http://pypi.python.org/pypi/setuptools)

install the digitalpanda module (python setup.py develop)

install py2exe

install esky (https://github.com/cloudmatrix/esky)

using innosetup for installer (windows)

install send2trash (in 3rdparty\Send2Trash-1.2.0 run python setup.py install)

install zope easy_install zope.interface-4.0.3-py2.7-win32.egg

install twisted - Twisted-12.3.0.win32-py2.7.msi

install pyOpenSSL - easy_install pyOpenSSL-0.11-py2.7-win32.egg

## Fonts

Original artwork used Bauhaus Medium and light; There are free alternatives that are close, but not the same - ttd-radisnoir and fonts-confortaa are free on ubuntu.

## Design Decisions

### The "Trash" Container
We could have a Trash folder in every containter, I've opted for one Trash container.
Seems like a better idea, than having tons of Trash folders all over the place.
