import wx


class UpdatePanel(wx.Panel):
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
	
		self.gauge = wx.Gauge(self, -1, 100, size=(250,25))
		self.progressCompletion = wx.StaticText(self, label="Progress Completion:")
		# We should probably change this to textctrl later
		# self.info = wx.TextCtrl(self, -1, style=wx.TE_READONLY | wx.BORDER_NONE)
		self.info = wx.StaticText(self, label="File: ")
		self.sizer = wx.BoxSizer(wx.VERTICAL)

		self.sizer.Add(self.progressCompletion, 0, wx.EXPAND | wx.ALL, 10)
		self.sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 10)
		self.sizer.Add(self.info, 0, wx.EXPAND | wx.ALL, 10)
		self.SetSizer(self.sizer)
		# self.SetBackgroundColour('#4f5049')


	def updateProgress(self, currentFile):
		if not currentFile:
			return
		self.info.SetLabel("File: " + str(currentFile))
		self.info.Update()
