import wx

class DirectoryView(wx.Panel):
	
	def __init__(self, parent, scanParents, toolbar):
		wx.Panel.__init__(self, parent)
		self.parent = parent
		self.toolbar = toolbar
		self.scanParents = scanParents
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		#self.directoryListings = wx.TextCtrl(self.directoryPanel, style=wx.TE_MULTILINE|wx.TE_READONLY)
		#self.lc1 = wx.ListCtrl(splitter2, -1, style=wx.LC_LIST)
		self.dirs = wx.ListCtrl(self, -1, style=wx.LC_LIST)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.enableRemoveTool, self.dirs)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.disableRemoveTool, self.dirs)
		self.title = wx.StaticText(self, label='Files')
		self.sizer.Add(self.title, 0, wx.ALIGN_CENTER|wx.BOTTOM)
		self.sizer.Add(self.dirs, 100, border=10, flag= wx.EXPAND|wx.ALL|wx.ALIGN_TOP)
		self.SetSizer(self.sizer)
	
	def updatePanel(self):
		self.dirs.ClearAll()
		for each in self.scanParents:
			self.dirs.InsertStringItem(0, each.getFilename())	
		
	def enableRemoveTool(self, e):
		self.toolbar.EnableTool(wx.ID_REMOVE, True)
	
	def disableRemoveTool(self, e):
		self.toolbar.EnableTool(wx.ID_REMOVE, False)
		
	
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