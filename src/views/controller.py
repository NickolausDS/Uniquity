import models.uniquity as uniquity
import wx
import logging

import data.config as config
#This also has the effect of setting up console logging, for now
import views.logger
import mainView
import dupViewController

from wx.lib.pubsub import pub

class Controller(object):
	
	def __init__(self):	
		#Setup the logger
		self.log = logging.getLogger('.'.join((config.GUI_LOG_NAME, 'controller')))
			
		#Setup the view
		app = wx.App(False)
		self.mainView = mainView.MainWindow(None, "Uniquity -- The Unique File Analyzer")
		
		#Setup various events we will respond to
		pub.subscribe(self.addFiles, "main.addfiles")
		pub.subscribe(self.removeFiles, "main.removefiles")
		pub.subscribe(self.updateViewProgress, "main.updaterequest")
		
		#Setup the model. Setting it up after the view is convienient, as no model code
		#will run if the view has a sudden crash (happens when testing new views)
		self.uniquity = uniquity.Uniquity()
		
		#Setup DupVC (for showing duplicate files)
		self.dupVC = dupViewController.DupViewController(self.uniquity, self.mainView.mainSplitter)
		self.mainView.setDupView(self.dupVC.view)
		
		#Run the main gui loop
		app.MainLoop()
		
		#We are finished, release all model resources
		self.uniquity.shutdown()
	
	#Returns False on success, or the name of the file on failure (file already added)
	def __addFile(self, filename):
		if self.uniquity.addFile(filename):
			return False
		return filename
	
	#Add new files or directories to scan with uniquity
	def addFiles(self, files):
		if not files:
			return
		
		errors = []
		successes = []
		for each in files:
			error = self.__addFile(each)
			if error:
				errors.append(error)
			else:
				successes.append(each)
		
		msg = ""
		if successes:
			msg += "Added: %s. " % ", ".join(successes)
		if errors:
			msg += "Already added: %s." % ", ".join(errors)
			self.mainView.statusError(msg)
		else:
			self.mainView.status(msg)
		self.log.info(msg)	
		
		self.mainView.splitView()
		self.mainView.updateDirView(self.uniquity.getFiles())
		
	
	#Remove files or directories from the list of hashObjects to scan with uniqutiy.		
	def removeFiles(self, files):
		if not files:
			return
		
		rc = self.uniquity.removeFiles(files)
		junk = zip(rc, files)
		errors = [afile for ers, afile in junk if not ers]
		sucs = [afile for sucs, afile in junk if sucs]
		msg = ""
		if sucs:
			msg = "Removed: " + ", ".join(sucs)
		if errors:
			msg += "Failed to remove: " + ", ".join(errors)
			self.mainView.statusError(msg)
		else:
			self.mainView.status(msg)
		self.log.info(msg)
		
		self.mainView.updateDirView(self.uniquity.getFiles())
		
	def updateViewProgress(self):
		self.mainView.updateUpdatePanel(self.uniquity.getUpdate())
		self.dupVC.update()
	