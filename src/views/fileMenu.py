import wx


class FileMenu(wx.MenuBar):
	
	def __init__(self):
		wx.MenuBar.__init__(self)
		
		
		#File menu bar
		self.file = wx.Menu()
		self.add = self.file.Append(wx.NewId(), "&Add Files\tCtrl+N", "Add a new Folder to scan.")
		self.remove = self.file.Append(wx.NewId(), "&Remove Files", "Remove a folder from the scan list.")
		self.file.AppendSeparator()
		self.about = self.file.Append(wx.NewId(), "&About", "About Uniquity")		
		self.file.AppendSeparator()
		self.quit = self.file.Append(wx.NewId(), "&Quit\tCtrl+Q", "Quit Uniquity")
		self.Append(self.file, "&File")
		
		self.edit = wx.Menu()
		self.delete = self.edit.Append(wx.NewId(), "&Delete File\tCtrl+D")
		self.Append(self.edit, "&Edit")
		
		self.view = wx.Menu()
		self.fileFormat = wx.Menu()
		self.fullName = self.fileFormat.Append(wx.NewId(), "&Full name", "Show the full path for files", wx.ITEM_RADIO)
		self.shortName = self.fileFormat.Append(wx.NewId(), "&Short name", "Show a shorter path for files, based on directories scanned", wx.ITEM_RADIO)
		self.baseName = self.fileFormat.Append(wx.NewId(), "&Base name", "Show only filenames", wx.ITEM_RADIO)
		self.view.AppendMenu(wx.NewId(), "File Format", self.fileFormat)
		self.viewFile = self.view.Append(wx.NewId(), "&Reveal in Finder")
		self.Append(self.view, "&View")
		
			