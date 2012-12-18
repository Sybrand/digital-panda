#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import wx.lib.newevent

ApplyEvent, EVT_APPLY = wx.lib.newevent.NewEvent()
OkEvent, EVT_OK = wx.lib.newevent.NewEvent()
CancelEvent, EVT_CANCEL = wx.lib.newevent.NewEvent()


class StatusPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        labelStatus = wx.StaticText(self, wx.ID_ANY,
                                    'Status: Online', style=wx.ALIGN_RIGHT)

        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(item=labelStatus, proportion=1,
                       flag=wx.ALL | wx.EXPAND, border=5)

        self.SetSizer(panelSizer)


class LogoPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)
        self.SetBackgroundColour((0, 255, 0))

        image = wx.Image('gfx/digital-panda-header.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        position = (0, 0)
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        staticBitmap = wx.StaticBitmap(self, -1,
                                       bitmap, position, size)

        hbox = wx.BoxSizer(wx.HORIZONTAL)
        hbox.Add(item=staticBitmap, proportion=0,
                 flag=wx.LEFT, border=0)

        self.SetSizer(hbox)


class TestConnectionPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        testButton = wx.Button(self, -1, 'Test now')

        image = wx.Image('gfx/connection-ok.png', wx.BITMAP_TYPE_ANY)
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


class HelpPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        #text = wx.StaticText(self, wx.ID_ANY, 'Help')
        url = 'http://www.digitalpanda.co.za/help.php'
        text = wx.HyperlinkCtrl(self, wx.ID_ANY, 'Help', url)

        sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(item=text, proportion=0,
                  flag=wx.ALL, border=5)
        self.SetSizer(sizer)


class OkCancelApply(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)
        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        btnOk = wx.Button(self, -1, 'Ok')
        btnOk.Bind(wx.EVT_BUTTON, self.OnOk)
        sizer.Add(item=btnOk, proportion=0,
                  flag=wx.ALL, border=2)

        btnCancel = wx.Button(self, -1, 'Cancel')
        btnCancel.Bind(wx.EVT_BUTTON, self.OnCancel)
        sizer.Add(item=btnCancel, proportion=0,
                  flag=wx.ALL, border=2)

        self.btnApply = wx.Button(self, -1, 'Apply')
        self.btnApply.Disable()
        self.btnApply.Bind(wx.EVT_BUTTON, self.OnApply)
        sizer.Add(item=self.btnApply, proportion=0,
                  flag=wx.ALL, border=2)

        self.SetSizer(sizer)

    def OnCancel(self, event):
        event = CancelEvent()
        wx.PostEvent(self.parent, event)

    def OnOk(self, event):
        event = OkEvent()
        wx.PostEvent(self.parent, event)

    def OnApply(self, event):
        event = ApplyEvent()
        wx.PostEvent(self.parent, event)

    def EnableApply(self):
        self.btnApply.Enable()

    def DisableApply(self):
        self.btnApply.Disable()


class BottomPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)
        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        help = HelpPanel(self, wx.ID_ANY)
        sizer.Add(item=help, proportion=0,
                  flag=wx.ALL, border=5)

        spacer = wx.Panel(self, wx.ID_ANY)
        sizer.Add(item=spacer, proportion=1,
                  flag=wx.ALL, border=0)

        okCancelApply = OkCancelApply(self, wx.RIGHT)
        sizer.Add(item=okCancelApply, proportion=0,
                  flag=wx.ALL, border=5)
        self.Bind(EVT_OK, self.HandleEvent)
        self.Bind(EVT_CANCEL, self.HandleEvent)
        self.Bind(EVT_APPLY, self.HandleEvent)

        """
        status = StatusPanel(self, wx.ID_ANY)
        sizer.Add(item=status, proportion=1,
                  flag=wx.ALL, border=5)"""

        self.SetSizer(sizer)

    def HandleEvent(self, event):
        print "handle event"
        wx.PostEvent(self.parent, event)


class SettingsPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        self.SetHelpText('This is a panel')

        #sizer = wx.FlexGridSizer(1, 2)
        sizer = wx.GridBagSizer(vgap=5, hgap=5)

        # auth url
        # using "Auth Url - is waaaay too technical - so instead
        # - using server"
        tipText = 'Authentication URL for your cloud ' \
                  'storage provider'
        labelAuthUrl = wx.StaticText(self, wx.ID_ANY,
                                     'Server')
        inputAuthUrl = wx.TextCtrl(self, wx.ID_ANY,
                                   'https://store-it.mweb.co.za/v1/auth')
        inputAuthUrl.SetHelpText(tipText)
        inputAuthUrl.SetToolTip(wx.ToolTip(tipText))
        labelAuthUrl.SetToolTip(wx.ToolTip(tipText))

        # username
        tipText = 'Cloud storage account user'
        labelUsername = wx.StaticText(self, wx.ID_ANY,
                                      'Username')
        inputUsername = wx.TextCtrl(self, wx.ID_ANY, '')
        inputUsername.SetHelpText(tipText)
        inputUsername.SetToolTip(wx.ToolTip(tipText))
        labelUsername.SetToolTip(wx.ToolTip(tipText))

        # password
        tipText = 'Cloud storage account password'
        labelPassword = wx.StaticText(self, wx.ID_ANY,
                                      'Password')
        inputAuthUrl.SetHelpText('''Password''')
        inputPassword = wx.TextCtrl(self, wx.ID_ANY, '',
                                    style=wx.TE_PASSWORD)
        labelPassword.SetToolTip(wx.ToolTip(tipText))
        inputPassword.SetToolTip(wx.ToolTip(tipText))

        sizer.AddGrowableCol(1)
        sizer.Add(item=labelAuthUrl, flag=wx.EXPAND | wx.TOP,
                  pos=(0, 0), border=5)
        sizer.Add(item=inputAuthUrl, flag=wx.EXPAND, pos=(0, 1))
        sizer.Add(item=labelUsername, flag=wx.EXPAND | wx.TOP,
                  pos=(1, 0), border=5)
        sizer.Add(item=inputUsername, flag=wx.EXPAND, pos=(1, 1))
        sizer.Add(item=labelPassword, flag=wx.EXPAND | wx.TOP,
                  pos=(2, 0), border=5)
        sizer.Add(item=inputPassword, flag=wx.EXPAND, pos=(2, 1))

        self.SetSizer(sizer)


class Settings(wx.Frame):
    def __init__(self, parent, id, title):
        # we don't want the user to be able to resize - since it's a very
        # basic menu - so we build up the style ourselves
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
                          style=wx.CLOSE_BOX | wx.SYSTEM_MENU |
                          wx.CAPTION | wx.WS_EX_CONTEXTHELP)
        self.SetExtraStyle(wx.FRAME_EX_CONTEXTHELP)

        self.icon = wx.Icon('gfx/digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize((400, 200))

        framePanel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        logoPanel = LogoPanel(framePanel, wx.ID_ANY)

        midPanel = wx.Panel(framePanel)
        midPanelSizer = wx.BoxSizer(wx.VERTICAL)
        midPanel.SetSizer(midPanelSizer)

        settingsPanel = SettingsPanel(framePanel, wx.ID_ANY)

        #statusPanel = StatusPanel(framePanel, wx.ID_ANY)

        vbox.Add(logoPanel, border=0, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        vbox.Add(midPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        #vbox.Add(line, border=10, proportion=0,
        #         flag=wx.EXPAND | wx.ALL)
        vbox.Add(settingsPanel, proportion=1, flag=wx.EXPAND | wx.ALL,
                 border=10)

        statusPanel = StatusPanel(framePanel, wx.ID_ANY)
        vbox.Add(statusPanel, proportion=0, flag=wx.EXPAND | wx.RIGHT,
                 border=5)

        """
        testConnectionPanel = TestConnectionPanel(framePanel, wx.ID_ANY)
        vbox.Add(testConnectionPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)"""

        #bottomPanel = StatusPanel(framePanel, wx.ID_ANY)
        bottomPanel = BottomPanel(framePanel, wx.ID_ANY)
        bottomPanel.Bind(EVT_APPLY, self.HandleApply)
        bottomPanel.Bind(EVT_OK, self.HandleOk)
        bottomPanel.Bind(EVT_CANCEL, self.HandleCancel)
        #bottomPanel = OkCancelApply(framePanel, wx.ID_ANY)
        #bottomPanel = HelpPanel(framePanel, wx.ID_ANY)
        vbox.Add(bottomPanel, border=0, proportion=0,
                 flag=wx.EXPAND | wx.ALL)

        framePanel.SetSizer(vbox)
        vbox.Fit(self)

    def HandleOk(self, event):
        self.Show(False)

    def HandleCancel(self, event):
        self.Show(False)

    def HandleApply(self, event):
        pass
