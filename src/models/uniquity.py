import hashlib
import zlib
import os
import inspect
from os.path import isfile, isdir
import Queue

import logging
import logger

import fileManager
import hasher
import fileObject
import data.config as config
import cursor

import time
import operator


class Uniquity:
	
	
	def __init__(self):
		self.log = logging.getLogger('.'.join((config.MAIN_LOG_NAME, 'Main')))
		#A list of all the directories (and files) scanned by uniquity. 
		self.rootFileObjects = []
		#All files will be stored here as hashObjects, indexed by their filesize. The format follows:
		# {10000: [so1, so2], 1234: [so3], 4567:[so4, so5, so6]}
		self.scannedFiles = {}
		self.hashedFiles = {}
		#Basically the same as hashedFiles, but we only add duplicate enteries.
		self.duplicateFilesIndex = {}
		
		
		#cleanup old tables.
		try:
			if config.DB_NAME != ":memory:" and os.path.exists(config.DB_NAME):
				os.remove(config.DB_NAME)
		except Exception:
			pass
			
		#Setup the db.	
		self.cursor = cursor.Cursor()
		self.cursor.setupTables()
		
		#A simple time check for when we last committed to the database
		#Useful for determining if a caller *really* wants the same data
		#in some methods
		self.lastDBFetch = 0
		
		self.UPDATE_INTERVAL = config.UPDATE_INTERVAL
		self.updateCallbackFunction = None
		
		#Both these queues handle jobs. The file Queue is for the file manager, meant for scanning
		#files. The file manager then hands off more work to the hash queue, if it needs to.
		self.fileQueue = Queue.Queue()
		self.hashQueue = Queue.Queue()
		
		#Setup the file manager
		self.fileManager = fileManager.FileManager(self.fileQueue, self.hashQueue, self.scannedFiles, self.updateProgress)
		self.fileManager.setDaemon(True)
		self.fileManager.start()
			
		#Setup the hasher			
		self.hasher = hasher.Hasher(self.hashQueue, self.hashedFiles, self.duplicateFilesIndex, self.updateProgress)
		self.hasher.setDaemon(True)
		self.hasher.start()
		
		#Where we store update information and such about the hasher and fileManager
		self.stats = {}
		

	#try for graceful shutdown. Returns true if successful, false if it quit with jobs running.
	def shutdown(self):
		exitStatus = True
		#shutdown file manager 
		if self.fileManager.isAlive():
			self.fileManager.shutdown()
			self.fileManager.join(config.SHUTDOWN_MAX_WAIT)
			if self.fileManager.isAlive():
				self.log.critical("File manager failed to shutdown!")
				exitStatus = False			
		else:
			self.log.warning("Called for fileManager shutdown but fileManager is not running!")
			exitStatus = False
		
		#shutdown hasher
		if self.hasher.isAlive():
			self.hasher.shutdown()
			self.hasher.join(config.SHUTDOWN_MAX_WAIT)
			if self.hasher.isAlive():
				self.log.critical("Hasher failed to shutdown!")
				exitStatus = False
		else:
			self.log.warning("Called for hasher to shutdown, but hasher is not running!")
			exitStatus = False		
								
		return exitStatus
	
	def addFile(self, theFile, block=False):
		"""Add a single file (string), and return a boolean for success
		Keyword arguments:
		block -- don't return until scanning and verification has finished (default False)
		"""
		newjob = fileObject.FileObject(theFile)
		if newjob not in self.rootFileObjects:
			self.fileQueue.put(newjob)
			self.rootFileObjects.append(newjob)
			self.log.debug("Adding new file: " + str(theFile))
			if block:
				self.__waitUntilFinished()
			return True
		else:
			return False
		
	def addFiles(self, inputFiles, block=False):
		"""Add a list of files, and return a list of booleans for success
		Keyword arguments:
		block -- don't return until scanning and verification has finished (default False)
		"""
		retval = []
		for each in inputFiles:
			retval.append(self.addFile(each, block))
		return retval
			
	def removeFile(self, thefile):	
		fo = fileObject.FileObject(thefile)
		if fo in self.rootFileObjects:
			self.rootFileObjects.remove(fo)
			self.log.critical("File '%s' not actually removed from model," + 
			" functionality not implemented yet!")
			return True
		return False
		
			
			
	def removeFiles(self, files):
		retval = []
		for each in files:
			retval.append(self.removeFile(each))
		return retval
		
			
	#Get the files previously added files (in filename format)
	def getFiles(self):
		"""Return a list of the root file objects previously added to Uniquity"""
		return [each.filename for each in self.rootFileObjects]
			
	def __waitUntilFinished(self):
		time.sleep(self.UPDATE_INTERVAL)
		while self.fileManager.isRunning() or self.hasher.isRunning():
			time.sleep(self.UPDATE_INTERVAL)
		self.log.info("Uniquity finished all jobs.")

	#Returns all duplicate files, as a giant list of smaller duplicate file lists.
	#ex. [[dupfilename1, dupfilename1copy], [dupfilename2, dupfilename2copy, dupfilename2anothercopy]]
	def getDuplicateFiles(self, onlyReturnNewData=False):
		if onlyReturnNewData and self.lastDBFetch > cursor.Cursor.lastCommit:
			return None
		self.lastDBFetch = time.time()
		return self.cursor.getDupData()

	def isIdle(self):
		if self.fileQueue.empty() and self.hashQueue.empty():
			return True
		return False
		
	def getFileFormats(self):
		return self.fileObject.FileObject.fileFormats.keys()
		
	def getSizeFormats(self):
		return self.fileObject.FileObject.sizeFormats.keys()	
		
	def getUpdate(self, sizeFormat="formatted", fileFormat="fullname"):
		"""
		(
			(uniquity status)
			(fileManager status, current file, files scanned, total scan size)
			(	hasher status, current file, 
				files hashed, total hashed size,
				number of duplicates, duplicates size,
				number of uniques,	unique size
			)
		)
		
		"""
		if not self.isIdle():
			status = "running"
		else:
			status = "idle"
		uniquityStats = (status,)
		fms = self.fileManager.getStats(sizeFormat, fileFormat)
		has = self.hasher.getStats(sizeFormat, fileFormat)
		return (uniquityStats, fms, has)
		
	#Update our current progress completing the scan
	#Docs regarding the contense of newProgress need to be added
	def updateProgress(self, newProgress):
		if self.updateCallbackFunction:
			try:
				self.updateCallbackFunction(newProgress)
			except Exception as e:
				self.log.critical("Uniquity: Failed to call updateProgress() callback function: " + str(e))
		
	#If you want uniquity to update you on its progress after each scanned file, you can
	#give it a function to call each time
	#
	#I understand this is a simple, butured version of the observer Dpattern. But as of now,
	#I don't feel the need for it support more than one callback. You could refactor it into
	#the more regular design pattern in the future, if you would like.	
	def setUpdateCallback(self, funct):
		self.updateCallbackFunction = funct
		
		
