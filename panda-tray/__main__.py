#!/usr/bin/python
import wx
import taskbar


def main():
    app = wx.PySimpleApp()
    taskbar.TaskBar()
    app.MainLoop()

if __name__ == '__main__':
    main()
