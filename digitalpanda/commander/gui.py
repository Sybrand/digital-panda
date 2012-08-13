"""
F.Y.I - it's VERY early days for this module - there's still a lot that needs
to be done

This module deviates from PEP 8 - seems like the wx-python guys didn't use
PEP 8 - and it just looks messy mixing PEP 8 with wx-python - so try to emulate
wx-python code in this module

TODO: currently busy with: skeleton
TODO: next: implement action panel
TODO: hookup events, re-factor, style, etc. etc.
"""

import wx
from wx.lib.mixins.listctrl import ListCtrlAutoWidthMixin
from ..bucket.local import LocalBucket
from ..bucket.swift import SwiftBucket
from ..digitalpanda import Config
import sys
import logging

ID_SPLITTER = 300

class AutoWidthListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
    def __init__(self, parent):
        wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT)
        ListCtrlAutoWidthMixin.__init__(self)

class ActionPanel(wx.Panel):
    """
    The action panel relates to the currently selected bucket pane,
    and allows one to perfrom actions in that context.
    e.g: copy file from selected pane, to other pane
    e.g: create directory in selected pane
    """
    def __init__(self, *args, **kwargs):
        super(ActionPanel, self).__init__(*args, **kwargs)

        self._InitUI()

    def _InitUI(self):
        
        sizer = wx.BoxSizer(wx.VERTICAL)

        gbs = wx.GridBagSizer(2, 2)
        gbs.AddGrowableCol(0)
        gbs.Add(wx.Button(self, label = 'Copy'), pos = (0,0), 
            span = (1, 1), flag= wx.EXPAND)
        gbs.AddGrowableCol(1)
        gbs.Add(wx.Button(self, label = 'Move'), pos = (0,1), 
            span = (1, 1), flag= wx.EXPAND)
        gbs.AddGrowableCol(2)
        gbs.Add(wx.Button(self, label = 'Mkdir'), pos = (0,2), 
            span = (1, 1), flag= wx.EXPAND)
        gbs.AddGrowableCol(3)
        gbs.Add(wx.Button(self, label = 'Delete'), pos = (0,3), 
            span = (1, 1), flag= wx.EXPAND)
        gbs.AddGrowableCol(4)
        gbs.Add(wx.Button(self, label = 'Search'), pos = (0,4), 
            span = (1, 1), flag= wx.EXPAND)

        sizer.Add(wx.StaticText(self, label='some static text?'), flag = wx.EXPAND)
        sizer.Add(gbs, flag = wx.EXPAND)
        self.SetSizer(sizer)        



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

        self._currentDirectory = wx.StaticText(self, label='TODO: show current directory here')

        #sizer = wx.GridSizer(rows = 2, cols = 1)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self._currentDirectory, 0, flag = wx.EXPAND)
        sizer.Add(self._listbox, 1, flag = wx.EXPAND)
        self.SetSizer(sizer)

        self._PopulateCurrentDirectory()

    def _PopulateCurrentDirectory(self):
        # get entries
        try:
            self._currentDirectory.SetLabel(self._bucket.get_current_dir())

            entries = self._bucket.list_current_dir()
            for entry in entries:
                index = self._listbox.InsertStringItem(sys.maxint, '')
                self._listbox.SetStringItem(index, 1, entry.name)
        except:
            # TODO: feed exception details to user
            logging.error('failed to get directory listing!')        

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

        splitter = wx.SplitterWindow(self, ID_SPLITTER, style = wx.SP_BORDER)
        splitter.SetMinimumPaneSize(50)

        # TODO: allow for runtime decision on loading openstack swift, local files system, or amazon s3
        local_panel = BucketPanel(splitter, LocalBucket())         
        remote_panel = BucketPanel(splitter, SwiftBucket())
        action_panel = ActionPanel(self)

        splitter.SplitVertically(local_panel, remote_panel)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(splitter,1,wx.EXPAND)
        sizer.Add(action_panel,0,wx.EXPAND)
        self.SetSizer(sizer)
        

    def _InitMenuItems(self):
        menubar = wx.MenuBar()
        file_menu = wx.Menu()        
        item = file_menu.Append(wx.ID_EXIT, '&Quit\tCtrl+Q')
        self.Bind(wx.EVT_MENU, self._OnQuit, item)
        menubar.Append(file_menu, '&File')
        self.SetMenuBar(menubar)

    def _OnQuit(self, e):
        self.Close()


def run_gui():
    config = Config().config;
    log_level = getattr(logging, config.get('Logging', 'log_level').upper())

    logging.basicConfig(level=log_level)

    app = wx.App()

    g = Gui(None, -1, 'Digital Panda Commander', size=(800,300))

    app.MainLoop()

if __name__ == '__main__':
    run_gui()
    