#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import wx.lib.newevent

ExitEvent, EVT_EXIT = wx.lib.newevent.NewEvent()
SettingsEvent, EVT_SETTINGS = wx.lib.newevent.NewEvent()


class CustomButton(wx.PyControl):
    def __init__(self, parent, id=wx.ID_ANY, bitmap=None,
                 label="", pos=wx.DefaultPosition,
                 size=(10, 10), style=wx.NO_BORDER,
                 validator=wx.DefaultValidator,
                 name="CustomButton"):
        wx.PyControl.__init__(self, parent, id,
                              pos, size, style, validator, name)
        self.label = label
        self.mouseOver = False
        self.leftDown = False

        self.Bind(wx.EVT_SIZE, self.OnSize)
        self.SetInitialSize(size)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEAVE_WINDOW, self.OnLeave)
        self.Bind(wx.EVT_ENTER_WINDOW, self.OnEnter)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnLeftUp)

    def OnLeftDown(self, event):
        self.leftDown = True

    def OnLeftUp(self, event):
        if (self.leftDown):
            self.leftDown = False
            buttonEvent = wx.PyCommandEvent(wx.EVT_BUTTON.typeId, self.GetId())
            wx.PostEvent(self, buttonEvent)

    def OnEnter(self, event):
        self.mouseOver = True
        self.leftDown = False
        self.Invalidate()

    def OnLeave(self, event):
        self.mouseOver = False
        self.leftDown = False
        self.Invalidate()

    def OnSize(self, event):
        """
        Handles the ``wx.EVT_SIZE`` event for L{AquaButton}.

        :param `event`: a `wx.SizeEvent` event to be processed.
        """

        self.Invalidate()

    def SetInitialSize(self, size=None):
        """
        Given the current font and bezel width settings, calculate
        and set a good size.

        :param `size`: an instance of `wx.Size`.
        """
        if size is None:
            size = wx.DefaultSize
        wx.PyControl.SetInitialSize(self, size)

    def OnPaint(self, event):
        dc = wx.BufferedPaintDC(self)
        self.Draw(dc)

    def Draw(self, dc):
        width, height = self.GetClientSize()
        if not width or not height:
            return

        textWidth, textHeight = dc.GetTextExtent(self.label)
        if self.mouseOver:
            backColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        else:
            menuColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
            backColour = menuColour

        backBrush = wx.Brush(backColour, wx.SOLID)
        dc.SetBackground(backBrush)
        dc.Clear()

        if self.mouseOver:
            penWidth = 1
            borderColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            pen = wx.Pen(colour=borderColour, width=penWidth, style=wx.SOLID)
            dc.SetPen(pen)
            right = width - penWidth
            bottom = height - 1
            dc.DrawLine(0, 0, right, 0)
            dc.DrawLine(right, 0, right, bottom)
            dc.DrawLine(right, bottom, 0, bottom)
            dc.DrawLine(0, bottom, 0, 0)
        #dc.Clear()

        dc.SetTextForeground(self.GetForegroundColour())
        dc.SetFont(self.GetFont())

        textXpos = self.GetSpacing()
        textYpos = (height - textHeight) / 2
        dc.DrawText(self.label, textXpos, textYpos)

    def Invalidate(self):
        self.Refresh()

    def GetSpacing(self):
        return 10


class LogoPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.BORDER_NONE)

        self.SetBackgroundColour((0, 255, 0))

        vbox = wx.BoxSizer(wx.VERTICAL)

        image = wx.Image('digital-panda-menu-graphic.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        staticBitmap = wx.StaticBitmap(self, -1, bitmap, (0, 0), size)
        vbox.Add(item=staticBitmap, proportion=0, flag=wx.ALL,
                 border=5)


class ActionPanel(wx.Panel):
    def __init__(self, parent, id):
        wx.Panel.__init__(self, parent, id, wx.DefaultPosition,
                          style=wx.BORDER_NONE)
        self.parent = parent

        vbox = wx.BoxSizer(wx.VERTICAL)

        #settingsButton = platebtn.PlateButton(self, -1, 'Settings...',
        #                                      style=platebtn.PB_STYLE_SQUARE)
        #image = wx.Image("digial-panda-header.png", wx.BITMAP_TYPE_ANY)
        #settingsButton = wx.BitmapButton(self, -1,
        #  wx.Bitmap('digital-panda-header.png'))
        #settingsButton = wx.Button(self, -1, 'Settings...',
        #                           style=wx.BORDER_NONE)
        settingsButton = CustomButton(self, wx.ID_ANY, label='Settings...')
        settingsButton.Bind(wx.EVT_BUTTON, self.on_settings_clicked)
        vbox.Add(item=settingsButton, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=1)

        lineA = wx.StaticLine(self, wx.ID_ANY)
        vbox.Add(item=lineA, proportion=0, flag=wx.ALL | wx.EXPAND,
                 border=2)

        #quitButton = platebtn.PlateButton(self, wx.ID_ANY, 'Quit',
        #                                  style=platebtn.PB_STYLE_SQUARE)
        quitButton = CustomButton(self, wx.ID_ANY, label='Quit')
        quitButton.Bind(wx.EVT_BUTTON, self.on_quit_clicked)
        vbox.Add(item=quitButton, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=1)

        lineB = wx.StaticLine(self, wx.ID_ANY)
        vbox.Add(item=lineB, proportion=0, flag=wx.ALL | wx.EXPAND,
                 border=2)

        # we plomp in a spacer to make everything fit nicely
        panelSpacer = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition,
                               size=(1, 1))
        vbox.Add(item=panelSpacer, proportion=0,
                 flag=wx.RIGHT | wx.EXPAND, border=150)

        labelStatus = wx.StaticText(self, wx.ID_ANY,
                                    'Status: Online')
        vbox.Add(item=labelStatus, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=10)

        self.SetSizer(vbox)

    def on_quit_clicked(self, event):
        event = ExitEvent()
        wx.PostEvent(self.parent, event)

    def on_settings_clicked(self, event):
        event = SettingsEvent()
        wx.PostEvent(self.parent, event)


class PandaMenu(wx.Frame):
    def __init__(self, parent, id, title, pos=wx.DefaultPosition):
        wx.Frame.__init__(self, parent=parent, id=id, title=title,
                          pos=pos, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP,
                          size=(500, 200))

        logoPanel = LogoPanel(self, wx.ID_ANY)
        actionPanel = ActionPanel(self, wx.ID_ANY)

        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.Add(item=logoPanel, proportion=0,
                 flag=wx.ALL | wx.EXPAND, border=0)
        hbox.Add(item=actionPanel, proportion=1,
                 flag=wx.EXPAND | wx.ALL,
                 border=0)

        self.SetSizer(hbox)
        hbox.Fit(self)

        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

    def on_activate(self, event):
        if not event.GetActive():
            self.Hide()
