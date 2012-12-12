#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx


class SettingsPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.SIMPLE_BORDER)
        # auth url
        labelAuthUrl = wx.StaticText(self, wx.ID_ANY,
                                     'Authentication Url')
        inputAuthUrl = wx.TextCtrl(self, wx.ID_ANY,
                                   'https://store-it.mweb.co.za/v1/auth')

        labelCredentials = wx.StaticText(self, wx.ID_ANY,
                                         'Credentials:')

        # username
        labelUsername = wx.StaticText(self, wx.ID_ANY,
                                      'Username')
        inputUsername = wx.TextCtrl(self, wx.ID_ANY, '')

        # password
        labelPassword = wx.StaticText(self, wx.ID_ANY,
                                      'Password')
        inputPassword = wx.TextCtrl(self, wx.ID_ANY, '')

        # sizers
        panelSizer = wx.BoxSizer(wx.VERTICAL)
        authSizer = wx.BoxSizer(wx.HORIZONTAL)
        credentialsSizer = wx.BoxSizer(wx.HORIZONTAL)
        usernameSizer = wx.BoxSizer(wx.HORIZONTAL)
        passwordSizer = wx.BoxSizer(wx.HORIZONTAL)

        authSizer.Add(item=labelAuthUrl, proportion=0,
                      flag=wx.ALL, border=5)
        authSizer.Add(item=inputAuthUrl, proportion=1,
                      flag=wx.ALL, border=5)

        credentialsSizer.Add(item=labelCredentials, proportion=0,
                             flag=wx.ALL, border=5)

        usernameSizer.Add(item=labelUsername, proportion=0,
                          flag=wx.ALL, border=5)
        usernameSizer.Add(item=inputUsername, proportion=1,
                          flag=wx.ALL, border=5)

        passwordSizer.Add(item=labelPassword, proportion=0,
                          flag=wx.ALL, border=5)
        passwordSizer.Add(item=inputPassword, proportion=1,
                          flag=wx.ALL, border=5)

        panelSizer.Add(item=authSizer, border=0, proportion=0,
                       flag=wx.ALL | wx.EXPAND)
        panelSizer.Add(item=credentialsSizer, border=0, proportion=0,
                       flag=wx.ALL | wx.EXPAND)
        panelSizer.Add(item=usernameSizer, border=0, proportion=0,
                       flag=wx.ALL | wx.EXPAND)
        panelSizer.Add(item=passwordSizer, border=0, proportion=0,
                       flag=wx.ALL | wx.EXPAND)

        self.SetSizer(panelSizer)
        #panelSizer.Fit(parent)


class Settings(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)

        self.icon = wx.Icon('digital-panda.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize((400, 200))

        framePanel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        settingsPanel = SettingsPanel(framePanel, wx.ID_ANY)

        vbox.Add(settingsPanel, 1, wx.EXPAND | wx.ALL, 10)
        framePanel.SetSizer(vbox)
        vbox.Fit(self)
