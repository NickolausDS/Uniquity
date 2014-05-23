import wx
import os
import sys
import subprocess
from wx.lib.pubsub import pub


import logging

from data.config import IMAGE_DIR

class Toolbar(wx.ToolBar):

	def __init__(self, parent):
		wx.ToolBar.__init__(self, parent)
		self.parent = parent
		
		self.parent.SetToolBar(self)

		#We add noLog in order to suspend wxlogging for a short time.
		#The reason is that it now gives a bogus error to the end user about the pngs we are
		#about to load. We want to keep that from happening. Delete noLog after adding menu items
		noLog = wx.LogNull()

		# self.start = self.AddLabelTool(wx.ID_ANY, 'Start', self.__loadImage('start_icon.png'))
		# self.AddSeparator()

		self.add = self.AddLabelTool(wx.ID_ADD, 'Add File', self.__loadImage('add_icon.png'))
		self.remove = self.AddLabelTool(wx.ID_REMOVE, 'Remove File', self.__loadImage('remove_icon.png'))
		self.EnableTool(wx.ID_REMOVE, False)
		self.AddSeparator()
		
		self.view = self.AddLabelTool(wx.ID_VIEW_DETAILS, 'View File', self.__loadImage('view_icon.png'))
		self.delete = self.AddLabelTool(wx.ID_DELETE, 'Delete File', self.__loadImage('delete_icon.png'))
		#We will disable both tools until we can use them
		self.EnableTool(wx.ID_VIEW_DETAILS, False)
		self.EnableTool(wx.ID_DELETE, False)

		# #show the toolbar
		self.Realize()

		#re-enable logging
		del noLog

	def __loadImage(self, filename):
		fullpath = os.path.join(IMAGE_DIR, filename)
		#wxPython will throw a terrible tissy fit if it tries to load a file that doesn't exist.
		if not os.path.exists(fullpath):
			raise ValueError("Failed to load image %s!" % os.path.abspath(fullpath))
		return wx.Bitmap(fullpath)

		