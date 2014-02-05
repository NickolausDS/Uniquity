import wx
from wx.lib.mixins.listctrl import CheckListCtrlMixin, ListCtrlAutoWidthMixin
import os
import sys

import time
import threading

import guicommands


if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    BASEPATH = sys._MEIPASS
else:
    # we are running in a normal Python environment
    BASEPATH = os.path.dirname(__file__)

IMAGE_DIR=os.path.join(BASEPATH, "assets" + os.path.sep)


class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname=''

		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.
		wx.Frame.__init__(self, parent, title=title, size=(800,600))
		
		self.command = guicommands.GuiCommands(self)

		self.mainSplitter = wx.SplitterWindow(self, -1, style=wx.SP_3DSASH, size=(300,300))

		#All the setup, spread out into several methods
		self.setupFileMenu()	
		self.setupToolbar()
		# self.setupDirectoryPanel(mainSplitter)
		
		#SETUP DIRECTORY PANEL
		self.directoryPanel = wx.Panel(self.mainSplitter)
		self.directoryPanelSizer = wx.BoxSizer(wx.VERTICAL)
		#self.directoryListings = wx.TextCtrl(self.directoryPanel, style=wx.TE_MULTILINE|wx.TE_READONLY)
		#self.lc1 = wx.ListCtrl(splitter2, -1, style=wx.LC_LIST)
		self.directoryListings = wx.ListCtrl(self.directoryPanel, -1, style=wx.LC_LIST)
		title = wx.StaticText(self.directoryPanel, label='Files')
		self.directoryPanelSizer.Add(title, 0, wx.ALIGN_CENTER|wx.BOTTOM)
		self.directoryPanelSizer.Add(self.directoryListings, 100, border=10, flag= wx.EXPAND|wx.ALL|wx.ALIGN_TOP)
		self.directoryPanel.SetSizer(self.directoryPanelSizer)
		
		#self.setupTabbedOutputDisplay(mainSplitter)
		
		#SETUP TABBED OUTPUT DISPLAY
		self.tabHolder = wx.Notebook(self.mainSplitter, -1, style=(wx.NB_TOP))
		
		# font = wx.SystemSettings_GetFont(wx.SYS_SYSTEM_FONT)
		# font.SetPointSize(12)
		
		self.dupFilePanel = wx.Panel(self.tabHolder)
		self.dupFileSizer = wx.BoxSizer(wx.HORIZONTAL)		
		self.dupFileOutput = wx.ListCtrl(self.dupFilePanel, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
		self.dupFileSizer.Add(self.dupFileOutput, 100, flag=wx.EXPAND | wx.ALL)
		self.dupFilePanel.SetSizer(self.dupFileSizer)
		
		
		self.filesSkippedOutput = wx.TextCtrl(self.tabHolder, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		self.tabHolder.AddPage(self.dupFilePanel, "Duplicate Files Found")
		self.tabHolder.AddPage(self.filesSkippedOutput, "Files Skipped")
		
		#Put all errors on this pane
		method = lambda string: self.filesSkippedOutput.AppendText(string)
		self.command.log.warning = method
		self.command.log.error = method
		self.command.log.critical = method

		##PUT MAIN GUI TOGETHER
		self.mainSplitter.SplitVertically(self.directoryPanel, self.tabHolder)
		#SetMinimumPaneSize stops the splitter from being closed by the user
		self.mainSplitter.SetMinimumPaneSize(20)
		#Combine the top (toolbar) and bottom (everything else) into the master
		self.mainSplitter.Unsplit(self.tabHolder)

		# self.progressPanel = wx.Panel(self)
		# self.progressGauge = wx.Gauge(self.progressPanel, -1, 100, size=(250,25))
		# self.progressCompletion = wx.StaticText(self.progressPanel, label="Progress Completion:")
		# self.progressInfo = wx.StaticText(self.progressPanel, label="File: ")
		# self.progressSizer = wx.BoxSizer(wx.VERTICAL)
		# 
		# self.progressSizer.Add(self.progressCompletion, 0, wx.EXPAND | wx.ALL, 10)
		# self.progressSizer.Add(self.progressGauge, 0, wx.EXPAND | wx.ALL, 10)
		# self.progressSizer.Add(self.progressInfo, 0, wx.EXPAND | wx.ALL, 10)
		# self.progressPanel.SetSizer(self.progressSizer)
		# self.progressPanel.SetBackgroundColour('#4f5049')
        

		self.masterSizer = wx.BoxSizer(wx.VERTICAL)
		paddingPanel = wx.Panel(self, size=(0,20))
		self.masterSizer.Add(paddingPanel, 0)
		self.masterSizer.Add(self.mainSplitter, 1, wx.EXPAND)
		# self.masterSizer.Add(self.progressPanel, 0, wx.EXPAND | wx.ALL)
		# #Layout sizers
		self.SetSizer(self.masterSizer)
		self.SetAutoLayout(1)
		self.Show()
		
		#STATUS BAR
		self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
		self.command.log.debug = lambda text: self.statusBar.SetStatusText(text)
		self.command.log.info = lambda text: self.statusBar.SetStatusText(text)
		self.statusBar.SetStatusText("Welcome to the Uniquity File Scanner!")
		
		
	
	
	def setupFileMenu(self):
		# Setting up the menu.
		filemenu= wx.Menu()
		#menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
		menuNew = filemenu.Append(wx.ID_NEW, "&New", "Empty the current list of scanned files and start again")
		# menuAdd = filemenu.Append(wx.ID_ADD, "Add", "Add a new directory")
		menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
		
		editMenu = wx.Menu()
		editMenu.Append(wx.ID_PASTE, "&Paste", "Paste a file path to be scanned")
		
		viewMenu = wx.Menu()
		viewMenu.Append(wx.ID_ANY, "Show Hash", "Show the resulting hash for each duplicate file displayed")
		
		helpMenu = wx.Menu()
		helpMenu.Append(wx.ID_ANY, "Quick Help", "A very simple quick start guide for using Uniquity")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		# menuBar.Append(editMenu,"Edit")
		# menuBar.Append(viewMenu,"View")
		menuBar.Append(helpMenu,"Help")
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		# Events.
		# self.Bind(wx.EVT_MENU, self.command.fileMenuOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.command.fileMenuNew, menuNew)
		# self.Bind(wx.EVT_MENU, self.command.toolbarMenuAdd, menuAdd)
		self.Bind(wx.EVT_MENU, self.command.fileMenuExit, menuExit)
		self.Bind(wx.EVT_MENU, self.command.fileMenuAbout, menuAbout)
		

	def setupToolbar(self):
		# self.toolbarSizer = wx.BoxSizer(wx.HORIZONTAL)
		#original buttons are here, but won't be used yet
		#toolbarButtontexts = [">", "+", "-", "X", "^-^"]
		toolbar = self.CreateToolBar()
		#We add noLog in order to suspend wxlogging for a short time.
		#The reason is that it now gives a bogus error to the end user about the pngs we are
		#about to load. We want to keep that from happening. Delete noLog after adding menu items
		noLog = wx.LogNull()
		start = toolbar.AddLabelTool(wx.ID_ANY, 'Start', wx.Bitmap(IMAGE_DIR+'start_icon.png'))
		toolbar.AddSeparator()
		addFile = toolbar.AddLabelTool(wx.ID_ANY, 'Add File', wx.Bitmap(IMAGE_DIR+'add_icon.png'))
		removeFile = toolbar.AddLabelTool(wx.ID_ANY, 'Remove File', wx.Bitmap(IMAGE_DIR+'remove_icon.png'))
		
		toolbar.AddSeparator()
		viewFile = toolbar.AddLabelTool(wx.ID_ANY, 'View File', wx.Bitmap(IMAGE_DIR+'view_icon.png'))
		deleteFile = toolbar.AddLabelTool(wx.ID_ANY, 'Delete File', wx.Bitmap(IMAGE_DIR+'delete_icon.png'))

		#We need the id's to be specific for this command to work
		#toolbar.EnableTool(wx.ID_ANY, False)
		# qtool = toolbar.AddLabelTool(wx.ID_ANY, 'Quit', wx.Bitmap(IMAGE_DIR+'view_icon.png'))
		toolbar.Realize()
		del noLog

		self.Bind(wx.EVT_TOOL, self.startScanning, start)
		self.Bind(wx.EVT_TOOL, self.command.toolbarAddFiles, addFile)
		
		self.Bind(wx.EVT_TOOL, self.command.toolbarRemoveFile, removeFile)
		self.Bind(wx.EVT_TOOL, self.command.toolbarViewFile, viewFile)
		self.Bind(wx.EVT_TOOL, self.command.toolbarDeleteFile, deleteFile)
		
		
	def startScanning(self, e):
		if self.command.toolbarStart(e):
			self.mainSplitter.SplitVertically(self.directoryPanel, self.tabHolder)
		else:
			self.printStatusError("Add files in order to start scanning")

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

class ResizingListCtrl(wx.ListCtrl, ListCtrlAutoWidthMixin):
	def __init__(self, parent):
		wx.ListCtrl.__init__(self, parent, -1, style=wx.LC_REPORT | wx.LC_NO_HEADER)
		# CheckListCtrlMixin.__init__(self)
		ListCtrlAutoWidthMixin.__init__(self)
				
