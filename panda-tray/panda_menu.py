#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import wx.lib.newevent
import response_event

ExitEvent, EVT_EXIT = wx.lib.newevent.NewEvent()
SettingsEvent, EVT_SETTINGS = wx.lib.newevent.NewEvent()
OpenFolderEvent, EVT_OPEN_FOLDER = wx.lib.newevent.NewEvent()


class CustomButton(wx.PyControl):
    def __init__(self, parent, id=wx.ID_ANY, bitmap=None,
                 label="", pos=wx.DefaultPosition,
                 size=(180, 10), style=wx.NO_BORDER,
                 validator=wx.DefaultValidator,
                 name="CustomButton",
                 font_weight=wx.FONTWEIGHT_NORMAL):
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
        self.SetTransparent(50)
        self.active = True
        self.font_weight = font_weight

    def SetLabel(self, text):
        self.label = text
        self.Invalidate()

    def SetInactive(self):
        self.active = False

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
        # http://wxpython.org/docs/api/wx.BufferedPaintDC-class.html
        bpdc = wx.BufferedPaintDC(self)
        #pdc = wx.PaintDC(self)
        dc = wx.GCDC(bpdc)
        self.Draw(dc)

    def Draw(self, dc):
        width, height = self.GetClientSize()
        if not width or not height:
            return

        # http://docs.wxwidgets.org/2.8/wx_wxsystemsettings.html
        backColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        backBrush = wx.Brush(backColour, wx.SOLID)
        dc.SetBackground(backBrush)
        dc.Clear()

        if self.mouseOver and self.active:
            penWidth = 1
            borderColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            borderColour = wx.Colour(borderColour.Red(),
                                     borderColour.Green(),
                                     borderColour.Blue(),
                                     80)
            # http://wxpython.org/docs/api/wx.Pen-class.html
            # http://docs.wxwidgets.org/trunk/classwx_pen.html
            pen = wx.Pen(colour=borderColour, width=penWidth,
                         style=wx.SOLID)
            dc.SetPen(pen)
            rectColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_HIGHLIGHT)
            rectColour = wx.Colour(rectColour.Red(),
                                   rectColour.Green(),
                                   rectColour.Blue(),
                                   5)
            dc.SetBrush(wx.Brush(rectColour))

            rect = wx.Rect(0, 0, width, height)
            rect.SetPosition((0, 0))
            dc.DrawRoundedRectangleRect(rect, 3)

        textColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENUTEXT)
        textColour = wx.Colour(textColour.Red(), textColour.Green(),
                               textColour.Blue(), wx.ALPHA_OPAQUE)
        dc.SetTextForeground(textColour)
        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(9)
        font.SetWeight(self.font_weight)
        font.SetFaceName('Segoe UI')

        #font = wx.Font(9, wx.FONTFAMILY_DEFAULT,
        #               wx.NORMAL, wx.NORMAL, False, 'MS Shell Dlg 2')
        #font = wx.Font(9, wx.SWISS, wx.NORMAL,
        #               wx.NORMAL, False, u'Segoe UI')

        dc.SetFont(font)

        textXpos = self.GetSpacing()
        textWidth, textHeight = dc.GetTextExtent(self.label)
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

        backColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        self.SetBackgroundColour(backColour)

        vbox = wx.BoxSizer(wx.VERTICAL)

        image = wx.Image('gfx/digital-panda-menu-graphic.png',
                         wx.BITMAP_TYPE_ANY)
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

        settingsButton = CustomButton(self, wx.ID_ANY,
                                      label='Open Digital Panda folder',
                                      font_weight=wx.FONTWEIGHT_BOLD)
        settingsButton.Bind(wx.EVT_BUTTON, self.on_open_folder_clicked)
        vbox.Add(item=settingsButton, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=1)

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

        #lineA = wx.StaticLine(self, wx.ID_ANY)
        #vbox.Add(item=lineA, proportion=0, flag=wx.ALL | wx.EXPAND,
        #         border=2)

        #quitButton = platebtn.PlateButton(self, wx.ID_ANY, 'Quit',
        #                                  style=platebtn.PB_STYLE_SQUARE)
        quitButton = CustomButton(self, wx.ID_ANY, label='Quit')
        quitButton.Bind(wx.EVT_BUTTON, self.on_quit_clicked)
        vbox.Add(item=quitButton, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=1)

        #lineB = wx.StaticLine(self, wx.ID_ANY)
        #vbox.Add(item=lineB, proportion=0, flag=wx.ALL | wx.EXPAND,
        #         border=2)

        # we plomp in a spacer to make everything fit nicely
        """panelSpacer = wx.Panel(self, wx.ID_ANY, wx.DefaultPosition,
                               size=(1, 1))
        vbox.Add(item=panelSpacer, proportion=0,
                 flag=wx.RIGHT | wx.EXPAND, border=150)"""

        """
        labelStatus = wx.StaticText(self, wx.ID_ANY,
                                    'Status: Online')
        vbox.Add(item=labelStatus, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=10)"""

        self.statusButton = CustomButton(self, wx.ID_ANY,
                                         label='Status: Disconnected')
        self.statusButton.SetInactive()
        vbox.Add(item=self.statusButton, proportion=1,
                 flag=wx.ALL | wx.EXPAND, border=1)

        self.SetSizer(vbox)

    def on_quit_clicked(self, event):
        event = ExitEvent()
        wx.PostEvent(self.parent, event)

    def on_settings_clicked(self, event):
        event = SettingsEvent()
        wx.PostEvent(self.parent, event)

    def on_open_folder_clicked(self, event):
        event = OpenFolderEvent()
        wx.PostEvent(self.parent, event)

    def set_status(self, status):
        self.stats = status
        self.statusButton.SetLabel('Status: %s' % status)


class PandaMenu(wx.Frame):
    def __init__(self, parent, id, title, pos=wx.DefaultPosition):
        wx.Frame.__init__(self, parent=parent, id=id, title=title,
                          pos=pos, style=wx.FRAME_NO_TASKBAR | wx.STAY_ON_TOP |
                          wx.SIMPLE_BORDER,
                          size=(500, 200))

        logoPanel = LogoPanel(self, wx.ID_ANY)
        self.actionPanel = ActionPanel(self, wx.ID_ANY)

        backColour = wx.SystemSettings.GetColour(wx.SYS_COLOUR_MENU)
        self.SetBackgroundColour(backColour)
        #self.SetBackgroundColour((255, 0, 0))
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        hbox.Add(item=logoPanel, proportion=0,
                 flag=wx.ALL | wx.EXPAND, border=0)

        hbox.Add(item=self.actionPanel, proportion=1,
                 flag=wx.EXPAND | wx.ALL,
                 border=0)

        self.SetSizer(hbox)
        hbox.Fit(self)
        #"""

        self.Bind(response_event.EVT_RESPONSE_EVENT, self.on_response_event)
        self.Bind(wx.EVT_ACTIVATE, self.on_activate)

    def on_response_event(self, event):
        print "menu has on_response_event"
        self.actionPanel.set_status(event.attr1)

    def on_activate(self, event):
        if not event.GetActive():
            self.Hide()
