import wx

import controller

from data.config import *
from directoryView import DirectoryView
from fileMenu import FileMenu
from toolbar import Toolbar
import updatePanel

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname=''

		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.
		wx.Frame.__init__(self, parent, title=title, size=(800,600))
		self.controller = controller.Controller(self)
		self.Bind(wx.EVT_CLOSE, self.OnClose)

		#setup drag and drop. It fires when someone drags a file onto the main window
		#and calls the method "addFiles"
		self.dt = DragAndDrop(self, self.controller.addFiles)
		self.SetDropTarget(self.dt)

		#Our main view objects
		self.fileMenu = FileMenu(self)
		self.toolbar = Toolbar(self, self.controller)
		self.updatePanel = updatePanel.UpdatePanel(self)
		
		
		self.mainSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH, size=(300,300))
		self.directoryView = DirectoryView(self.mainSplitter, self.controller.hashObjects, self.toolbar)
		self.tabHolder = wx.Notebook(self.mainSplitter, -1, style=(wx.NB_TOP))
		
		#SETUP TABBED OUTPUT DISPLAY
		
		# font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		# font.SetPointSize(12)
		
		self.dupFilePanel = wx.Panel(self.tabHolder)
		self.dupFileSizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.dupFileOutput = wx.ListCtrl(self.dupFilePanel, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
		self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.toolbar.enableDupFileTools, self.dupFileOutput)
		self.Bind(wx.EVT_LIST_ITEM_DESELECTED, self.toolbar.disableDupFileTools, self.dupFileOutput)
		self.dupFileSizer.Add(self.dupFileOutput, 100, flag=wx.EXPAND | wx.ALL)
		self.dupFilePanel.SetSizer(self.dupFileSizer)
		
		
		# self.filesSkippedOutput = wx.TextCtrl(self.tabHolder, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		self.tabHolder.AddPage(self.dupFilePanel, "Duplicate Files Found")
		# self.tabHolder.AddPage(self.filesSkippedOutput, "Files Skipped")
		
		
		##PUT MAIN GUI TOGETHER
		self.mainSplitter.SplitVertically(self.directoryView, self.tabHolder)
		#SetMinimumPaneSize stops the splitter from being closed by the user
		self.mainSplitter.SetMinimumPaneSize(20)
		#Combine the top (toolbar) and bottom (everything else) into the master
		#We will re-split the toolbar when we have dup files to show the user
		self.mainSplitter.Unsplit(self.tabHolder)		        

		self.masterSizer = wx.BoxSizer(wx.VERTICAL)
		paddingPanel = wx.Panel(self, size=(0,20))
		self.masterSizer.Add(paddingPanel, 0)
		self.masterSizer.Add(self.mainSplitter, 1, wx.EXPAND)
		self.masterSizer.Add(self.updatePanel, 0, wx.EXPAND | wx.ALL, 10)
		# self.masterSizer.Add(self.progressPanel, 0, wx.EXPAND | wx.ALL)
		# #Layout sizers
		self.SetSizer(self.masterSizer)
		self.SetAutoLayout(1)
		self.Show()
		
		#STATUS BAR
		self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
		self.statusBar.SetStatusText("Welcome to the Uniquity File Scanner!")
		self.STATUS_TIMER_ID = 0
		
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
		self.timer = wx.Timer(self, self.STATUS_TIMER_ID)  # message will be sent to the panel
		self.timer.Start(2000)  # x100 milliseconds
		wx.EVT_TIMER(self, self.STATUS_TIMER_ID, self.__resetStatusBar)  # call the on_timer function
		self.statusBar.SetStatusText(error)
		self.statusBar.SetBackgroundColour("RED")
		self.statusBar.Refresh()
		
	def __resetStatusBar(self, event):
		self.statusBar.SetBackgroundColour("WHITE")
		self.statusBar.Refresh()
		
	def OnClose(self, e):
		#We could have an 'are you sure' dialogue here if we wanted.
		self.controller.shutdown()
		self.Destroy()
		
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

				
