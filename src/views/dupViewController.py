import wx
import sys
import subprocess
from wx.lib.pubsub import pub
import logging

import data.config as config
import mainDupView
from models.schema import FILE

class DupViewController(object):
	
	def __init__(self, model, viewParent):
		self.log = logging.getLogger('.'.join((config.GUI_LOG_NAME, 'dupController.controller')))
		
		self.uniquity = model
		
		self.fileFormat = [i[0] for i in FILE]
		self.itemMap = (
				self.fileFormat.index("shortname"),
				self.fileFormat.index("niceSizeAndDesc"),
				self.fileFormat.index("strongHash")
			)
		self.uidFunction = lambda x: x[0]
		
		#We don't need to hold on to the parent, just initialize from it.
		self.view = mainDupView.MainDupView(viewParent, self.itemMap, self.uidFunction)
		self.stats = self.uniquity.getUpdate()
			
	def getFilename(self, fileobj):
		return fileobj[0]
		
	def update(self):
		newStats = self.uniquity.getUpdate()
		if self.stats != newStats:
			self.stats = newStats
			newData = self.uniquity.getDuplicateFiles(onlyReturnNewData=True)
			if newData:	
				self.log.debug("Model returned new Duplicate data, updating View!")
				self.view.update(newData)
			
	def viewSelected(self):
		#We only support opening one file at a time
		selected = self.view.getSelected()
		if selected:
			selection = selected.pop()
			if sys.platform == "win32":
				os.startfile(self.getFilename(selected))
			elif sys.platform == "darwin":
				ret = subprocess.Popen(['open', '-R', self.getFilename(selection)])
				self.log.info("revealed %s on mac, with ret call: %s", self.getFilename(selection), str(ret))
			else:
				pub.sendMessage("dupview.stautserror", 
					error="I'm sorry, but this command is not available for your current platform.")
		else:
			pub.sendMessage("dupview.statuserror",
				error="Select a file in the duplicate list to view it")

		
	def deleteSelected(self):
		toDelete = self.view.getSelected()
		if toDelete:
			message = "Are you sure you want to delete these files:\n"
			message += "\n".join([self.getFilename(files) for files in toDelete])
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
						os.remove(self.getFilename(theFile))
					except Exception as e:
						self.log.exception(e)
						pub.sendMessage("dupview.error","Could not delete '%s'.", self.getFilename(theFile))
		else:
			pub.sendMessage("dupview.error", error="Select one or more duplicate files from the list to delete.")
				