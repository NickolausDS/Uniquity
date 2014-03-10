import threading
import Queue
import os
import logging

import scanObject
import scanParent
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
		self.totalSize = 0
		self.filesScanned = 0

	def run(self):
		while True:
			
			try:
				#grabs host from fileQueue
				nextScanParent = self.fileQueue.get(True, self.UPDATE_INTERVAL)
				self.log.debug("Beginning scan: %s", nextScanParent.getFilename())
				self.__scan(nextScanParent)
				self.fileQueue.task_done()
				self.__update(True)
				self.log.debug("Finished scanning: %s.", nextScanParent.getFilename())
			except Queue.Empty:
				pass
			except Exception as e:
				self.log.exception(e)
				
			if self.__shouldShutdown():
				self.log.info("Shutting down...")
				break

	#Scan a parent file
	def __scan(self, scanParent):
		for root, dirs, files in os.walk(scanParent.getFilename()):
			for filename in files:
				try:
					newso = scanObject.ScanObject(os.path.join(root,filename))
					#Add to the dictionary indexed by size
					self.__addFile(newso)
				except OSError as ose:
					self.log.warning("File disappeared before we could scan it: %s", newso)
				except Exception as e:
					self.log.exception(e)
				#check if we should stop what we are doing, otherwise continue
				if self.__shouldShutdown():
					return
				else:
					self.__update()
				# self.log.debug(self.files)
		
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
			progress = {'file': "Total files: %s, Total Size %d" % (self.filesScanned, self.totalSize)}
			self.updateCallback(progress)
			
	def __addFile(self, newso):
		fileSize = newso.getSize()
		#Check for 'collisions', files already present because they're the same size
		record = self.files.get(fileSize, None)
		#If there's no record, there is no collision
		if not record:
			self.files[fileSize] = [newso]
		#Add record to the queue to be hashed
		else:
			#Make sure we don't add the record twice
			for each in record:
				if each.equals(newso):
					return
				else:
					continue
			#Add the record		
			record.append(newso)
			# self.hashQueue.put(newso)
			for each in record:
				self.hashQueue.put(each)
		self.totalSize += fileSize
		self.filesScanned += 1
		
