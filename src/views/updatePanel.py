import wx
import sys

from models.fileObject import FileObject as fo


class UpdatePanel(wx.Panel):
	
	def __init__(self, parent):
		wx.Panel.__init__(self, parent, style=wx.BORDER)

		self.title = wx.StaticText(self, label="Progress Completion:")
			
		#Data to be displayed. You can add more lists inside the columns
		#to display more data, however make sure the column lists are the 
		#same size or add an "empty" column by using negative indicies, or
		#the column will not display properly.
		
		#The string will be the lable, and the tuple is mapped to how uniquity
		#presents stat data. Darn, this breaks the MVC pattern, doesn't it?
		
		column1 = [
					["Scanned: ", 				(1,2)], 
					["Total Size Scanned: ", 	(1,3)], 
					["Scanning: ", 				(1,1)],
					# ["",						(-1,-1)] #Empty 
					]
					
		column2 = [
					["Duplicate Files: ", 		(2,4) ],
					["Total Duplicate Size: ", 	(2,5) ], 
					["Verifying: ", 			(2,1) ],
					# ["",						(-1,-1)]
					]		
				
		# self.stats.SetBackgroundColour("#EDEDED")
		# # self.gauge = wx.Gauge(self, -1, 100, size=(250,25))
		
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		self.sizer.Add(self.title, 0, wx.ALIGN_CENTER_HORIZONTAL|wx.ALL, 10)

		self.stats = zip(column1, column2)
		self.columnSizers = []
		
		for col1, col2 in self.stats:
			col1.append(wx.StaticText(self, -1, col1[0]))
			col2.append(wx.StaticText(self, -1, col2[0]))

			colsizer = wx.BoxSizer(wx.HORIZONTAL)
			colsizer.Add(col1[2], 1, wx.EXPAND)
			colsizer.Add(col2[2], 1, wx.EXPAND)
			self.columnSizers.append(colsizer)
			
		for each in self.columnSizers:
			self.sizer.Add(each, 1, wx.EXPAND | wx.ALL)

		# self.sizer.Add(self.gauge, 0, wx.EXPAND | wx.ALL, 10)
		self.sizer.Add((10,10), flag=wx.EXPAND | wx.ALL)
		self.SetSizer(self.sizer)
		


	def updateProgress(self, stats):
			#Possible replacement code for the below. This only assumes the data is 
			#a structure like this (which is better then the alternative mess): 
			#(
			#("info00", "info01")
			#("info10", "info11")
			#)
			# for col1, col2 in self.stats:
			# 	col1Labels, col2Labels = stats
			# 	for idx in range(len(col1)):
			# 		col1[idx].SetLabel(col1Labels[idx])
			# 		col2[idx].SetLabel(col2Labels[idx])
			# 		col1[idx].Update()
			# 		col2[idx].Update()
				
		for col1, col2 in self.stats:
			x,y = col1[1]
			if x > -1:
				col1[2].SetLabel("".join([col1[0], stats[x][y] ] ))
			x,y = col2[1]
			if x > -1:
				col2[2].SetLabel("".join([col2[0], stats[x][y] ] ))
			col1[2].Update()
			col2[2].Update()
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
		
