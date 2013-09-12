import wx
import os
import guicommands

class MainWindow(wx.Frame):
	def __init__(self, parent, title):
		self.dirname=''

		# A "-1" in the size parameter instructs wxWidgets to use the default size.
		# In this case, we select 200px width and the default height.
		wx.Frame.__init__(self, parent, title=title, size=(800,600))
		
		self.command = guicommands.GuiCommands(self)

		#All the setup, spread out into several methods
		self.setupFileMenu()	
		self.setupToolbar()
		self.setupDirectoryPanel()
		self.setupTabbedOutputDisplay()

		##PUT MAIN GUI TOGETHER
		self.bottomAreaSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.bottomAreaSizer.Add(self.directoryPanelSizer, 30, wx.EXPAND)
		self.bottomAreaSizer.Add(self.tabHolder, 70, wx.EXPAND)

		#Combine the top (toolbar) and bottom (everything else) into the master
		self.masterSizer = wx.BoxSizer(wx.VERTICAL)
		self.masterSizer.Add(self.toolbarSizer, 0, wx.EXPAND)
		self.masterSizer.Add(self.bottomAreaSizer, 1, wx.EXPAND)
		# #Layout sizers
		self.SetSizer(self.masterSizer)
		self.SetAutoLayout(1)
		self.masterSizer.Fit(self)
		self.Show()
		
		#STATUS BAR
		self.statusBar = self.CreateStatusBar() # A Statusbar in the bottom of the window
		self.command.log.debug = lambda text: self.statusBar.SetStatusText(text)
		self.command.log.info = lambda text: self.statusBar.SetStatusText(text)
		#self.statusBar.SetStatusText("HELLO WORLD")
		
	
	
	def setupFileMenu(self):
		# Setting up the menu.
		filemenu= wx.Menu()
		menuOpen = filemenu.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
		menuAbout= filemenu.Append(wx.ID_ABOUT, "&About"," Information about this program")
		menuExit = filemenu.Append(wx.ID_EXIT,"E&xit"," Terminate the program")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
		self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		# Events.
		self.Bind(wx.EVT_MENU, self.command.fileMenuOpen, menuOpen)
		self.Bind(wx.EVT_MENU, self.command.fileMenuExit, menuExit)
		self.Bind(wx.EVT_MENU, self.command.fileMenuAbout, menuAbout)
		
		

	def setupToolbar(self):
		self.toolbarSizer = wx.BoxSizer(wx.HORIZONTAL)
		#original buttons are here, but won't be used yet
		#toolbarButtontexts = [">", "+", "-", "X", "^-^"]
		toolbarButtontexts = [">", "+", "-", "X", "^-^"]
		self.toolbarButtons = []
		
		
		for i in toolbarButtontexts:
			self.toolbarButtons.append(wx.Button(self, -1, i, size=(64,32)))
		for i in self.toolbarButtons:
			self.toolbarSizer.Add(i, wx.EXPAND)
			
			
		self.Bind(wx.EVT_BUTTON, self.command.toolbarMenuAdd, self.toolbarButtons[0])
		

	def setupDirectoryPanel(self):
		# self.directoryPanel = wx.Panel(self)
		self.directoryPanelSizer = wx.BoxSizer(wx.VERTICAL)
		self.directoryListings = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
		title = wx.StaticText(self, label='Files')
		self.directoryPanelSizer.Add(title, 0, wx.ALIGN_CENTER|wx.BOTTOM)
		self.directoryPanelSizer.Add(self.directoryListings, 100, border=10, flag= wx.EXPAND|wx.ALL|wx.ALIGN_TOP)
		
	def setupTabbedOutputDisplay(self):
		#TABBED OUTPUT DISPLAY
		self.tabHolder = wx.Notebook(self, -1, style=(wx.NB_TOP))
		self.dupFileOutput = wx.TextCtrl(self.tabHolder, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.filesSkippedOutput = wx.TextCtrl(self.tabHolder, pos=(300,20), size=(200,300), style=wx.TE_MULTILINE | wx.TE_READONLY)
		
		self.tabHolder.AddPage(self.dupFileOutput, "Duplicate Files Found")
		self.tabHolder.AddPage(self.filesSkippedOutput, "Files Skipped")
		
		#Put all errors on this pane
		method = lambda string: self.filesSkippedOutput.AppendText(string)
		self.command.log.warning = method
		self.command.log.error = method
		self.command.log.critical = method

