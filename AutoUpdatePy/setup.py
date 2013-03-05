#!/usr/bin/python
'''
Created on March 05, 2013
'''
from glob import glob
from distutils.core import setup
import sys
# we need to import setuptools to allow develop mode
# on ubuntu apt-get install python-setuptools
import setuptools


if sys.platform in ['win32', 'win64', 'cygwin']:
    import py2exe

    data_files = [('gfx', glob(r'.\gfx\*.*'))]

    setup(
        windows=[{'script': 'auto_update.pyw',
                  'icon_resources': [(1, 'gfx/digital-panda-icon.ico')]}],
        data_files=data_files,
        name='Digital Panda Auto Update',
        version='0.1',
        author='Sybrand Strauss',
        author_email='sybrand.strauss@gmail.com',
        options={"py2exe": {"bundle_files": 1,
                            "dll_excludes": ["w9xpopen.exe"]}})
else:
    raise Exception('please implement me for your platform!!!')
