import logging
import wx
from wx.lib.wordwrap import wordwrap
import threading
from updater import AutoUpdate
from tooling.instance import SingleInstance
import os
import traceback


EVT_COMPLETE_ID = wx.NewId()
EVT_PROGRESS_ID = wx.NewId()
EVT_FAIL_ID = wx.NewId()


def EVT_COMPLETE(win, func):
    win.Connect(-1, -1, EVT_COMPLETE_ID, func)


def EVT_PROGRESS(win, func):
    win.Connect(-1, -1, EVT_PROGRESS_ID, func)


def EVT_FAIL(win, func):
    win.Connect(-1, -1, EVT_FAIL_ID, func)


class CompleteEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_COMPLETE_ID)


class ProgressEvent(wx.PyEvent):
    def __init__(self, bytesRead, expectedBytes):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_PROGRESS_ID)
        self.bytesRead = bytesRead
        self.expectedBytes = expectedBytes


class FailEvent(wx.PyEvent):
    def __init__(self):
        wx.PyEvent.__init__(self)
        self.SetEventType(EVT_FAIL_ID)


class wxImagePanel(wx.Panel):
    def __init__(self, parent, bitmap):
        size = (bitmap.GetWidth(), bitmap.GetHeight())
        wx.Panel.__init__(self, parent, size=size)
        self.SetBackgroundStyle(wx.BG_STYLE_CUSTOM)
        self.bitmap = bitmap
        #self.Bind(wx.EVT_ERASE_BACKGROUND, self.OnEraseBackground)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.label = ''

    """
    def OnEraseBackground(self, evt):
        dc = evt.GetDC()
        if not dc:
            dc = wx.ClintDC(self)
            rect = self.GetUpdateRegion().GetBox()
            dc.SetClippingRect(rect)
        dc.Clear()
        dc.DrawBitmap(self.bitmap, 0, 0)"""

    def OnPaint(self, evt):
        bpdc = wx.BufferedPaintDC(self)
        dc = wx.GCDC(bpdc)
        self.Draw(dc)

    def Draw(self, dc):
        width, height = self.GetClientSize()
        if not width or not height:
            return

        dc.Clear()
        dc.DrawBitmap(self.bitmap, 0, 0)

        font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
        font.SetPointSize(15)
        font.SetWeight(wx.FONTWEIGHT_NORMAL)
        font.SetFaceName('Segoe UI')
        dc.SetFont(font)
        textColour = wx.Colour(255, 255, 255)
        dc.SetTextForeground(textColour)

        textWidth, textHeight = dc.GetTextExtent(self.label)
        pandaWidth = 90
        x = pandaWidth
        text = wordwrap(self.label,
                        width - pandaWidth - 50,
                        wx.ClientDC(self))

        lines = 1
        start = text.find('\n', 0)
        while start > 0:
            start = text.find('\n', start + 1)
            lines += 1

        y = (height / 2) - textHeight * lines / 2
        #print("original: %s" % self.label)
        #print("new     : %s" % text)
        dc.DrawText(text, x, y)

    def SetText(self, text):
        self.label = text
        self.Invalidate()

    def Invalidate(self):
        self.Refresh()


class wxUpdateFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, wx.ID_ANY, "Digital Panda",
                          wx.DefaultPosition,
                          style=wx.CLOSE_BOX | wx.SYSTEM_MENU | wx.CAPTION)

        icon = wx.Icon('gfx/digital-panda-icon.ico', wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

        # panel
        image = wx.Image('gfx/digitalpanda_autoupdate.png', wx.BITMAP_TYPE_ANY)
        bitmap = image.ConvertToBitmap()
        self.framePanel = wxImagePanel(self, bitmap)

        EVT_COMPLETE(self, self.OnResult)
        EVT_PROGRESS(self, self.OnProgress)
        EVT_FAIL(self, self.OnFail)

    def SetText(self, text):
        self.framePanel.SetText(text)

    def OnResult(self, event):
        self.framePanel.SetText('Starting the Digital Panda...')
        StartPanda()
        self.Close()

    def OnProgress(self, event):
        megabytesRead = 0
        if event.bytesRead > 0:
            megabytesRead = event.bytesRead / 1024.0 / 1024.0
        expectedMegaBytes = event.expectedBytes / 1024.0 / 1024.0
        self.framePanel.SetText(('Downloading the Digital Panda\n'
                                 '%s MB / %s MB') %
                                (format(megabytesRead, '.2f'),
                                 format(expectedMegaBytes, '.2f')))

    def OnFail(self, event):
        self.framePanel.SetText(('Digital Panda installation failed!\n'
                                 ':(\nPlease try again.'))


class PandaInstaller(threading.Thread):
    def __init__(self, notify_window):
        threading.Thread.__init__(self)
        self._notify_window = notify_window

    def run(self):
        try:
            autoUpdate = AutoUpdate(self)
            if autoUpdate.Install():
                self.SignalComplete()
            else:
                self.SignalFail()
        except:
            logging.error(traceback.format_exc())
            self.SignalFail()

    def SignalComplete(self):
        wx.PostEvent(self._notify_window, CompleteEvent())

    def SignalDownloadProgress(self, bytesRead, expectedBytes):
        wx.PostEvent(self._notify_window,
                     ProgressEvent(bytesRead, expectedBytes))

    def SignalFail(self):
        wx.PostEvent(self._notify_window,
                     FailEvent())


def InstallPanda():
    # the panda isn't installed at all!
    app = wx.PySimpleApp()
    frame = wxUpdateFrame()
    frame.Fit()
    frame.Centre()
    frame.SetText('Installing the Digital Panda...')
    frame.Show(True)
    # start up a thread for the update
    installerThread = PandaInstaller(frame)
    installerThread.start()
    frame.SetText('Installing the Digital Panda...')
    app.MainLoop()


def StartPanda():
    logging.info("starting the panda")
    autoUpdate = AutoUpdate(None)
    os.startfile(autoUpdate.GetShortcutPath())


def main():
    logging.basicConfig(level=logging.DEBUG)
    instanceName = '{5A475CB1-CDB5-46b5-B221-4E36602FC47E}'
    myapp = SingleInstance(instanceName)
    try:
        if myapp.alreadyRunning():
            logging.info('another instance of sync tool already running')

        autoUpdate = AutoUpdate(None)
        if (autoUpdate.IsInstalled()):
            #pandaPath = autoUpdate.GetShortcutPath()
            #subprocess.call([pandaPath])
            os.startfile(autoUpdate.GetShortcutPath())
        else:
            InstallPanda()
    finally:
        del myapp
