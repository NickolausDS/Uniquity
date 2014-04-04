import wx
import os
import sys
import subprocess

import logging

from data.config import IMAGE_DIR as BASE_IMAGE_DIR

#This is a hack, since I don't have time to figure out how this should be set in 
#the config. 
if getattr(sys, 'frozen', False):
    # we are running in a |PyInstaller| bundle
    BASEPATH = sys._MEIPASS
else:
	# we are running in a normal Python environment
	BASEPATH = os.path.dirname(__file__)
	BASEPATH = os.path.abspath(os.path.join(BASEPATH, os.pardir))

IMAGE_DIR = os.path.join(BASEPATH, BASE_IMAGE_DIR)

class Toolbar(wx.ToolBar):

	def __init__(self, parent, controller):
		wx.ToolBar.__init__(self, parent)
		self.parent = parent
		self.controller = controller
		
		self.parent.SetToolBar(self)

		#We add noLog in order to suspend wxlogging for a short time.
		#The reason is that it now gives a bogus error to the end user about the pngs we are
		#about to load. We want to keep that from happening. Delete noLog after adding menu items
		noLog = wx.LogNull()

		start = self.AddLabelTool(wx.ID_ANY, 'Start', self.__loadImage('start_icon.png'))
		self.AddSeparator()

		addFile = self.AddLabelTool(wx.ID_ADD, 'Add File', self.__loadImage('add_icon.png'))
		removeFile = self.AddLabelTool(wx.ID_REMOVE, 'Remove File', self.__loadImage('remove_icon.png'))
		self.EnableTool(wx.ID_REMOVE, False)
		self.AddSeparator()
		
		viewFile = self.AddLabelTool(wx.ID_VIEW_DETAILS, 'View File', self.__loadImage('view_icon.png'))
		deleteFile = self.AddLabelTool(wx.ID_DELETE, 'Delete File', self.__loadImage('delete_icon.png'))
		#We will disable both tools until we can use them
		self.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.EnableTool(wx.ID_DELETE, False)

		# #show the toolbar
		self.Realize()

		#re-enable logging
		del noLog

		# Bind all the methods to the toolbar buttons
		self.Bind(wx.EVT_TOOL, self.startf, start)
		self.Bind(wx.EVT_TOOL, self.addFiles , addFile)
		self.Bind(wx.EVT_TOOL, self.removeFiles, removeFile)
		self.Bind(wx.EVT_TOOL, self.viewFiles, viewFile)
		self.Bind(wx.EVT_TOOL, self.deleteFiles, deleteFile)

	#TOOLBAR MENU EVENTS
	def startf(self, e):
		self.parent.start()

	def addFiles(self, e):
		self.parent.addFiles()

	def removeFiles(self, e):
		self.parent.removeFiles()

	def viewFiles(self, e):
		selected = self.controller.getSelectedDups()
		if not selected:
			self.parent.printStatusError("Select a file in the duplicate list to view it")
		else:
			#We only support opening one file at a time
			selection = selected[0]
			print "DEBUG: " + selection
			# selection = self.mainView.dupFileOutput.GetItemText(selected[0], 1)
			if sys.platform == "win32":
				os.startfile(selected[0])
			elif sys.platform == "darwin":
				subprocess.Popen(['open', '-R', selection])
			else:
				self.parent.printStatusERror("I'm sorry, but this tool failed to work for your current platform")

	def deleteFiles(self, e):
		toDelete = self.controller.getSelectedDups()
		if toDelete:
			message = "Are you sure you want to delete these files:\n"
			message += "\n".join(self.controller.getNiceDupNames(toDelete))
			title = "They will never bother you again."
			askDialog = wx.MessageDialog(None, 
										title, 
										message, 
										style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			result = askDialog.ShowModal()
			askDialog.Destroy()	
			if result == wx.ID_YES:
				for theFile in toDelete:
					try:
						os.remove(theFile)
						self.controller.setDupFileOutputBackgroundColor(theFile, "RED")
					except Exception as e:
						self.controller.setDupFileOutputBackgroundColor(theFile, "YELLOW")
						print str(e)
						self.parent.printStatusError("Could not delete '"+str(theFile)+"'.")
		else:
			self.parent.printStatusError("Select one or more duplicate files from the list to delete.")

	def enableDupFileTools(self, e):
		if self.controller.getSelectedDups():
			self.EnableTool(wx.ID_VIEW_DETAILS, True)
			self.EnableTool(wx.ID_DELETE, True)
		
	def disableDupFileTools(self, e):
		self.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.EnableTool(wx.ID_DELETE, False)

	def __loadImage(self, filename):
		fullpath = os.path.join(IMAGE_DIR, filename)
		#wxPython will throw a terrible tissy fit if it tries to load a file that doesn't exist.
		if not os.path.exists(fullpath):
			raise ValueError("Failed to load image %s!" % fullpath)
		return wx.Bitmap(fullpath)

		