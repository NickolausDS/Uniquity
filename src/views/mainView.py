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
from toolbar import Toolbar

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

		#Our main view objects
		self.fileMenu = FileMenu(self)
		self.toolbar = Toolbar(self, self.controller)
		
		self.mainSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH, size=(300,300))
		self.directoryView = DirectoryView(self.mainSplitter, self.controller.scanObjects, self.toolbar)
		self.tabHolder = wx.Notebook(self.mainSplitter, -1, style=(wx.NB_TOP))

		
		#SETUP TABBED OUTPUT DISPLAY
		
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
		self.statusBar.SetStatusText("Welcome to the Uniquity File Scanner!")
		
### COMMON METHODS ###
#These methods, start, addFiles, and RemoveFiles, are both used by the fileMenu and the
#Toolbar. Since neither object really *owns* the functionality, they are left here.

	def start(self):
		# self.updateProgressBar(0.0, "Preparing Scan...")
		if self.controller.start():
			self.mainSplitter.SplitVertically(self.directoryView, self.tabHolder)
			# self.updateProgressBar(100.0, "Finished!")
		else:
			self.printStatusError("Add files in order to start scanning")

		self.controller.refreshDuplicateFileOutput()
		return True

	def addFiles(self):
		dirname = "."
		""" Open a file"""
		dlg = wx.DirDialog(self, "Choose a Directory", ".")
		if dlg.ShowModal() == wx.ID_OK:
			self.controller.addFiles([dlg.GetPath()])
		dlg.Destroy()

	def removeFiles(self):
		selection = self.directoryView.getSelected()
		if not selection:
			self.mainView.printStatusError("Select a file or directory to remove it")
		else:
			self.controller.removeFiles(selection)

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

	#These should be moved to the toolbar object
	#They will once the dup flie view gets refactored
	def enableDupFileTools(self, e):
		if self.controller.getSelectedDups():
			self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, True)
			self.toolbar.EnableTool(wx.ID_DELETE, True)
		
	def disableDupFileTools(self, e):
		self.toolbar.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.toolbar.EnableTool(wx.ID_DELETE, False)
		
	
	def updateProgressBar(self, currentFile):
		# self.progressGauge.SetValue(percent)
		# if currentFile:
		# print currentFile
		self.progressInfo.SetLabel("File: " + str(currentFile))
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
		#So, when the drop happens, we get a list of filenames. We call
		#the callback function with the list of filenames, which *should*
		#be the addFiles() method in the controller.

				
