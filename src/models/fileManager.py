import threading
import Queue
import os
import logging
import copy

import hashObject
import fileObject
import time
import data.config as config

class FileManager(threading.Thread):
	def __init__(self, fileQueue, hashQueue, fileList, updateCallback):
		threading.Thread.__init__(self)
		self.fileQueue = fileQueue
		self.hashQueue = hashQueue
		self.updateCallback = updateCallback
		self.files = fileList
		
		self.UPDATE_INTERVAL = config.UPDATE_INTERVAL
		self.log = logging.getLogger('.'.join((config.MAIN_LOG_NAME, 'FileManager')))
		
		self.SHUTDOWN_FLAG = False
		self.lastUpdateTime = time.time()

		self.status = "Idle"
		self.scanned = 0
		self.scannedSize = 0
		# #Possible future feature stats!
		# self.possibleDuplicates = 0
		# self.possibleDuplicateSize = 0
		# self.possibleUnique = 0
		# self.possibleUniqueSize = 0
		self.current = None

	def run(self):
		while True:
			
			try:
				
				#grabs host from fileQueue
				nextFileObject = self.fileQueue.get(True, self.UPDATE_INTERVAL)
				self.log.debug("Beginning scan: %s", nextFileObject.getFilename())
				self.__scan(nextFileObject)
				self.fileQueue.task_done()
				self.log.debug("Finished scanning: %s.", nextFileObject.getFilename())
				if self.fileQueue.empty():
					self.status = "Done"
					self.current = None
					self.log.info("Scanner finished current queue")
					self.__update(True)	
				else:
					self.__update()
			except Queue.Empty:
				pass
			except Exception as e:
				self.log.exception(e)
				
			if self.__shouldShutdown():
				self.log.info("Shutting down...")
				break

	#Scan a parent file
	def __scan(self, fileObject):
		self.status = 'running'
		for root, dirs, files in os.walk(fileObject.getFilename()):
			for filename in files:
				try:
					newho = hashObject.HashObject(os.path.join(root,filename))
					if newho.isRegularFile():
						self.__addFile(newho)
					elif os.path.islink(newho.filename):
						self.log.info("Skipping Symbolic Link: %s", newho.filename)
					else:
						self.log.warning("Skipping non-regular File: %s", newho.filename)
				except OSError as ose:
					self.log.warning("File could not be scanned: %s", str(ose))
				except Exception as e:
					self.log.exception(e)
				#check if we should stop what we are doing, otherwise continue
				if self.__shouldShutdown():
					return
				else:
					self.__update()
		self.current = None
		
		
	#Returns true if it should shutdwon		
	def __shouldShutdown(self):
		if self.SHUTDOWN_FLAG:
			return True
		return False
		
	def shutdown(self, boolean_setting=True):
		self.SHUTDOWN_FLAG = boolean_setting
			
	def __update(self, forcedUpdate=False):
		if time.time() - self.lastUpdateTime > self.UPDATE_INTERVAL or forcedUpdate:
			self.lastUpdateTime = time.time()
			self.log.debug("Progress Update!")
			
			self.updateCallback(self.getStats)
	
	def getStats(self, sizeFormat="formatted", fileFormat="fullname"):
		sizeFormatter = fileObject.FileObject.sizeFormats.get(sizeFormat)
		fileFormatter = fileObject.FileObject.fileFormats.get(fileFormat)
		
		cur = ""
		if self.current:
			cur = fileFormatter(self.current)
		return (self.status, cur, unicode(self.scanned), sizeFormatter(self.scannedSize))
			
	def __addFile(self, newho):
		self.current = newho
		fileSize = newho.getSize()
		#Check for 'collisions', files already present because they're the same size we
		#will store all files of the same size in lists called 'records'
		record = self.files.get(fileSize, None)
		#If there's no record, there is no collision
		if record == None:
			self.files[fileSize] = [newho]
		#Add record to the queue to be hashed
		else:
			#Make sure we don't add the record twice. Really this should never happen,
			#because during a scan we should check that we have already scanned these
			#folders. Log an error if it does happen.
			for each in record:
				if each.filename == newho.filename:
					self.log.error("File: '%s' added twice. ", each.filename)
					return
			#Add the record		
			record.append(newho)
			#Verify the file
			self.hashQueue.put(newho)
			#If the size is two, we also need to verify the other file in the record.
			#This is because we don't need to hash files if the record size is less than
			#2. However, we also know that all other records have been scanned if the size
			#is greator than 2, because we will have previously scanned them.
			if len(record) == 2:
				self.hashQueue.put(record[0])

		self.scanned += 1
		self.scannedSize += fileSize
		
