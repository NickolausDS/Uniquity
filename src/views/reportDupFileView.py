import wx

import abc
from wx.lib.pubsub import pub



class ReportDupFileView(wx.ListCtrl):
	def __init__(self, parent):
		wx.ListCtrl.__init__(
			self, parent, -1, 
			style=wx.LC_REPORT|wx.LC_VIRTUAL|wx.LC_HRULES|wx.LC_VRULES
		)


		self.InsertColumn(0, "Name")
		self.InsertColumn(1, "Size")
		self.InsertColumn(2, "Hash")
		self.SetColumnWidth(0, 350)
		self.SetColumnWidth(1, 120)
		self.SetColumnWidth(2, 175)

		#For some reason, we need to make a blank image or the second
		#column refuses to show up. I'm not sure why. Thanks Obama. 
		self.il = wx.ImageList(16, 16)
		# self.idx1 = self.il.Add(images.Smiles.GetBitmap())
		empty = self.makeBlank()
		self.idx2 = self.il.Add(empty)
		self.SetImageList(self.il, wx.IMAGE_LIST_SMALL)

		self.altAttr = wx.ListItemAttr()
		#Light grey background colour
		self.altAttr.SetBackgroundColour((220,220,220))


		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.OnItemSelected)
		self.Bind(wx.EVT_LIST_ITEM_ACTIVATED, self.OnItemActivated)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.OnItemDeselected)

		self.parentDirs = []
		self.files = []
		self.uniqueGroupIndex = []
		# self.SetItemCount(10000)
		
		
	def getSelected(self):
		selection = []
		# start at -1 to get the first selected item
		current = -1
		while True:
			next = self.GetNextSelected(current)
			if next == -1:
				break
			selection.append(self.files[next])
			current = next
		return selection

	def updateView(self, files):
		self.files = []
		self.uniqueGroupIndex = []
		for each in files:
			self.files.extend(each)
			self.uniqueGroupIndex.append(each[0].hashes)
		self.SetItemCount(len(self.files))
		
	def updateParentDirs(self, dirs):
		self.parentDirs = dirs

	#Finds the parent dir, since that isn't built into fileObjects yet
	def findParentDir(self, fileObject):
		for each in self.parentDirs:
			if fileObject.isParent(each):
				return each
		return fileObject

	def makeBlank(self):
		empty = wx.EmptyBitmap(16,16,32)
		dc = wx.MemoryDC(empty)
		dc.SetBackground(wx.Brush((0,0,0,0)))
		dc.Clear()
		del dc
		empty.SetMaskColour((0,0,0))
		return empty
    

	def OnItemSelected(self, event):
		if len(self.getSelected()) >= 1:
			pub.sendMessage("dupview.itemselected")

	def OnItemActivated(self, event):
		self.currentItem = event.m_itemIndex
		# self.log.debug("User selected item %s, Top Item: %s", self.GetItemText(self.currentItem), self.GetTopItem())
		# self.log.WriteText("OnItemActivated: %s\nTopItem: %s\n" %
		             # (self.GetItemText(self.currentItem), self.GetTopItem()))

	# def getColumnText(self, index, col):
	# 	#Old values
	# 	item = self.GetItem(index, col)
	# 	return item.GetText()

	def OnItemDeselected(self, evt):
		if len(self.getSelected()) == 0:
			pub.sendMessage("dupview.allitemsdeselected")

	#-----------------------------------------------------------------
	# These methods are callbacks for implementing the "virtualness"
	# of the list...  Normally you would determine the text,
	# attributes and/or image based on values from some external data
	# source, but for this demo we'll just calculate them
	def OnGetItemText(self, item, col):
		if col == 0:
			return self.files[item].filename
		elif col == 1:
			return self.files[item].niceSizeAndDesc
		elif col == 2:
			return self.files[item].strongHash
		else:
			return "Item %d, column %d" % (item, col)

	def OnGetItemImage(self, item):
		# if item % 3 == 0:
		# 	return self.idx1
		# else:
		return self.idx2

	def OnGetItemAttr(self, item):
		if self.uniqueGroupIndex.index(self.files[item].hashes) % 2 == 1:
			return self.altAttr
		else:
			return None	
	