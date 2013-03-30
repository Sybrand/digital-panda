# digital-panda

Cloud storage client - the endgoal is to have a tray application that syncs your local files into the cloud.

Target cloud solutions to begin with are: Swift (Openstack) and Amazon S3

## License

This Software is licensed under the MIT License (MIT), please refer to LICENSE for details

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

## How to run

Currently runs on Windows 7

python (ubuntu: 2.7, windows 2.7 32bit (using 32 bit for now, it being the lowest common denominator))

python-wx (for ubuntu: apt-get install python-wxgtk2.8, for windows: wxPython2.8-win32-unicode-2.8.12.1-py27.exe)

setuptools
- ubuntu:
    sudo apt-get install python-setuptools
- windows:
    http://pypi.python.org/pypi/setuptools download and run setuptools-0.6c11.win32-py2.7.exe
    add C:\Python27\Scripts to path for easy_install to work

install the digitalpanda module
    go to ./digitalpanda
    sudo python setup.py develop

install the autoupdate module
    go to ./AutoUpdatePy
    sudo python setup.py develop

install py2exe (windows only
py2exe-0.6.9.win32-py2.7.exe

install pywin (windows only)
pywin32-218.win32-py2.7.exe

using innosetup for installer (windows)

install send2trash
    go to ./3rdparty/Send2Trash-1.2.0
    sudo python setup.py install

install zope: in 3rdparty\win32 run: easy_install zope.interface-4.0.3-py2.7-win32.egg (for windows only)

// install twisted - Twisted-12.3.0.win32-py2.7.msi (decided not to use it for now!) doesn't make things that much simpler at all!

install pyOpenSSL
 - ubuntu: ?
 - windows: easy_install pyOpenSSL-0.11-py2.7-win32.egg

 you are now ready to run the app!
 go to ./panda-tray
 python dev.py

## How to build an update

### Create exe
in ./panda-tray, run build.bat
### Sign exe
This can only be done if you have the correct certificate, on a computer that's allowed to create the certificate.

in ./panda-tray, run build.bat sign

### Create dist file
./panda-tray, run build.bat distfile


## Fonts

Original artwork used Bauhaus Medium and light; There are free alternatives that are close, but not the same - ttd-radisnoir and fonts-confortaa are free on ubuntu.

## Design Decisions

### The "Trash" Container
We could have a Trash folder in every container, I've opted for one Trash container.
Seems like a better idea, than having tons of Trash folders all over the place.
