#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss

known issues:
1) apply button: after clicking cancel, the apply button remains
    enabled. what should happen, is that the default settings
    should be reloaded, and apply should be disabled
'''
import wx
import wx.lib.newevent
import config
import messages

ApplyEvent, EVT_APPLY = wx.lib.newevent.NewEvent()
OkEvent, EVT_OK = wx.lib.newevent.NewEvent()
CancelEvent, EVT_CANCEL = wx.lib.newevent.NewEvent()
SettingsChanged, EVT_SETTINGS = wx.lib.newevent.NewEvent()


class StatusPanel(wx.Panel):
    """ Panel that shows the current status of the sync app

    """

    def __init__(self, parent, id, status):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER)

        self.labelStatus = wx.StaticText(self, wx.ID_ANY,
                                         'Status: %s' % status,
                                         style=wx.ALIGN_RIGHT |
                                         wx.ST_NO_AUTORESIZE)

        panelSizer = wx.BoxSizer(wx.HORIZONTAL)
        panelSizer.Add(item=self.labelStatus, proportion=1,
                       flag=wx.ALL | wx.EXPAND, border=5)

        self.SetSizer(panelSizer)

    def set_status(self, status):
        self.status = status
        self.labelStatus.SetLabel('Status: %s' % status)


class LogoPanel(wx.Panel):
    """ Panel that shows the logo of the sync app

    """
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
    """ Panel that can be used to test a connection

    """
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
    """ Panel that contains help link

    """
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
    """ Panel that contains the Ok, Cancel and Apply buttons

    """

    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER | wx.TAB_TRAVERSAL)
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

    def OnEnableApply(self, event):
        print "OnEnableApply"
        self.EnableApply()

    def EnableApply(self):
        self.btnApply.Enable()

    def DisableApply(self):
        self.btnApply.Disable()


class BottomPanel(wx.Panel):
    """ Unimagintively named panel that sits at the bottom of the dialog
    It houses the help panel, apply, ok and cancel

    """
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER | wx.TAB_TRAVERSAL)
        self.parent = parent

        sizer = wx.BoxSizer(wx.HORIZONTAL)

        help = HelpPanel(self, wx.ID_ANY)
        sizer.Add(item=help, proportion=0,
                  flag=wx.ALL, border=5)

        spacer = wx.Panel(self, wx.ID_ANY)
        sizer.Add(item=spacer, proportion=1,
                  flag=wx.ALL, border=0)

        self.okCancelApply = OkCancelApply(self, wx.RIGHT)
        sizer.Add(item=self.okCancelApply, proportion=0,
                  flag=wx.ALL, border=5)
        self.Bind(EVT_OK, self.HandleEvent)
        self.Bind(EVT_CANCEL, self.HandleEvent)
        self.Bind(EVT_APPLY, self.HandleEvent)

        self.SetSizer(sizer)

    def HandleEvent(self, event):
        print "handle event"
        wx.PostEvent(self.parent, event)


class SettingsPanel(wx.Panel):
    """ Panel that houses all the widgets for changing settings
    Username, password, auth url

    """
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.NO_BORDER | wx.TAB_TRAVERSAL)

        self.parent = parent

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
        self.inputAuthUrl = wx.TextCtrl(self, wx.ID_ANY)
        # if the server is changed - we need to handle it
        self.inputAuthUrl.SetHelpText(tipText)
        self.inputAuthUrl.SetToolTip(wx.ToolTip(tipText))
        labelAuthUrl.SetToolTip(wx.ToolTip(tipText))

        appConfig = config.Config()
        # username
        tipText = 'Cloud storage account user'
        labelUsername = wx.StaticText(self, wx.ID_ANY,
                                      'Username')
        self.inputUsername = wx.TextCtrl(self, wx.ID_ANY, '')
        self.inputUsername.SetHelpText(tipText)
        self.inputUsername.SetValue(appConfig.username)
        self.inputUsername.SetToolTip(wx.ToolTip(tipText))
        labelUsername.SetToolTip(wx.ToolTip(tipText))

        # password
        tipText = 'Cloud storage account password'
        labelPassword = wx.StaticText(self, wx.ID_ANY,
                                      'Password')
        labelPassword.SetHelpText('''Password''')
        self.inputPassword = wx.TextCtrl(self, wx.ID_ANY,
                                         appConfig.password,
                                         style=wx.TE_PASSWORD)
        labelPassword.SetToolTip(wx.ToolTip(tipText))
        self.inputPassword.SetToolTip(wx.ToolTip(tipText))

        self.SetDefaultValues()
        self.BindHandleTextChanged()

        sizer.AddGrowableCol(1)
        sizer.Add(item=labelAuthUrl, flag=wx.EXPAND | wx.TOP,
                  pos=(0, 0), border=5)
        sizer.Add(item=self.inputAuthUrl, flag=wx.EXPAND, pos=(0, 1))
        sizer.Add(item=labelUsername, flag=wx.EXPAND | wx.TOP,
                  pos=(1, 0), border=5)
        sizer.Add(item=self.inputUsername, flag=wx.EXPAND, pos=(1, 1))
        sizer.Add(item=labelPassword, flag=wx.EXPAND | wx.TOP,
                  pos=(2, 0), border=5)
        sizer.Add(item=self.inputPassword, flag=wx.EXPAND, pos=(2, 1))

        self.SetSizer(sizer)

    def GetUserName(self):
        return self.inputUsername.GetValue()

    def GetUrl(self):
        return self.inputAuthUrl.GetValue()

    def GetPassword(self):
        return self.inputPassword.GetValue()

    def BindHandleTextChanged(self):
        self.inputPassword.Bind(wx.EVT_TEXT, self.HandleTextChange)
        self.inputAuthUrl.Bind(wx.EVT_TEXT, self.HandleTextChange)
        self.inputUsername.Bind(wx.EVT_TEXT, self.HandleTextChange)

    def HandleTextChange(self, event):
        event = SettingsChanged()
        wx.PostEvent(self, event)

    def SetDefaultValues(self):
        print("setting default values")
        appConfig = config.Config()
        self.inputAuthUrl.SetValue(appConfig.get_authUrl())


class Settings(wx.Frame):
    """ The frame that pops up when you click settings
    """

    def __init__(self, parent, id, title, status, outputQueue):
        # we don't want the user to be able to resize - since it's a very
        # basic menu - so we build up the style ourselves
        wx.Frame.__init__(self, parent, id, title, wx.DefaultPosition,
                          style=wx.CLOSE_BOX | wx.SYSTEM_MENU |
                          wx.CAPTION | wx.WS_EX_CONTEXTHELP | wx.TAB_TRAVERSAL)
        self.SetExtraStyle(wx.FRAME_EX_CONTEXTHELP)
        self.outputQueue = outputQueue

        self.icon = wx.Icon('gfx/digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(self.icon)
        self.SetMinSize((400, 200))

        framePanel = wx.Panel(self)

        vbox = wx.BoxSizer(wx.VERTICAL)

        logoPanel = LogoPanel(framePanel, wx.ID_ANY)

        midPanel = wx.Panel(framePanel)
        midPanelSizer = wx.BoxSizer(wx.VERTICAL)
        midPanel.SetSizer(midPanelSizer)

        self.settingsPanel = SettingsPanel(framePanel, wx.ID_ANY)

        #statusPanel = StatusPanel(framePanel, wx.ID_ANY)

        vbox.Add(logoPanel, border=0, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        vbox.Add(midPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)
        #vbox.Add(line, border=10, proportion=0,
        #         flag=wx.EXPAND | wx.ALL)
        vbox.Add(self.settingsPanel, proportion=1, flag=wx.EXPAND | wx.ALL,
                 border=10)

        self.statusPanel = StatusPanel(framePanel, wx.ID_ANY, status)
        vbox.Add(self.statusPanel, proportion=0, flag=wx.EXPAND | wx.RIGHT,
                 border=5)

        """
        testConnectionPanel = TestConnectionPanel(framePanel, wx.ID_ANY)
        vbox.Add(testConnectionPanel, border=5, proportion=0,
                 flag=wx.EXPAND | wx.ALL)"""

        #bottomPanel = StatusPanel(framePanel, wx.ID_ANY)
        self.bottomPanel = BottomPanel(framePanel, wx.ID_ANY)
        self.bottomPanel.Bind(EVT_APPLY, self.HandleApply)
        self.bottomPanel.Bind(EVT_OK, self.HandleOk)
        self.bottomPanel.Bind(EVT_CANCEL, self.HandleCancel)
        #bottomPanel = OkCancelApply(framePanel, wx.ID_ANY)
        #bottomPanel = HelpPanel(framePanel, wx.ID_ANY)
        vbox.Add(self.bottomPanel, border=0, proportion=0,
                 flag=wx.EXPAND | wx.ALL)

        # this is probably a very ugly way of binding things together!
        # need to replace this with a pretier way of doing things
        # if this control changes, or get's re-factored, stringing
        # things toghether like this is going to be a nightmare!
        self.settingsPanel.Bind(EVT_SETTINGS, self.HandleSettings)
        self.parent = parent

        framePanel.SetSizer(vbox)
        vbox.Fit(self)

    def SetStatus(self, status):
        self.statusPanel.set_status(status)

    def HandleSettings(self, event):
        print("settings changed!")
        self.bottomPanel.okCancelApply.EnableApply()

    def HandleOk(self, event):
        self.Show(False)
        self.bottomPanel.okCancelApply.DisableApply()
        self.SaveSettings()

    def HandleCancel(self, event):
        self.Show(False)
        # reset the default values
        self.settingsPanel.SetDefaultValues()
        print("going to disable apply")
        self.bottomPanel.okCancelApply.DisableApply()

    def HandleApply(self, event):
        self.bottomPanel.okCancelApply.DisableApply()
        self.SaveSettings()

    def SaveSettings(self):
        # change config
        appConfig = config.Config()
        appConfig.username = self.settingsPanel.GetUserName()
        appConfig.password = self.settingsPanel.GetPassword()
        appConfig.authUrl = self.settingsPanel.GetUrl()
        # push event
        self.outputQueue.put(messages.SettingsChanged())
