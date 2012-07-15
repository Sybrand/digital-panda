# digital-panda

Cloud storage client - the endgoal is to have a tray application that syncs your local files into the cloud.

Target cloud solutions to begin with are: Swift (Openstack) and Amazon S3

## License

This Software is licensed under the MIT License (MIT), please refer to LICENSE for details

## How to run

Currently runs on Ubuntu 12.04 - but should work on any OS with the correct dependancies installed.

There's not much to see right now...

## Milestones

* (busy implementing) Classic commander style interface (left pane local file structure, right page remote file structure)
* (busy implementing) Rackspace - OpenStack Swift integration
* (next step) Amazon - S3 integration 
* Synchronization capabilities - e.g. "sync folder"
* Configuration GUI
* Minimal GUI that does syncing in background

## Dependancies

python-wx (for ubunut: apt-get install python-wxgtk2.8)