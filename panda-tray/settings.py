#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx


class StatusPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)
        #self.SetBackgroundColour((255, 0, 0))

        labelStatus = wx.StaticText(self, wx.ID_ANY,
                                    'Status: Online', style=wx.ALIGN_RIGHT)

        image = wx.Image('digital-panda-online-1616.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        position = (0, 0)
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        staticBitmap = wx.StaticBitmap(self, -1, bitmap, position, size)

        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(item=labelStatus, proportion=1,
                       flag=wx.ALL | wx.EXPAND, border=5)
        panelSizer.Add(item=staticBitmap, proportion=0,
                       flag=wx.ALL, border=5)
        self.SetSizer(panelSizer)


class LogoPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.SIMPLE_BORDER)
        self.SetBackgroundColour((0, 255, 0))

        image = wx.Image('digital-panda-header.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        position = (0, 0)
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        staticBitmap = wx.StaticBitmap(self, -1,
                                       bitmap, position, size)
        #self.SetSize(size)

        logoLabel = wx.StaticText(self, wx.ID_ANY,
                                  'Digital Panda')
        font = wx.Font(pointSize=20, family=wx.FONTFAMILY_DEFAULT,
                       style=wx.FONTSTYLE_NORMAL,
                       weight=wx.FONTWEIGHT_BOLD)
        logoLabel.SetFont(font)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(item=staticBitmap, proportion=0,
                 flag=wx.LEFT, border=0)
        hbox.Add(item=logoLabel, proportion=0,
                 flag=wx.ALL, border=5)
        self.SetSizer(hbox)


class TestConnectionPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        testButton = wx.Button(self, -1, 'Test now')

        image = wx.Image('connection-ok.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        position = (0, 0)
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        staticBitmap = wx.StaticBitmap(self, -1,
                                       bitmap, position, size)

        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(item=testButton, proportion=0,
                       flag=wx.ALL, border=5)
        panelSizer.Add(item=staticBitmap, proportion=0,
                       flag=wx.ALL, border=5)
        self.SetSizer(panelSizer)


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
        inputPassword = wx.TextCtrl(self, wx.ID_ANY, '',
                                    style=wx.TE_PASSWORD)

        # test
        testConnectionPanel = TestConnectionPanel(self, -1)

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
        panelSizer.Add(item=testConnectionPanel, border=0, proportion=0,
                       flag=wx.ALL | wx.EXPAND)

        self.SetSizer(panelSizer)
        #panelSizer.Fit(parent)


class Settings(wx.Frame):
    def __init__(self, parent, id, title):
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition)

        self.icon = wx.Icon('digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize((400, 200))

        framePanel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        logoPanel = LogoPanel(framePanel, wx.ID_ANY)

        midPanel = wx.Panel(framePanel)
        midPanelSizer = wx.BoxSizer(wx.VERTICAL)
        labelEditYourSettings = wx.StaticText(midPanel, wx.ID_ANY,
                                              'Edit your settings')
        midPanelSizer.Add(item=labelEditYourSettings, border=5,
                          proportion=0,
                          flag=wx.ALL | wx.EXPAND)
        midPanel.SetSizer(midPanelSizer)

        settingsPanel = SettingsPanel(framePanel, wx.ID_ANY)

        statusPanel = StatusPanel(framePanel, wx.ID_ANY)

        vbox.Add(logoPanel, border=0, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        vbox.Add(midPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        vbox.Add(settingsPanel, proportion=1, flag=wx.EXPAND | wx.ALL,
                 border=10)
        vbox.Add(statusPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        framePanel.SetSizer(vbox)
        vbox.Fit(self)
