# digital-panda

Cloud storage client - the endgoal is to have a tray application that syncs your local files into the cloud.

Target cloud solutions to begin with are: Swift (Openstack) and Amazon S3

## License

This Software is licensed under the MIT License (MIT), please refer to LICENSE for details

## How to run

Currently runs on Ubuntu 12.04 - but should work on any OS with the correct dependancies installed.

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

python-wx (for ubuntu: apt-get install python-wxgtk2.8)

## Known issues
Panda-Tray:
- In settings dialog, Apply doesn't disable after clicking cancel
- Tabbing in settings dialog doesn't work right (not jumping to buttons after text)
- In settings dialog, first textbox should be selected by default
- On tray menu, the panda looks like it's crying!
- Event handling is just bloody crazy right now!
- Something is causing a freeze on startup - no idea what!
