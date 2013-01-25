#!/usr/bin/python
'''
Created on Feb 23, 2012

@author: sstrau

1) download and install py2exe from http://sourceforge.net/projects/py2exe
2) run python setup.py py2exe
'''

import sys
from esky.bdist_esky import Executable
from esky import bdist_esky
from glob import glob

# for windows
if sys.platform in ['win32', 'win64', 'cygwin']:
    import py2exe
    from distutils.core import setup

    data_files = [('gfx', glob(r'.\gfx\*.*'))]

    #a = Executable('panda-tray-w.pyw')
    #scripts = ['panda-tray-w.pyw']

    setup(
        data_files=data_files,
        name='Digital Panda Tray Application',
        version="0.4",
        scripts=[Executable(script='panda-tray-w.pyw',
                            icon='gfx/digital-panda-icon.ico',
                            gui_only=True,)],
        options={'bdist_esky': {'freezer_module': 'py2exe'}}
    )
# right now only dealing with windows
else:
    raise Exception('please implement me for your platform!!!')

"""windows=[
            {
                'script': 'panda-tray-w.py',
                'icon_resources': [(1, 'gfx/digital-panda-icon.ico')]
            }
        ],"""
