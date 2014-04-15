import wx

import dupViewController
import reportDupFileView



class MainDupView(wx.Notebook):
	
	def __init__(self, parent, maincontroller):
		wx.Notebook.__init__(self, parent, -1, style=(wx.NB_TOP))
		self.parent = parent
		self.mainController = maincontroller
		
		# self.dupController = dupViewController.DupViewController()
		self.view = reportDupFileView.ReportDupFileView(self)
		self.AddPage(self.view, "Detail")
		
		# views = self.dupController.getAllViews()
		# 
		# for each in views:
		# 	self.AddPage(each, each.name)
		
		
		def getSelected(self):
			"""Get the currently selected files from the view."""
			return	


		def updateView(self, files):
			"""Update the view with a new set of files"""
			return