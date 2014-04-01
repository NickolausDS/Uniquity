import threading
import Queue
import os
import logging

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

		#STATS
		self.stats = {}
		self.stats['files'] = self.files
		self.stats['filesScanned'] = 0
		self.stats['sizeScanned'] = 0
		self.stats['currentScanFile'] = None
		self.stats['scannerStatus'] = "idle"
		self.stats['possibleDuplicates'] = 0

	def run(self):
		while True:
			
			try:
				
				#grabs host from fileQueue
				nextFileObject = self.fileQueue.get(True, self.UPDATE_INTERVAL)
				self.log.debug("Beginning scan: %s", nextFileObject.getFilename())
				self.__scan(nextFileObject)
				self.fileQueue.task_done()
				self.__update(True)
				self.log.debug("Finished scanning: %s.", nextFileObject.getFilename())
			except Queue.Empty:
				self.stats['scannerStatus'] = "idle"
			except Exception as e:
				self.log.exception(e)
				
			if self.__shouldShutdown():
				self.log.info("Shutting down...")
				break

	#Scan a parent file
	def __scan(self, fileObject):
		self.stats['scannerStatus'] = 'running'
		for root, dirs, files in os.walk(fileObject.getFilename()):
			for filename in files:
				try:
					newho = hashObject.HashObject(os.path.join(root,filename))
					self.stats['currentScanFile'] = newho.getBasename()
					#Add to the dictionary indexed by size
					self.__addFile(newho)
				except OSError as ose:
					self.log.warning("File disappeared before we could scan it: %s", newho)
				except Exception as e:
					self.log.exception(e)
				#check if we should stop what we are doing, otherwise continue
				if self.__shouldShutdown():
					return
				else:
					self.__update()
		self.stats['currentScanFile'] = None
		
		
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
			self.updateCallback(self.stats)
			
	def __addFile(self, newho):
		fileSize = newho.getSize()
		#Check for 'collisions', files already present because they're the same size we
		#will store all files of the same size in lists called 'records'
		record = self.files.get(fileSize, None)
		#If there's no record, there is no collision
		if not record:
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
				
		self.stats['sizeScanned'] += fileSize
		self.stats['filesScanned'] += 1
		
