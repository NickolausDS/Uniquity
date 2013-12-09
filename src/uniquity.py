import hashlib
import zlib
import os
import inspect
from os.path import isfile, isdir

import logging

##TODO: The file listings can get very large, possibly > 500 mb. We might consider storing this in
#A temporary file, or by using mapped memory (which is kinda the same thing)

class Uniquity:
	
	def __init__(self):
		#A list of all of the directories containing files we will hash
		self.directoryListings = []
		#A list of ALL the files we will hash, which can include specific files not in the above
		self.fileListings = []
		self.firstPass = {}
		self.secondPass = {}
		
		self.maxFileSize = 0
		#Files skipped because of errors or large filesize
		self.filesSkipped = []
		
		#Hashing Algorithms
		self.weakHasher = zlib.crc32 #zlib has functions
		self.strongHasher = hashlib.sha512 #hashlib has classes
		
		#Logging
		self.log = logging.getLogger("main")
		self.logHandler = logging.StreamHandler()
		
		self.logHandler.setFormatter(logging.Formatter("%(message)s"))
		self.logHandler.setLevel(logging.DEBUG)
		self.log.addHandler(self.logHandler)
		self.log.setLevel(logging.INFO)
		
	#Add files to be hashed. 
	#Adding directories means adding all the files within it.
	def addFiles(self, inputFiles, maxDirDepth=0):
		for each in inputFiles:
			if(isfile(each)):
				each = os.path.abspath(each)
				if each not in self.fileListings:
					self.fileListings.append(each)
			elif(isdir(each)):
				self.__addRecursiveDirectories(each, maxDirDepth, 0)
			else:
				self.log.error(each+": No such file or directory")
				continue

		self.fileListings = [os.path.abspath(f) for f in self.fileListings]
		#self.hashAndStoreFiles(absfiles)
		
	def setMaxFileSize(self, max):
		self.maxFileSize = max	
		
	def setHashAlgorithm(self, newhasher):
		self.strongHasher = getattr(hashlib, newhasher)
		#reset the 
		self.secondPass = {}
		
	#Not to be called explicitly by other programs
	#Adds diretories to the list recursively
	def __addRecursiveDirectories(self, nextDir, maxlevel, level=0):
		dirs = []
		thems = [os.path.join(nextDir, f) for f in os.listdir(nextDir)]                    
		for each in thems:
			if(isdir(each)):
				if (each not in self.directoryListings):
					dirs.append(each)
					self.log.debug("Adding Directory: " + each)
			if(isfile(each)):
				each = os.path.abspath(each)
				self.fileListings.append(each)
				#self.log.debug("Adding Specific File: " + each)
												
		if( dirs and (maxlevel == 0 or level != maxlevel) ):
			self.directoryListings.extend(dirs)
			for each in dirs:
				self.__addRecursiveDirectories(each, maxlevel, level+1)

	def start(self):
		self.log.debug("Scanning all files given...")
		self.hashFiles(self.fileListings, self.firstPass, self.__weakHash)
		dups = []
		for each in self.firstPass.values():
			if (len(each) > 1):
				dups.extend(each)
		self.log.debug("Verifying duplicates...")
		self.hashFiles(dups, self.secondPass, self.__strongHash)

	#Weak checksum to narrow down the mass of files chosen
	def hashFiles(self, fileList, outputDict, hashFunct):
		for idx, fname in enumerate(fileList):
				
			#Skip large files
			if(self.maxFileSize != 0):
				#Remove large files
				filesize = os.stat(fname).st_size / 2**20
				if (filesize > self.maxFileSize):
					self.filesSkipped.append(fname)
					self.log.warning("Skipped "+fname+" because it was too large (" + str(filesize) + "MB).")
					continue
			
			#Hash File
			try:
				fileHash = hashFunct(fname)
			except IOError:
				self.log.error("Error: Could not open '" + fname + "'.")
				self.filesSkipped.append(fname)
				continue
				
			#Add it to the list
			if (fileHash in outputDict ):
				if( fname not in outputDict[fileHash] ):
					outputDict[fileHash].append(fname)
				else:
					self.log.debug("WARNING: " + fname + " Already hashed!")
			else:
				outputDict[fileHash] = [fname]
			
			#Compute percent completed
			percent = float(idx) / float(len(self.fileListings) ) * 100
			self.log.info("(%.1f%%) %s" %(percent, os.path.basename(fname) )) 

	
	# #Strong hash, so we know for sure if it was a duplicate			
	# def doSecondPass(self):
	# 	self.log.debug("Verifying duplicates are exact...")
	# 	#print "\n\nSECOND PASS Verifying..."
	# 	foo = []
	# 	for vals in self.firstPass.values():
	# 		if len(vals) > 1:
	# 			for each in vals:
	# 				foo.extend([ (self.__strongHash(each, hashlib.sha512() ), [each]) ])
	# 				
	# 	for each in foo:
	# 		if (each[0] in self.secondPass ):
	# 			if( each[1][0] not in self.secondPass[each[0]] ):
	# 				self.secondPass[each[0]].append(each[1][0])
	# 			else:
	# 				self.log.debug("WARNING: " + each[1][0] + " Already hashed!")
	# 		else:
	# 			self.secondPass[each[0]] = each[1]
		
	
	def __weakHash(self, fileName, blocksize=65536):
		theFile = open(fileName, 'rb')
		buf = theFile.read(blocksize)
		prev = 0
		while len(buf) > 0:
			prev = zlib.crc32(buf, prev)
			buf = theFile.read(blocksize)
		theFile.close()
		return "%X"%(prev & 0xFFFFFFFF)
		
	def __strongHash(self, fileName, blocksize=65536):
		hasher = self.strongHasher()
		try:
			theFile = open(fileName, 'rb')
		except IOError:
			self.log.error("Could not open: '" + fileName + "'.")
			return None
		
		buf = theFile.read(blocksize)
		while len(buf) > 0:
			hasher.update(buf)
			buf = theFile.read(blocksize)
		theFile.close()
		return hasher.hexdigest()
	
	
	def printList(self):
		for keys, vals in self.secondPass.items():
			s = ""
			if len(vals) > 1:
				print " ".join(vals)

	

	def printPretty(self):
		print getPrettyOutput
					
	def getPrettyOutput(self):
		retVal = ""
		for keys, vals in self.secondPass.items():
			if len(vals) > 1:
				retVal += "\nDuplicates ("+self.strongHasher().name+"): " + keys + "\n"
				for each in vals:
					retVal += each + "\n"
		return retVal
