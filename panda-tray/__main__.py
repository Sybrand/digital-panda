#!/usr/bin/python2.7
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import taskbar


def main():
    provider = wx.SimpleHelpProvider()
    wx.HelpProvider_Set(provider)

    app = wx.PySimpleApp()
    taskbar.TaskBar()
    app.MainLoop()

if __name__ == '__main__':
    main()
