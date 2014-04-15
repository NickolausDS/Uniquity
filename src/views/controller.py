import models.uniquity as uniquity
import wx
import logging
import os
import sys

import models.hashObject as hashObject
import data.config as config
#This also has the effect of setting up console logging, for now
import views.logger


# import thread

from cStringIO import StringIO


class Controller(object):
	
	def __init__(self, theMainWindow):
		self.mainView = theMainWindow
		
		#Set options (Consider using a dictionary)
		# self.MAXDIRDEPTH = 0
		# self.VERBOSITY = "NORMAL"
		# self.OUTPUTFORMAT = "LIST"
		# self.MAXFILESIZE = 0
		# self.HASHALG = "md5"
		# self.DEPTH = 0 #Zero means no max self.DEPTH (go forever)
		#Set data
		self.uniquity = uniquity.Uniquity()
		self.uniquity.setUpdateCallback(self.updateViewProgress)
		self.log = logging.getLogger('.'.join((config.GUI_LOG_NAME, 'controller')))
		#List of files and dirs we will scan with uniquity	
		self.hashObjects = []

		self.dupFileOutputMap = {}
		
		self.debug_update_calls = 0
	
	def start(self):		
		#We shouldn't need this bit when we're done with the refactor.
		#Just hand the scan objects stragiht to Uniqutiy
		files = []
		for each in self.hashObjects:
			files.append(each.getFilename())
		if not files:
			return False

		# self.mainView.updateProgressBar(0.0, "Preparing Scan...")
		self.uniquity.addFiles(files)
		self.uniquity.log.info("Finished.")
		return True
		
	def shutdown(self):
		self.uniquity.shutdown()

	
	#Add new files or directories to scan with uniquity
	def addFiles(self, files):
		for each in files:
			#Check if the user already added this file
			error = False
			for sos in self.hashObjects:
				if sos.getFilename() == each:
					self.mainView.printStatusError("Filename '" + each + "' already added!")
					error = True
					break
			if error == False:
				newSO = hashObject.HashObject(each)
				self.hashObjects.append(newSO)
				self.mainView.printStatus("Added '" + newSO.getFilename() + "'.")
		self.mainView.directoryView.updatePanel()

	
	#Remove files or directories from the list of hashObjects to scan with uniqutiy.		
	def removeFiles(self, files):
		for each in files:
			for so in self.hashObjects:
				if each == so.getFilename():
					self.hashObjects.remove(so)
					self.mainView.printStatus("Removed '" + each + "'.")
		self.mainView.directoryView.updatePanel()
	
	def getDuplicateFiles(self):
		return self.uniquity.getDuplicateFiles()
		
	def modelIsIdle(self):
		return self.uniquity.isIdle()
		
	def getUpdate(self):
		return self.uniquity.getUpdate()
		
	def updateViewProgress(self, args):
		self.debug_update_calls += 1
		self.log.debug("update calls: %d", self.debug_update_calls)
		# wx.CallAfter(self.mainView.updatePanel.updateProgress, args )
		# wx.CallAfter(self.refreshDuplicateFileOutput, args.get('hashedFiles', None))
		# theFile = kwargs.get('file', "")
		# percent = kwargs.get('percent', 0.0)
		# self.mainView.updateProgressBar(percent, self.getNiceDupName(theFile))
	