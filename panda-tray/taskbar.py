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
        icon = wx.IconFromBitmap(wx.Bitmap("panda3232.png"))
        self.SetIcon(icon, "Digital Panda - Cloud Storage Sync Client" +
                     " - Online")
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)

    def on_left_down(self, event):
        # we give left click the same functionality as right click
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

    def show_settings(self, event):
        settings.Settings()
