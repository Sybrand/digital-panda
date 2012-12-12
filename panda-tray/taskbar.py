#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import settings


class TaskBar(wx.TaskBarIcon):
    def __init__(self):
        super(TaskBar, self).__init__()
        #icon = wx.IconFromBitmap(wx.Bitmap("panda3232.png"))
        icon = wx.Icon('digital-panda.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon, "Digital Panda\r\nCloud Storage Sync Client\r\n" +
                     "Online")
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down)

        self.dialog = None

    def on_left_down(self, event):
        # we give left click the same functionality as right click
        self.PopupMenu(self.create_popup_menu())

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

    def show_settings(self, event):
        self.dialog = settings.Settings(None, -1, 'Settings')
        self.dialog.Center()
        self.dialog.Show()
