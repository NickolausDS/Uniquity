import wx

class DirectoryView(wx.Panel):
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.dirs = wx.ListCtrl(self, -1, style=wx.LC_LIST)
		self.title = wx.StaticText(self, label='Files')
		self.sizer.Add(self.title, 0, wx.ALIGN_CENTER|wx.BOTTOM)
		self.sizer.Add(self.dirs, 100, border=10, flag= wx.EXPAND|wx.ALL|wx.ALIGN_TOP)
		self.SetSizer(self.sizer)
	
	def updateView(self, filenames):
		self.dirs.ClearAll()
		for each in filenames:
			self.dirs.InsertStringItem(0, each)			
		
	
	def getSelected(self):
		selection = []
		# start at -1 to get the first selected item
		current = -1
		while True:
			# next = self.mainView.directoryListings.GetNextSelected(listctrl, current)
			next = self.dirs.GetNextSelected(current)
			if next == -1:
				break
			selection.append(self.dirs.GetItemText(next, 0))
			current = next
		
		return selection
	
	# #We don't really need these. It's preferred for the controller to 
	# #Update everything with updateView(). This way, the controller can
	# #Handle errors and this view won't get out of sync.	
	# def AddItems(self):
	# 	pass
	# 	
	# def RemoveItems(self):
	# 	pass