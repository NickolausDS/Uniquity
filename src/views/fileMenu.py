import wx


class FileMenu(wx.Menu):
	
	def __init__(self, parent):
		wx.Menu.__init__(self)
		self.parent = parent
		
		#menuOpen = self.Append(wx.ID_OPEN, "&Open"," Open a file to edit")
		# menuNew = self.Append(wx.ID_NEW, "&New", "Empty the current list of scanned files and start again")
		# menuAdd = self.Append(wx.ID_ADD, "Add", "Add a new directory")
		about = self.Append(wx.ID_ABOUT, "&About"," Information about this program")
		menuExit = self.Append(wx.ID_EXIT,"E&xit"," Terminate the program")
	
		editMenu = wx.Menu()
		editMenu.Append(wx.ID_PASTE, "&Paste", "Paste a file path to be scanned")
	
		viewMenu = wx.Menu()
		viewMenu.Append(wx.ID_ANY, "Show Hash", "Show the resulting hash for each duplicate file displayed")
	
		helpMenu = wx.Menu()
		helpMenu.Append(wx.ID_ANY, "Quick Help", "A very simple quick start guide for using Uniquity")

		# Creating the menubar.
		menuBar = wx.MenuBar()
		menuBar.Append(self,"&File") # Adding the "self" to the MenuBar
		# menuBar.Append(editMenu,"Edit")
		# menuBar.Append(viewMenu,"View")
		# menuBar.Append(helpMenu,"Help")
		parent.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.

		# Events.
		# self.Bind(wx.EVT_MENU, self.controller.selfOpen, menuOpen)
		# self.Bind(wx.EVT_MENU, self.controller.selfNew, menuNew)
		# # self.Bind(wx.EVT_MENU, self.controller.toolbarMenuAdd, menuAdd)
		# self.Bind(wx.EVT_MENU, self.controller.selfExit, menuExit)
		parent.Bind(wx.EVT_MENU, self.about, about)
	
	#DISABLED AS OF 2/24/2014
	#KEPT FOR REFERENCE
	#PLEASE DELETE WHEN FUNCTIONALITY HAS BEEN REBUILT	
	# def new(self, e):
	# 	#Set files to empty
	# 	self.files = []
	# 
	# 	#If the program is started up for the first time, this won't exist
	# 	try:
	# 		self.mainView.directoryListings.ClearAll()
	# 		self.mainView.mainSplitter.Unsplit(self.mainView.tabHolder)
	# 	except AttributeError:
	# 		pass
	# 





	def about(self,e):
		# Create a message dialog box
		message = "A program to find all of the duplicate files on your computer\n\n"
		message += "A creation by Nickolaus Saint at \nWindward Productions"
		dlg = wx.MessageDialog(self.parent, message, "About Uniquity", wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy() # finally destroy it when finished.

	def exit(self,e):
		# Create a message dialog box
		message = "Are you sure you want to exit?"
		dlg = wx.MessageDialog(self.parent, message, "Quit Uniquity?", wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy() # finally destroy it when finished.
		self.parent.Close(True)  # Close the frame.