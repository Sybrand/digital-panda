#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import settings
import panda_menu


class PandaMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)

        image = wx.Image('digital-panda-online-1616.png', wx.BITMAP_TYPE_ANY)
        self.bitmap = image.ConvertToBitmap()
        wx.EVT_PAINT(self, self.on_paint)


class TaskBar(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBar, self).__init__()
        #icon = wx.IconFromBitmap(wx.Bitmap("panda3232.png"))
        icon = wx.Icon('digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon, "Digital Panda\r\nCloud Storage Sync Client\r\n" +
                     "Online")
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down)

        self.dialog = None
        self.advancedMenu = None

    def on_left_down(self, event):
        # we give left click the same functionality as right click
        self.show_advanced_menu()

    def on_right_down(self, event):
        # we give right click the same functionality as left
        self.PopupMenu(self.create_popup_menu())

    def create_popup_menu(self):
        menu = wx.Menu()

        # settings
        item = wx.MenuItem(menu, -1, 'Settings...')
        menu.Bind(wx.EVT_MENU, self.show_settings, id=item.GetId())
        menu.AppendItem(item)

        # quit
        item = wx.MenuItem(menu, -1, 'Quit')
        menu.Bind(wx.EVT_MENU, self.on_exit, id=item.GetId())
        menu.AppendItem(item)

        # status
        item = wx.MenuItem(menu, -1, 'Status: Online')
        menu.AppendItem(item)
        return menu

    def on_exit(self, event):
        wx.CallAfter(self.Destroy)
        if self.dialog:
            self.dialog.Destroy()
        if self.advancedMenu:
            self.advancedMenu.Destroy()

    def show_settings(self, event):
        self.dialog = settings.Settings(None, -1, 'Settings')
        self.dialog.Center()
        self.dialog.Show()

    def show_advanced_menu(self):
        if not self.advancedMenu:
            self.advancedMenu = panda_menu.PandaMenu(None, -1, 'Advanced Menu')
        self.advancedMenu.Center()
        self.advancedMenu.Show()
        self.advancedMenu.Raise()
