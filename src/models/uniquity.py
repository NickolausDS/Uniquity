import hashlib
import zlib
import os
import inspect
from os.path import isfile, isdir
import Queue

import logging

import fileManager
import hasher
import scanObject
import scanParent

##TODO: The file listings can get very large, possibly > 500 mb. We might consider storing this in
#A temporary file, or by using mapped memory (which is kinda the same thing)

class Uniquity:
	
	def __init__(self):
		#A list of all of the directories containing files we will hash
		# self.directoryListings = []
		#A list of ALL the files we will hash, which can include specific files not in the above
		# self.fileListings = []
		# self.firstPass = {}
		# self.secondPass = {}
		
		#All files will be stored here as scanObjects, indexed by their filesize. The format follows:
		# {10000: [so1, so2], 1234: [so3], 4567:[so4, so5, so6]}
		self.allFiles = {}
		
		self.hashedFiles = {}
		self.secondPass = self.hashedFiles
		
		# self.maxFileSize = 0
		#Files skipped because of errors or large filesize
		# self.filesSkipped = []
		
		#Hashing Algorithms
		# self.weakHasher = zlib.crc32 #zlib has functions
		# self.strongHasher = hashlib.sha512 #hashlib has classes
		
		#Logging
		self.log = logging.getLogger("main")
		self.logHandler = logging.StreamHandler()
		
		self.logHandler.setFormatter(logging.Formatter("%(message)s"))
		self.logHandler.setLevel(logging.DEBUG)
		self.log.addHandler(self.logHandler)
		self.log.setLevel(logging.INFO)
		
		
		self.progress = {}
		self.progressPercentComplete = 0.0
		self.progressFileComplete = None
		self.updateCallbackFunction = None
		
		
		self.fileQueue = Queue.Queue()
		self.hashQueue = Queue.Queue()
		
		self.fileManager = fileManager.FileManager(self.fileQueue, self.hashQueue, self.allFiles, self.updateProgress)
		self.fileManager.setDaemon(True)
		self.fileManager.start()
				
		#Put stuff on the queue
		
		self.hasher = hasher.Hasher(self.hashQueue, self.hashedFiles, self.updateProgress)
		self.hasher.setDaemon(True)
		self.hasher.start()


	def shutdown(self):
		#wait on the queue until everything has been processed
		self.fileManager.shutdown()
		self.hasher.shutdown()
		self.log.Debug("Waiting for services to shutdown.")
		self.fileQueue.join()
		# self.hashQueue.join()
	
		
	def addFiles(self, inputFiles):
		for each in inputFiles:
			newjob = scanParent.ScanParent(each)
			self.fileQueue.put(newjob)
			self.log.debug("Adding new file(s): " + str(inputFiles))
			
		
	# def setMaxFileSize(self, max):
	# 	self.maxFileSize = max	
	# 	
	# def setHashAlgorithm(self, newhasher):
	# 	self.strongHasher = getattr(hashlib, newhasher)
	# 	#reset the 
	# 	self.secondPass = {}

	def start(self):
		pass

	# def start(self):
	# 	self.log.debug("Scanning all files given...")
	# 	self.hashFiles(self.fileListings, self.firstPass, self.__weakHash)
	# 	dups = []
	# 	for each in self.firstPass.values():
	# 		if (len(each) > 1):
	# 			dups.extend(each)
	# 	self.log.debug("Verifying duplicates...")
	# 	self.hashFiles(dups, self.secondPass, self.__strongHash)
	# 	self.updateProgress(100.0)

	#Update our current progress completing the scan
	def updateProgress(self, newProgress):
		# for key, val in newProgress.items():
		# 	self.progress[key] = val
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
		
	# def getProgressPercent(self):
	# 	return self.progressPercentComplete
	# 	
	# def getProgressFile(self):
	# 	if self.progressFileComplete:
	# 		return self.progressFileComplete
	# 	else:
	# 		return "None."

	# #Weak checksum to narrow down the mass of files chosen
	# def hashFiles(self, fileList, outputDict, hashFunct):
	# 	for idx, fname in enumerate(fileList):
	# 			
	# 		#Compute percent completed
	# 		percent = float(idx) / float(len(self.fileListings) ) * 100.0
	# 		#I'll say it now, this is a hack. It should be taken care of in the refactor
	# 		#next week, but I'm really sorry if it didn't.
	# 		#
	# 		#Manually check if this is the second pass by checking if it has any files.
	# 		if len(self.secondPass) == 0:
	# 			self.updateProgress(percent/2.0, fname)
	# 		else:
	# 			self.updateProgress(percent/2.0+50.0, fname)
	# 		# self.log.info("(%.1f%%) %s" %(percent, os.path.basename(fname) ))	
	# 			
	# 		#Skip large files
	# 		if(self.maxFileSize != 0):
	# 			#Remove large files
	# 			filesize = os.stat(fname).st_size / 2**20
	# 			if (filesize > self.maxFileSize):
	# 				self.filesSkipped.append(fname)
	# 				self.log.warning("Skipped "+fname+" because it was too large (" + str(filesize) + "MB).")
	# 				continue
	# 		
	# 		#Hash File
	# 		try:
	# 			fileHash = hashFunct(fname)
	# 		except IOError:
	# 			self.log.error("Error: Could not open '" + fname + "'.")
	# 			self.filesSkipped.append(fname)
	# 			continue
	# 			
	# 		#Add it to the list
	# 		if (fileHash in outputDict ):
	# 			if( fname not in outputDict[fileHash] ):
	# 				outputDict[fileHash].append(fname)
	# 			else:
	# 				self.log.debug("WARNING: " + fname + " Already hashed!")
	# 		else:
	# 			outputDict[fileHash] = [fname]
	# 
	# def __weakHash(self, fileName, blocksize=65536):
	# 	theFile = open(fileName, 'rb')
	# 	buf = theFile.read(blocksize)
	# 	prev = 0
	# 	while len(buf) > 0:
	# 		prev = zlib.crc32(buf, prev)
	# 		buf = theFile.read(blocksize)
	# 	theFile.close()
	# 	return "%X"%(prev & 0xFFFFFFFF)
	# 	
	# def __strongHash(self, fileName, blocksize=65536):
	# 	hasher = self.strongHasher()
	# 	try:
	# 		theFile = open(fileName, 'rb')
	# 	except IOError:
	# 		self.log.error("Could not open: '" + fileName + "'.")
	# 		return None
	# 	
	# 	buf = theFile.read(blocksize)
	# 	while len(buf) > 0:
	# 		hasher.update(buf)
	# 		buf = theFile.read(blocksize)
	# 	theFile.close()
	# 	return hasher.hexdigest()
	# 
	# 
	# def printList(self):
	# 	for keys, vals in self.secondPass.items():
	# 		s = ""
	# 		if len(vals) > 1:
	# 			print " ".join(vals)
	# 
	# 
	# 
	# def printPretty(self):
	# 	print getPrettyOutput
	# 				
	# def getPrettyOutput(self):
	# 	retVal = ""
	# 	for keys, vals in self.secondPass.items():
	# 		if len(vals) > 1:
	# 			retVal += "\nDuplicates ("+self.strongHasher().name+"): " + keys + "\n"
	# 			for each in vals:
	# 				retVal += each + "\n"
	# 	return retVal
