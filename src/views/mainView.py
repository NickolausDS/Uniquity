import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import os
import sys

import time
import threading

import controller

from data.config import *
from directoryView import DirectoryView
from fileMenu import FileMenu

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname=''

		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.
		wx.Frame.__init__(self, parent, title=title, size=(800,600))

		self.controller = controller.Controller(self)

		#setup drag and drop. It fires when someone drags a file onto the main window
		#and calls the method "addFiles"
		self.dt = DragAndDrop(self, self.controller.addFiles)
		self.SetDropTarget(self.dt)

		self.mainSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH, size=(300,300))

		#All the setup, spread out into several methods
		# self.setupFileMenu()	
		self.fileMenu = FileMenu(self)
		self.setupToolbar()
		# self.setupDirectoryPanel(mainSplitter)

		self.directoryView = DirectoryView(self.mainSplitter, self.controller.scanObjects, self.toolbar)
		#self.setupTabbedOutputDisplay(mainSplitter)
		
		#SETUP TABBED OUTPUT DISPLAY
		self.tabHolder = wx.Notebook(self.mainSplitter, -1, style=(wx.NB_TOP))
		
		# font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		# font.SetPointSize(12)
		
		self.dupFilePanel = wx.Panel(self.tabHolder)
		self.dupFileSizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.dupFileOutput = wx.ListCtrl(self.dupFilePanel, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.enableDupFileTools, self.dupFileOutput)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.disableDupFileTools, self.dupFileOutput)
		self.dupFileSizer.Add(self.dupFileOutput, 100, flag=wx.EXPAND | wx.ALL)
		self.dupFilePanel.SetSizer(self.dupFileSizer)
		
		
		self.filesSkippedOutput = wx.TextCtrl(self.tabHolder, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		self.tabHolder.AddPage(self.dupFilePanel, "Duplicate Files Found")
		self.tabHolder.AddPage(self.filesSkippedOutput, "Files Skipped")
		
		#Put all errors on this pane
		method = lambda string: self.filesSkippedOutput.AppendText(string)
		self.controller.log.warning = method
		self.controller.log.error = method
		self.controller.log.critical = method
		
		##PUT MAIN GUI TOGETHER
		self.mainSplitter.SplitVertically(self.directoryView, self.tabHolder)
		#SetMinimumPaneSize stops the splitter from being closed by the user
		self.mainSplitter.SetMinimumPaneSize(20)
		#Combine the top (toolbar) and bottom (everything else) into the master
		#We will re-split the toolbar when we have dup files to show the user
		self.mainSplitter.Unsplit(self.tabHolder)
		
		self.progressPanel = wx.Panel(self)
		self.progressGauge = wx.Gauge(self.progressPanel, -1, 100, size=(250,25))
		self.progressCompletion = wx.StaticText(self.progressPanel, label="Progress Completion:")
		# We should probably change this to textctrl later
		# self.progressInfo = wx.TextCtrl(self.progressPanel, -1, style=wx.TE_READONLY | wx.BORDER_NONE)
		self.progressInfo = wx.StaticText(self.progressPanel, label="File: ")
		self.progressSizer = wx.BoxSizer(wx.VERTICAL)
		
		# method = lambda string: self.progressInfo.SetLabelText(string)
		# self.controller.log.debug = method
		# self.controller.log.info = method
		
		self.progressSizer.Add(self.progressCompletion, 0, wx.EXPAND | wx.ALL, 10)
		self.progressSizer.Add(self.progressGauge, 0, wx.EXPAND | wx.ALL, 10)
		self.progressSizer.Add(self.progressInfo, 0, wx.EXPAND | wx.ALL, 10)
		self.progressPanel.SetSizer(self.progressSizer)
		# self.progressPanel.SetBackgroundColour('#4f5049')
		        

		self.masterSizer = wx.BoxSizer(wx.VERTICAL)
		paddingPanel = wx.Panel(self, size=(0,20))
		self.masterSizer.Add(paddingPanel, 0)
		self.masterSizer.Add(self.mainSplitter, 1, wx.EXPAND)
		self.masterSizer.Add(self.progressPanel, 0, wx.EXPAND | wx.ALL)
		# #Layout sizers
		self.SetSizer(self.masterSizer)
		self.SetAutoLayout(1)
		self.Show()
		
		#STATUS BAR
		self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
		# method = lambda text: self.statusBar.SetStatusText(text)
		# self.controller.log.debug = method
		# self.controller.log.info = method
		self.statusBar.SetStatusText("Welcome to the Uniquity File Scanner!")
		
	def setupFileMenu(self):
		# Setting up the menu.
		pass
		

	def setupToolbar(self):
		self.toolbar = self.CreateToolBar()
		#We add noLog in order to suspend wxlogging for a short time.
		#The reason is that it now gives a bogus error to the end user about the pngs we are
		#about to load. We want to keep that from happening. Delete noLog after adding menu items
		noLog = wx.LogNull()
		
		
		start = self.toolbar.AddLabelTool(wx.ID_ANY, 'Start', wx.Bitmap(IMAGE_DIR+'start_icon.png'))
		self.toolbar.AddSeparator()
		addFile = self.toolbar.AddLabelTool(wx.ID_ADD, 'Add File', wx.Bitmap(IMAGE_DIR+'add_icon.png'))
		removeFile = self.toolbar.AddLabelTool(wx.ID_REMOVE, 'Remove File', wx.Bitmap(IMAGE_DIR+'remove_icon.png'))
		self.toolbar.EnableTool(wx.ID_REMOVE, False)
		
		
		self.toolbar.AddSeparator()
		viewFile = self.toolbar.AddLabelTool(wx.ID_VIEW_DETAILS, 'View File', wx.Bitmap(IMAGE_DIR+'view_icon.png'))
		deleteFile = self.toolbar.AddLabelTool(wx.ID_DELETE, 'Delete File', wx.Bitmap(IMAGE_DIR+'delete_icon.png'))
		#We will disable both tools until we can use them
		self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.toolbar.EnableTool(wx.ID_DELETE, False)
		
		#show the toolbar
		self.toolbar.Realize()
		
		#re-enable logging
		del noLog

		#Bind all the methods to the toolbar buttons
		self.Bind(wx.EVT_TOOL, self.startScanning, start)
		self.Bind(wx.EVT_TOOL, self.controller.toolbarAddFiles, addFile)
		
		self.Bind(wx.EVT_TOOL, self.controller.toolbarRemoveFile, removeFile)
		self.Bind(wx.EVT_TOOL, self.controller.toolbarViewFile, viewFile)
		self.Bind(wx.EVT_TOOL, self.controller.toolbarDeleteFile, deleteFile)
		
		
	def startScanning(self, e):
		if self.controller.toolbarStart(e):
			self.mainSplitter.SplitVertically(self.directoryView, self.tabHolder)
		else:
			self.printStatusError("Add files in order to start scanning")

	def printStatus(self, text):
		self.statusBar.SetStatusText(text)
		self.statusBar.Refresh()

	def printStatusError(self, error):
		class ResetStatusBarTimer(threading.Thread):
			def __init__(self, milliseconds, statusBar):
				threading.Thread.__init__(self)
				self.milliseconds = milliseconds
				self.statusBar = statusBar

			def run(self):
				time.sleep(self.milliseconds / 1000.0)
				self.statusBar.SetBackgroundColour("WHITE")
				self.statusBar.Refresh()
				del self
				
		self.statusBar.SetStatusText(error)
		self.statusBar.SetBackgroundColour("RED")
		self.statusBar.Refresh()
		sbr = ResetStatusBarTimer(1500, self.statusBar)
		sbr.start()
		
	def OnQuit(self, e):
		self.Close()

	def enableDupFileTools(self, e):
		if self.controller.getSelectedDups():
			self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, True)
			self.toolbar.EnableTool(wx.ID_DELETE, True)
		
	def disableDupFileTools(self, e):
		self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.toolbar.EnableTool(wx.ID_DELETE, False)
		
	
	def updateProgressBar(self, percent, currentFile=None):
		self.progressGauge.SetValue(percent)
		# if currentFile:
		print currentFile
		self.progressInfo.SetLabel("File: " + currentFile)
		self.progressInfo.Update()
		# self.progressSizer.Layout()

class ResizingListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
		# CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)
		
class DragAndDrop(wx.FileDropTarget):
	def __init__(self, window, callbackFunct):
		wx.FileDropTarget.__init__(self)
		self.callbackFunct = callbackFunct

	def OnDropFiles(self, x, y, filenames):
		#Yep, that's literally all we do.
		self.callbackFunct(filenames)

				
