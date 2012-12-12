#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx


class PandaMenu(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent=parent, id=id, title=title,
                          pos=wx.DefaultPosition, style=wx.FRAME_NO_TASKBAR)

        self.SetMinSize((400, 200))

        framePanel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        settingsButton = wx.Button(self, -1, 'Settings...')
        vbox.Add(item=settingsButton, proportion=0, flag=wx.ALL, border=1)

        framePanel.SetSizer(vbox)
        vbox.Fit(self)
