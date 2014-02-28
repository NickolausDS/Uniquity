import threading
import Queue
import os

import scanObject
import scanParent
import time

class FileManager(threading.Thread):
	def __init__(self, queue, out_queue):
		threading.Thread.__init__(self)
		self.SLEEPINTERVAL = 1
		self.queue = queue
		self.out_queue = out_queue
		self.files = {}
		self.SHUTDOWN_FLAG = False

	def run(self):
		while True:
			
			try:
				#grabs host from queue
				nextScanParent = self.queue.get(True, 1)
				self.__scan(nextScanParent)
				#place chunk into out queue
				self.out_queue.put(nextScanParent)
				#signals to queue job is done
				self.queue.task_done()
			except Exception as e:
				if self.__shouldShutdown():
					break
				time.sleep(self.SLEEPINTERVAL)

	#Scan a parent file
	def __scan(self, scanParent):
		for root, dirs, files in os.walk(scanParent.getFilename()):
			# print "root: %s, dirs: %s, files %s\n" % (root, dirs, files)
			for filename in files:
				newso = scanObject.ScanObject(os.path.join(root,filename))
				#Add to the dictionary indexed by size
				self.files[newso.getSize()] = newso
				print filename
		#check if we should stop what we are doing, otherwise continue
		if self.__shouldShutdown():
			return
		
	#Returns true if it should shutdwon		
	def __shouldShutdown(self):
		if self.SHUTDOWN_FLAG:
			return True
		return False
		
	def shutdown(self, boolean_setting=True):
		self.SHUTDOWN_FLAG = boolean_setting
			
	#OLD CODE here for reference		
			
	# #Add files to be hashed. 
	# #Adding directories means adding all the files within it.
	# def addFiles(self, inputFiles, maxDirDepth=0):
	# 	for each in inputFiles:
	# 		if(isfile(each)):
	# 			each = os.path.abspath(each)
	# 			if each not in self.fileListings:
	# 				self.fileListings.append(each)
	# 		elif(isdir(each)):
	# 			self.__addRecursiveDirectories(each, maxDirDepth, 0)
	# 		else:
	# 			self.log.error(each+": No such file or directory")
	# 			continue
	# 
	# 	self.fileListings = [os.path.abspath(f) for f in self.fileListings]
	# 	#self.hashAndStoreFiles(absfiles)
	# 	
	# #Not to be called explicitly by other programs
	# #Adds diretories to the list recursively
	# def __addRecursiveDirectories(self, nextDir, maxlevel, level=0):
	# 	dirs = []
	# 	thems = [os.path.join(nextDir, f) for f in os.listdir(nextDir)]                    
	# 	for each in thems:
	# 		if(isdir(each)):
	# 			if (each not in self.directoryListings):
	# 				dirs.append(each)
	# 				self.log.debug("Adding Directory: " + each)
	# 		if(isfile(each)):
	# 			each = os.path.abspath(each)
	# 			self.fileListings.append(each)
	# 			#self.log.debug("Adding Specific File: " + each)
	# 
	# 	if( dirs and (maxlevel == 0 or level != maxlevel) ):
	# 		self.directoryListings.extend(dirs)
	# 		for each in dirs:
	# 			self.__addRecursiveDirectories(each, maxlevel, level+1)