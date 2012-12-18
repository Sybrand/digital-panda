#!/usr/bin/python
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
