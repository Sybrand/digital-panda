import hashlib
import sys
import os
import version
import json
import shutil

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

def get_dist_filename():
    return 'win7_32.txt'

def get_dist_path():
    return os.path.join('dist', get_dist_filename())

def get_zip_file_name():
    return ('Digital Panda Tray Application-%s.win32.zip' %
                   (version.version))

def make_version():
    distPath = get_dist_path()
    if os.path.exists(distPath):
        os.remove(distPath)
    zipfile = os.path.join('dist', get_zip_file_name())
    location = '/update/%s' % get_zip_file_name()
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

def deploy_local():
    tmpPath = 'c:\\temp\\digitalpanda\\build'
    shutil.copy(get_dist_path(), os.path.join(tmpPath, get_dist_filename()))
    shutil.copy(os.path.join('dist', get_zip_file_name()), os.path.join(tmpPath, get_zip_file_name()))


if __name__ == '__main__':
    if sys.argv[1] == 'hash':
        print get_file_hash(sys.argv[2])
    elif sys.argv[1] == 'filesize':
        print get_file_size(sys.argv[2])
    elif sys.argv[1] == 'version':
        make_version()
    elif sys.argv[1] == 'deploy_local':
        deploy_local()
