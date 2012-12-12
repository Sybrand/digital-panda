#!/usr/bin/python
'''
Created on Feb 23, 2012

@author: sstrau

1) download and install py2exe from http://sourceforge.net/projects/py2exe
2) run python setup.py py2exe
'''

from distutils.core import setup

import py2exe

setup(windows=['__main__.py'])
