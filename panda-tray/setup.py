#!/usr/bin/python
'''
Created on Feb 23, 2012

@author: sstrau

1) download and install py2exe from http://sourceforge.net/projects/py2exe
2) run python setup.py py2exe
'''

#import os
import sys
#from esky.bdist_esky import Executable
#from esky import bdist_esky
from glob import glob
#import version

"""
image_files = []
for files in os.listdir('gfx/'):
    f1 = 'gfx/' + files
    if os.path.isfile(f1):
        f2 = 'images', [f1]
        image_files.append(f2)"""

# for windows
if sys.platform in ['win32', 'win64', 'cygwin']:
    import py2exe
    from distutils.core import setup

    data_files = [('gfx', glob(r'.\gfx\*.*'))]

    #a = Executable('panda-tray-w.pyw')
    #scripts = ['panda-tray-w.pyw']

    setup(
        windows=[{'script': 'panda-tray-w.pyw',
                  'icon_resources': [(1, 'gfx/digital-panda-icon.ico')]}],
        data_files=data_files,
        options={"py2exe": {"ignores": ["gtk", "appindicator", "Carbon",
                                        "Carbon.Files", "_scproxy", "bsdiff",
                                        "bsdiff4", "build_panda"],
                            "bundle_files": "1",
                            "dll_excludes": ["w9xpopen.exe"]}}
    )

    '''
        data_files=data_files,
        name='Digital Panda Tray Application',
        version=version.version,
        scripts=[Executable(script='panda-tray-w.pyw',
                            icon='gfx/digital-panda-icon.ico',
                            gui_only=True,)],
        #options={'bdist_esky': {'freezer_module': 'py2exe'}}'''
# right now only dealing with windows
else:
    raise Exception('please implement me for your platform!!!')

"""windows=[
            {
                'script': 'panda-tray-w.py',
                'icon_resources': [(1, 'gfx/digital-panda-icon.ico')]
            }
        ],"""
