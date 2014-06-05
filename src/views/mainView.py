import wx
import os
import logging
from wx.lib.pubsub import pub


import controller

import data.config as config
from directoryView import DirectoryView
from fileMenu import FileMenu
from toolbar import Toolbar
import updatePanel
import mainDupView

class MainWindow(wx.Frame, wx.FileDropTarget):
	def __init__(self, parent, title):
		self.dirname=''
		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.
		wx.Frame.__init__(self, parent, title=title, size=(800,600))
		
		#setup drag and drop. It fires when someone drags a file onto the main window
		#and calls the method "addFiles"
		wx.FileDropTarget.__init__(self)
		self.SetDropTarget(self)
		
		self.log = logging.getLogger('.'.join((config.GUI_LOG_NAME, "MainView")))
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		#Our main view objects
		self.fileMenu = FileMenu(self)
		self.toolbar = Toolbar(self)
		self.toolbar.Bind(wx.EVT_TOOL, self.addFile, self.toolbar.add)
		self.toolbar.Bind(wx.EVT_TOOL, self.removeFiles, self.toolbar.remove)
		self.toolbar.Bind(wx.EVT_TOOL, self.viewFiles, self.toolbar.view)
		self.toolbar.Bind(wx.EVT_TOOL, self.deleteFiles, self.toolbar.delete)
		self.updatePanel = updatePanel.UpdatePanel(self)
		
		self.mainSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH, size=(300,300))
		self.directoryView = DirectoryView(self.mainSplitter)
		self.directoryView.Bind(wx.EVT_LIST_ITEM_SELECTED, self.dirsSelected, self.directoryView.dirs)
		self.directoryView.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.dirsDeselected, self.directoryView.dirs)
		
		#Added later by controller. The main view should never need this, except to add
		#it to the wx components. 
		self.dupView = None
	
		
		##PUT MAIN GUI TOGETHER
		self.sizer = wx.BoxSizer(wx.VERTICAL)
		paddingPanel = wx.Panel(self, size=(0,20))
		self.sizer.Add(paddingPanel, 0)
		self.sizer.Add(self.mainSplitter, 1, wx.EXPAND)
		self.sizer.Add(self.updatePanel, 0, wx.EXPAND | wx.ALL, 10)
		# self.sizer.Add(self.progressPanel, 0, wx.EXPAND | wx.ALL)
		# #Layout sizers
		self.SetSizer(self.sizer)
		self.SetAutoLayout(1)
		self.Show()
		
		#STATUS BAR & TIMERS
		self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
		self.statusBar.SetStatusText("Welcome to the Uniquity File Scanner!")
		self.STATUS_TIMER_ID = 0
		
		self.UPDATE_INTERVAL = config.GUI_UPDATE_INTERVAL
		self.UPDATE_TIMER_ID = 1
		self.updateTimer = wx.Timer(self, self.UPDATE_TIMER_ID) 
		wx.EVT_TIMER(self, self.UPDATE_TIMER_ID, self.timerUpdate)  # call the on_timer function
		self.updateTimer.Start(self.UPDATE_INTERVAL)
		self.duplicateFiles = 0
		
	def setDupView(self, view):
		self.dupView = view
		self.mainSplitter.SplitVertically(self.directoryView, self.dupView)
		#SetMinimumPaneSize stops the splitter from being closed by the user
		self.mainSplitter.SetMinimumPaneSize(20)
		#Combine the top (toolbar) and bottom (everything else) into the master
		#We will re-split the toolbar when we have dup files to show the user
		self.mainSplitter.Unsplit(self.dupView)
		

	#############
	# WX Events #
	#############
	
	#Add files via drag and drop
	def OnDropFiles(self, x, y, filenames):
		if filenames:
			pub.sendMessage("main.addfiles", files=filenames)
			
	def OnClose(self, e):
		#We could have an 'are you sure' dialogue here if we wanted.
		self.Destroy()
		
	################
	# View Methods #
	################

	def addFile(self, e):
		theFile = None
		dirname = "."
		""" Open a file"""
		dlg = wx.DirDialog(self, "Choose a directory to scan", os.path.expanduser('~'))
		if dlg.ShowModal() == wx.ID_OK:
			theFile = dlg.GetPath()
		dlg.Destroy()
		pub.sendMessage("main.addfiles", files=[theFile])

	def removeFiles(self, e):
		pub.sendMessage("main.removefiles", files=self.directoryView.getSelected())
		
	def viewFiles(self, e):
		pub.sendMessage("main.viewdupfiles")
		
	def deleteFiles(self, e):
		pub.sendMessage("main.deletedupfiles")
		
	def timerUpdate(self, e):
		pub.sendMessage("main.updaterequest")
		self.updateTimer.Start(self.UPDATE_INTERVAL)
		
	def dirsSelected(self, e):
		self.toolbar.EnableTool(wx.ID_REMOVE, True)
		
	def dirsDeselected(self, e):
		if len(self.directoryView.getSelected()) == 0:
			self.toolbar.EnableTool(wx.ID_REMOVE, False)
			
	def enableDupFileTools(self):
		self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, True)
		self.toolbar.EnableTool(wx.ID_DELETE, True)
		
	def disableDupFileTools(self):
		self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.toolbar.EnableTool(wx.ID_DELETE, False)
			
	#Will fail if dup view has not been added
	def splitView(self):
		self.mainSplitter.SplitVertically(self.directoryView, self.dupView)

	def unsplitView(self):
		self.mainSplitter.Unsplit(self.mainDupView)
		
	def updateDirView(self, files):
		self.directoryView.updateView(files)
		
	def updateUpdatePanel(self, newinfo):
		self.updatePanel.updateProgress(newinfo)

	def status(self, text):
		self.statusBar.SetStatusText(text)
		self.statusBar.Refresh()

	def statusError(self, error):
		self.timer = wx.Timer(self, self.STATUS_TIMER_ID)  # message will be sent to the panel
		self.timer.Start(2000)  # x100 milliseconds
		wx.EVT_TIMER(self, self.STATUS_TIMER_ID, self.__resetStatusBar)  # call the on_timer function
		self.statusBar.SetStatusText(error)
		self.statusBar.SetBackgroundColour("RED")
		self.statusBar.Refresh()
		
	def __resetStatusBar(self, event):
		self.statusBar.SetBackgroundColour("WHITE")
		self.statusBar.Refresh()			
