#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx


class Settings(wx.Frame):
    def __init__(self):
        frame = wx.Frame(None, title='Settings')
        icon = wx.Icon('digital-panda.ico', wx.BITMAP_TYPE_ICO)
        frame.SetIcon(icon)
        frame.Center()
        frame.Show()
