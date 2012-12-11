#!/usr/bin/python
'''
Created on December 11, 2012

@author: Sybrand Strauss
'''
import wx


class Settings:
    def __init__(self):
        frame = wx.Frame(None, title='Settings')
        icon = wx.IconFromBitmap(wx.Bitmap("panda1616.png"))
        frame.SetIcon(icon)
        frame.Center()
        frame.Show()
