"""
Main GUI module for Uniquity. 

This class is responsible for starting and stopping both the 'view'
and the 'model'. It is structured, as best as possible, in an MVC
design pattern. 'View' corresponds with GUI elements, and 'model' 
corresponds to the Uniquity backend responsible for scanning and
verifying information. Additionally, the 'controllers' are the glue
that hold together both the view and the model. 

See the Controller class for invoking the Uniquity GUI.
"""
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
	"""
	The controller is the main object for starting the Uniquity GUI.
	
	Calling init sets up both the view and the model. Afterward, the 
	mainLoop() method needs to be called in order for the GUI to run, 
	or it will exit instantaneously.
	"""
	
	def __init__(self):	
		#Setup the logger
		self.log = logging.getLogger('.'.join((config.GUI_LOG_NAME, 'controller')))
			
		#Setup the view
		self.app = wx.App(False)
		self.mainView = mainView.MainWindow(None, "Uniquity -- The Unique File Analyzer")
		
		#Setup the model. Setting it up after the view is convienient, as no model code
		#will run if the view has a sudden crash (happens when testing new views)
		self.uniquity = None
		try:
			self.uniquity = uniquity.Uniquity()
		except Exception as e:
			message = "Please install Uniquity before using it."
			diag = wx.MessageBox(message,style=wx.OK | wx.ICON_EXCLAMATION)
			self.mainView.Destroy()
			return
			
		
		#Setup DupVC (for showing duplicate files)
		self.dupVC = dupViewController.DupViewController(self.uniquity, self.mainView.mainSplitter)
		self.mainView.setDupView(self.dupVC.view)
		
		#Setup various events we will respond to
		pub.subscribe(self.addFiles, "main.addfiles")
		pub.subscribe(self.removeFiles, "main.removefiles")
		pub.subscribe(self.updateViewProgress, "main.updaterequest")
		pub.subscribe(self.mainView.enableDupFileTools, "dupview.itemselected")
		pub.subscribe(self.mainView.disableDupFileTools, "dupview.allitemsdeselected")
		pub.subscribe(self.mainView.status, "dupview.status")
		pub.subscribe(self.mainView.statusError, "dupview.statuserror")
		pub.subscribe(self.dupVC.viewSelected, "main.viewdupfiles")
		pub.subscribe(self.dupVC.deleteSelected, "main.deletedupfiles")
	
	def mainLoop(self):
		"""
		This runs the main thread for the GUI. After the GUI is closed by the
		user, this method also ensures the model is saved and shutdown. 
		"""
		#Run the main gui loop. This will run until Uniquity shuts down.
		self.app.MainLoop()
		#We are finished, release all model resources
		if self.uniquity:
			self.uniquity.shutdown()
	
	def __addFile(self, filename):
		"""
		Add a single file (or directory) to be scanned by uniquity. Isn't meant to be
		used externally, because it doesn't update the view
		Returns False on success, or the name of the file on failure (file already added)
		
		"""
		if self.uniquity.addFile(filename):
			return False
		return filename
	
	def addFiles(self, files):
		"""
		Add multiple files or directories (in a list of filenames) 
		to be scanned by Uniquity. Updates the view on successful
		or unsuccessful "adds"
		"""
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
		self.dupVC.update(forced=True)
		self.mainView.updateDirView(self.uniquity.getFiles())
		
	
	def removeFiles(self, files):
		"""
		Remove files or directories from the main list of objects
		to scan. Updates the view on success or fail.
		"""
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
		
		self.dupVC.update(forced=True)
		self.mainView.updateDirView(self.uniquity.getFiles())
		
	def updateViewProgress(self):
		"""
		Update the entire view with new model information. Sub-controllers
		may *decide* not to update their view if the model has not changed.
		See each sub-controller's update for more information. 
		"""
		self.mainView.updateUpdatePanel(self.uniquity.getUpdate(fileFormat="basename"))
		self.dupVC.update()
	