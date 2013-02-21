#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx
import settings
import panda_menu
import sys
import os
import os.path
import subprocess
import threading
import response_event
import version
import messages
import logging
import config
from bucket.abstract import ProgressMessage


if sys.platform == 'win32':
    def open_folder(path):
        if not os.path.exists(path):
            os.makedirs(path)
        subprocess.call(['explorer', path])


class PandaMenu(wx.Menu):
    def __init__(self):
        wx.Menu.__init__(self)

        image = wx.Image('gfx/digital-panda-online-1616.png',
                         wx.BITMAP_TYPE_ANY)
        self.bitmap = image.ConvertToBitmap()
        wx.EVT_PAINT(self, self.on_paint)


class TaskBar(wx.TaskBarIcon):
    """ Icon that appears on TaskBar

    - Windows <= 8 have taskbar icons - this class will run fine in
     those environments.
    - Ubuntu with Unity >= 11.04 needs to use an Application
     Indicator - see http://unity.ubuntu.com/projects/appindicators/
    - No idea what would have to be done for mac at this point in time.

    """

    def __init__(self, outputQueue, inputQueue):
        super(TaskBar, self).__init__()
        self.icon = wx.IconFromBitmap(wx.Bitmap("gfx/icon1616.png"))
        #icon = wx.Icon('digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.Bind(wx.EVT_TASKBAR_LEFT_DOWN, self.on_left_down)
        self.Bind(wx.EVT_TASKBAR_RIGHT_DOWN, self.on_right_down)

        self.dialog = None
        self.outputQueue = outputQueue
        self.inputQueue = inputQueue
        self.set_status('Starting...')
        """self.timer = wx.Timer(self)
        self.timer.Bind(wx.EVT_TIMER, self.on_timer)
        self.timer.Start(100)"""
        self.advancedMenu = self.create_advanced_menu()

        self.inputQueueThread = threading.Thread(target=self.queue_listener)
        self.isRunning = True
        self.inputQueueThread.start()

    def queue_listener(self):
        while self.isRunning:
            item = self.inputQueue.get()
            if item:
                if isinstance(item, messages.ShowSettings):
                    event = panda_menu.SettingsEvent()
                    wx.PostEvent(self.advancedMenu, event)
                elif isinstance(item, messages.Status):
                    self.set_status(item.message)
                    wx.PostEvent(self.advancedMenu,
                                 response_event.ResponseEvent(attr1=item.message))
                elif isinstance(item, messages.Stop):
                    break
                elif isinstance(item, ProgressMessage):
                    parts = item.path.split('/')
                    mBRead = item.bytes_read / 1024 / 1024
                    mBExpected = item.bytes_expected / 1024 / 1024
                    mBps = item._bytes_per_second / 1024 / 1024

                    message = ('Downloading %s (%.2fMB/%.2fMB @ %.2fMBps)'
                               % (parts[-1], mBRead, mBExpected, mBps))
                    self.set_status(message)
                    pass
                else:
                    try:
                        self.set_status(item)
                        wx.PostEvent(self.advancedMenu,
                                     response_event.ResponseEvent(attr1=item))
                    finally:
                        logging.info('exception')
                        pass

    def set_status(self, status):
        self.status = status
        self.SetIcon(self.icon, 'Digital Panda v%s\r\n'
                                'Cloud Storage Sync Client\r\n'
                                '%s' %
                                (version.version, self.status))
        if self.dialog:
            self.dialog.SetStatus(self.status)

    def on_left_down(self, event):
        self.show_advanced_menu()

    def on_right_down(self, event):
        # showing system default popup menu - will probably switch
        # over to using ONLY the advanced menu
        self.PopupMenu(self.create_popup_menu())

    def create_popup_menu(self):
        """ Returns a popup menu.

        """
        menu = wx.Menu()

        # open folder
        item = wx.MenuItem(menu, -1, 'Open Digital Panda folder')
        menu.Bind(wx.EVT_MENU, self.open_folder, id=item.GetId())
        menu.AppendItem(item)

        # settings
        item = wx.MenuItem(menu, -1, 'Settings...')
        menu.Bind(wx.EVT_MENU, self.show_settings, id=item.GetId())
        menu.AppendItem(item)

        # quit
        item = wx.MenuItem(menu, -1, 'Quit')
        menu.Bind(wx.EVT_MENU, self.on_exit, id=item.GetId())
        menu.AppendItem(item)

        # status
        item = wx.MenuItem(menu, -1, 'Status: %s' % self.status)
        menu.AppendItem(item)
        return menu

    def create_advanced_menu(self):
        """ Returns an "advanced menu" - this is just a popup
        menu with nice graphics on it.

        """
        advancedMenu = panda_menu.PandaMenu(None, -1, 'Advanced Menu')

        advancedMenu.Bind(panda_menu.EVT_EXIT, self.on_exit)
        advancedMenu.Bind(panda_menu.EVT_SETTINGS, self.show_settings)
        advancedMenu.Bind(panda_menu.EVT_OPEN_FOLDER, self.open_folder)

        return advancedMenu

    def on_exit(self, event):
        self.isRunning = False
        self.inputQueue.put(messages.Stop())
        logging.debug('putting stop on queue')
        self.outputQueue.put(messages.Stop())
        wx.CallAfter(self.Destroy)
        if self.dialog:
            self.dialog.Destroy()
        if self.advancedMenu:
            self.advancedMenu.Destroy()

    def show_settings(self, event):
        logging.debug('show_settings')
        if not self.dialog:
            self.dialog = settings.Settings(None, -1, 'Digital Panda Settings',
                                            self.status, self.outputQueue)

            self.dialog.Center()
            self.dialog.Show(True)
        else:
            self.dialog.SetStatus(self.status)
            self.dialog.Show(True)
            # simply calling .Raise() doesn't work in windows
            # so we change the style to on top, and back again
            style = self.dialog.GetWindowStyle()
            self.dialog.SetWindowStyle(style | wx.STAY_ON_TOP)
            self.dialog.SetWindowStyle(style)

    def open_folder(self, event):
        """ Open the sync folder (and creates it if it doesn't exist)
        """
        if self.advancedMenu:
            self.advancedMenu.Show(False)
        home = os.path.expanduser('~')
        c = config.Config()
        panda = None
        if c.username:
            # try for full path if there is a username
            panda = os.path.join(home, 'Digital Panda', c.username)
            if not os.path.exists(panda):
                # if the path doesn't exist - reset
                panda = None
        if not panda:
            # get base folder (without acccount)
            panda = os.path.join(home, 'Digital Panda')
        if not os.path.exists(panda):
            try:
                os.makedirs(panda)
            except:
                print "TODO: need to handle folder creation failure!"
        open_folder(panda)

    def show_advanced_menu(self):
        menuSize = self.advancedMenu.GetSize()
        mousePosition = wx.GetMousePosition()
        pos = (mousePosition[0],
               mousePosition[1] - menuSize.height)
        self.advancedMenu.Move(pos)

        self.advancedMenu.Show()
        self.advancedMenu.Raise()
