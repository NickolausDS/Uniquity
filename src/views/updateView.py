import wx


class UpdateBar(wx.Panel):
	self.progressPanel = wx.Panel(self)
	self.progressGauge = wx.Gauge(self.progressPanel, -1, 100, size=(250,25))
	self.progressCompletion = wx.StaticText(self.progressPanel, label="Progress Completion:")
	# We should probably change this to textctrl later
	# self.progressInfo = wx.TextCtrl(self.progressPanel, -1, style=wx.TE_READONLY | wx.BORDER_NONE)
	self.progressInfo = wx.StaticText(self.progressPanel, label="File: ")
	self.progressSizer = wx.BoxSizer(wx.VERTICAL)

	self.progressSizer.Add(self.progressCompletion, 0, wx.EXPAND | wx.ALL, 10)
	self.progressSizer.Add(self.progressGauge, 0, wx.EXPAND | wx.ALL, 10)
	self.progressSizer.Add(self.progressInfo, 0, wx.EXPAND | wx.ALL, 10)
	self.progressPanel.SetSizer(self.progressSizer)
	# self.progressPanel.SetBackgroundColour('#4f5049')


def updateProgressBar(self, percent, currentFile=None):
	self.progressGauge.SetValue(percent)
	# if currentFile:
	print currentFile
	self.progressInfo.SetLabel("File: " + currentFile)
	self.progressInfo.Update()
	# self.progressSizer.Layout()