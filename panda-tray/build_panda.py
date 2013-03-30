import hashlib
import sys
import os
import version
import json


def get_file_hash(filename):
    md5 = hashlib.md5()
    with open(filename, 'rb') as f:
        while True:
            data = f.read(1048576)
            if not data:
                break
            md5.update(data)
    return md5.hexdigest()


def get_file_size(filename):
    return os.path.getsize(filename)


def make_version():
    distPath = os.path.join('dist', 'win7_32.txt')
    if os.path.exists(distPath):
        os.remove(distPath)
    zipfileName = ('Digital Panda Tray Application-%s.win32.zip' %
                   (version.version))
    zipfile = os.path.join('dist', zipfileName)
    location = '/updates/%s' % zipfile
    fd = open(distPath, 'w')
    data = json.dumps({'version': float(version.version),
                       'protocol': 'http',
                       'host': 'www.digitalpanda.co.za',
                       'location': location,
                       'hash': get_file_hash(zipfile),
                       'fileSize': os.path.getsize(zipfile)})
    fd.write(data)
    fd.flush()
    fd.close()


if __name__ == '__main__':
    if sys.argv[1] == 'hash':
        print get_file_hash(sys.argv[2])
    elif sys.argv[1] == 'filesize':
        print get_file_size(sys.argv[2])
    elif sys.argv[1] == 'version':
        make_version()
