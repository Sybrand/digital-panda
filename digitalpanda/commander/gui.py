import wx

class Gui():
	def __init__(self, app):
		"""

		"""
		frame = wx.Frame(None, -1, 'Digital Panda Commander')
		frame.Show()


if __name__ == '__main__':
	print "panda commander gui!"
	app = wx.App()

	g = Gui(app)

	app.MainLoop()