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

class Uniquity:
	
	def __init__(self):
		self.log = logging.getLogger('.'.join((config.MAIN_LOG_NAME, 'Main')))
		#All files will be stored here as hashObjects, indexed by their filesize. The format follows:
		# {10000: [so1, so2], 1234: [so3], 4567:[so4, so5, so6]}
		self.scannedFiles = {}
		self.hashedFiles = {}	
		
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
		self.hasher = hasher.Hasher(self.hashQueue, self.hashedFiles, self.updateProgress)
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
	
		
	def addFiles(self, inputFiles, block=False):
		for each in inputFiles:
			newjob = fileObject.FileObject(each)
			self.fileQueue.put(newjob)
			self.log.debug("Adding new file(s): " + str(inputFiles))
		
		if block == True:
			while not fileQueue.empty() and not hashQueue.empty():
				time.sleep(config.UPDATE_INTERVAL)
			self.log.info("Uniquity finished all jobs.")

	#Returns all duplicate files, as a giant list of smaller duplicate file lists.
	#ex. [[dupfilename1, dupfilename1copy], [dupfilename2, dupfilename2copy, dupfilename2anothercopy]]
	def getDuplicateFiles(self):
		return [dup for dup in self.hashedFiles.values() if len(dup) > 1]

	def isIdle(self):
		if self.fileQueue.empty() and self.hashQueue.empty():
			return True
		return False
		
	def getUpdate(self):
		self.stats.update(self.fileManager.stats)
		self.stats.update(self.hasher.stats)
		return self.stats
		
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
		
