import wx


class UpdatePanel(wx.Panel):
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.BORDER)

		self.title = wx.StaticText(self, label="Progress Completion:")
		
		self.scanProperties = ['Scanned: ','Size Scanned: ','Current File: ']
		self.scanP = ['filesScanned', 'sizeScanned', 'currentScanFile']
		
		self.verifiedProperties = ['Verified:', 'Size Verified:', 'Current File: ']
		self.verifiedP = ['filesHashed','sizeHashed','currentHashFile']
		
		self.scanInfo = wx.ListCtrl(self, -1, style=wx.LC_LIST , size=(200,60))
		for each in self.scanProperties:
			self.scanInfo.InsertStringItem(10, each + "\n")
			
		self.scanInfo.SetBackgroundColour("#EDEDED")
			
		self.verifiedInfo = wx.ListCtrl(self, -1, style=wx.LC_LIST, size=(200,60))
		for each in self.verifiedProperties:
			self.verifiedInfo.InsertStringItem(10, each + "\n")
		self.verifiedInfo.SetBackgroundColour("#EDEDED")	
		
		# self.gauge = wx.Gauge(self, -1, 100, size=(250,25))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.title, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 10)
		
		self.infoSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.infoSizer.Add(self.scanInfo, 1, flag=wx.ALIGN_LEFT | wx.EXPAND | wx.LEFT | wx.FIXED_MINSIZE, border=10)
		self.infoSizer.Add(self.verifiedInfo, 1, flag=wx.ALIGN_RIGHT|wx.EXPAND | wx.RIGHT | wx.FIXED_MINSIZE, border=10)
		
		self.sizer.Add(self.infoSizer, flag=wx.EXPAND)
		# self.sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 10)
		self.sizer.Add((10,10), flag=wx.EXPAND | wx.ALL)
		self.SetSizer(self.sizer)


	def updateProgress(self, stats):
		# ss = stats.get('scannerStatus')
		# hs = stats.get('hasherStatus')
		# if ss == 'running' and hs == 'idle':
		# 	self.gauge.Pulse()
		# elif ss == 'idle' and hs == 'running':
		# 	self.gauge.SetRange(stats.get('possibleDuplicates'))
		# 	self.gauge.SetValue(stats.get('filesHashed'))
		# else:
		# 	self.gauge.SetRange(stats.get('possibleDuplicates', 0))
		# 	self.gauge.SetValue(stats.get('possibleDuplicates', 0))
		
		if stats.get("scannerStatus") == "idle":
			stats['currentScanFile'] = 'Done'
		if stats.get("hasherStatus") == "idle":
			stats['currentHashFile'] = 'Done'
			
			
		for idx, each in enumerate(self.scanP):
			if stats.get(each):
				self.scanInfo.DeleteItem(idx)
				self.scanInfo.InsertStringItem(idx, self.scanProperties[idx] + unicode(stats.get(each)))
		for idx, each in enumerate(self.verifiedP):
			if stats.get(each):
				self.verifiedInfo.DeleteItem(idx)
				self.verifiedInfo.InsertStringItem(idx, self.verifiedProperties[idx] + unicode(stats.get(each)))
		# self.scanInfo.Update()
