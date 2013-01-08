#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import taskbar
import os

def main():
    useWxTaskBarIcon = True

    if os.name == 'posix':
        # running on posix? is it ubuntu?
        import platform
        # get back a tuple: (distname, version, id)
        tuple = platform.linux_distribution('Ubuntu')
        if tuple[1]>= '12.10':
            useWxTaskBarIcon = False

    if useWxTaskBarIcon:
        provider = wx.SimpleHelpProvider()
        wx.HelpProvider_Set(provider)

        app = wx.PySimpleApp()
        taskbar.TaskBar()
        app.MainLoop()
    else:
        print('Wups - we''re trying to get Ubuntu 12.10 to work!')

if __name__ == '__main__':
    main()
