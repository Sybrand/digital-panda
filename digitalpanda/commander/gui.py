import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from ..bucket.local import LocalBucket
from ..bucket.swift import SwiftBucket
from ..digitalpanda import Config
import sys
import logging

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)

class BucketPanel(wx.Panel):
    """
    All the different data sources have the same panel - the only difference 
    is the bucket passed at construction

    """

    def __init__(self, parent, bucket):
        """
        parent - parent widget
        bucket - instance of ..bucket.abstract.AbstractBucket
        """

        super(BucketPanel, self).__init__(parent, -1)
        self._bucket = bucket
        self._InitUI()

    def _InitUI(self):
        self._listbox = AutoWidthListCtrl(self)
        self._listbox.InsertColumn(0, '', width = 20) # icon column
        self._listbox.InsertColumn(1, 'name')
        self._listbox.InsertColumn(2, 'ext')
        self._listbox.InsertColumn(3, 'size')
        self._listbox.InsertColumn(4, 'date')

        gs = wx.GridSizer(rows = 1, cols = 1)
        gs.Add(self._listbox, flag = wx.EXPAND)
        self.SetSizer(gs)

        self._PopulateCurrentDirectory()

    def _PopulateCurrentDirectory(self):
        # get entries
        entries = self._bucket.list_current_dir()
        for entry in entries:
            index = self._listbox.InsertStringItem(sys.maxint, '')
            self._listbox.SetStringItem(index, 1, entry.name)

class Gui(wx.Frame):
    def __init__(self, *args, **kwargs):
        """ classic user interface for advanced users (currently very much
            a work in progress)

        """
        super(Gui, self).__init__(*args, **kwargs)

        self._InitUi()
        self.Show()

    def _InitUi(self):
        self._InitMenuItems()

        local_panel = BucketPanel(self, LocalBucket()) 
        # TODO: allow for runtime decision on loading openstack swift or amazon s3
        remote_panel = BucketPanel(self, SwiftBucket()) 

        frame_gs = wx.GridSizer(rows = 1, cols = 2)
        frame_gs.Add(local_panel, flag = wx.EXPAND)
        frame_gs.Add(remote_panel, flag = wx.EXPAND)
        self.SetSizer(frame_gs)
        

    def _InitMenuItems(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()        
        item = file_menu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')
        self.Bind(wx.EVT_MENU, self._OnQuit, item)
        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

    def _OnQuit(self, e):
        self.Close()


if __name__ == '__main__':
    config = Config().config;
    log_level = getattr(logging, config.get('Logging', 'log_level').upper())

    logging.basicConfig(level=log_level)

    app = wx.App()

    g = Gui(None, -1, 'Digital Panda Commander', size=(800,300))

    app.MainLoop()