import threading
import Queue
import logging
import time
import zlib
import hashlib

import data.config as config


class Hasher(threading.Thread):
	def __init__(self, hashQueue, verifiedFiles, updateCallback):
		threading.Thread.__init__(self)
		self.hashQueue = hashQueue
		self.updateCallback = updateCallback
		self.verifiedFiles = verifiedFiles
		
		self.UPDATE_INTERVAL = config.UPDATE_INTERVAL
		self.log = logging.getLogger('.'.join((config.MAIN_LOG_NAME, 'Hasher')))
		
		self.SHUTDOWN_FLAG = False
		self.lastUpdateTime = time.time()
		
		self.weakHashAlgorithm = config.WEAK_HASH
		self.strongHashAlgorithm = config.STRONG_HASH
		self.blockSize = config.BLOCK_SIZE
		
		#Used for counting stats
		self.stats = {}
		self.totalSize = 0
		self.totalVerifiedFiles = 0
		self.currentFile = ""
		self.currentSizeHashed = 0
		self.stats['filesHashed'] = 0
		self.stats['totalHashSize'] = 0
		
	
	@property
	def weakHashAlgorithm(self):
		return self._weakHashAlgorithm

	@weakHashAlgorithm.setter
	def weakHashAlgorithm(self, newalg):
		try:
			setattr(self, "_weakHashAlgorithm", getattr(zlib, newalg))
		except AttributeError:
			raise ValueError("Could not load hash algorithm '%s' from zlib library." % newalg)	
		
		
	@property
	def strongHashAlgorithm(self):
		return self._strongHashAlgorithm
		
	@strongHashAlgorithm.setter
	def strongHashAlgorithm(self, newalg):
		try:
			setattr(self, "_strongHashAlgorithm", getattr(hashlib, newalg))
		except AttributeError:
			raise ValueError("Could not load hash algorithm '%s' from hashlib library." % newalg)

	def run(self):
		while True:
			
			try:
				#grabs host from fileQueue
				nextSO = self.hashQueue.get(True, self.UPDATE_INTERVAL)
				self.log.info("Verifying File: %s", nextSO.getFilename())
				self.hash(nextSO)
				self.hashQueue.task_done()
				self.__update(True)
			except Queue.Empty:
				pass
			except Exception as e:
				self.log.exception(e)
				
			if self.__shouldShutdown():
				self.log.debug("Shutting down...")
				break


	def hash(self, so):
		self.currentSizeHashed = 0
		self.currentFile = so.filename
		
		#Note: the weak hasher is a function, the strong hasher is an object
		#For more info, see zlib and hashlib for weak and strong hashes respectfully
		weakHasher = self.weakHashAlgorithm
		strongHasher = self.strongHashAlgorithm()
		#Weak hash needs to start at 0, so zlib can add to it
		weakHash = 0
		strongHash = ""
		try:
			theFile = open(so.getFilename(), 'rb')
			buf = theFile.read(self.blockSize)
			while len(buf) > 0:
				#Do some hashing
				weakHash = weakHasher(buf, weakHash)
				strongHasher.update(buf)
				#Tell the world what we're up to
				self.currentSizeHashed += len(buf)
				self.__update()
				if self.__shouldShutdown():
					return
				#Get more junk to hash
				buf = theFile.read(self.blockSize)
			theFile.close()
			#set the weak hash
			so.setWeakHash("%X"%(weakHash & 0xFFFFFFFF), self.weakHashAlgorithm )
			so.setStrongHash(strongHasher.hexdigest(), self.strongHashAlgorithm )
			self.__addFile(so)
		except IOError as ioe:
			self.log.error(ioe)
		except Exception as e:
			self.log.exception(e)
			
		# self.__update(True)
		
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
			# self.totalSize = 0
			# self.totalVerifiedFiles = 0
			# self.currentFile = ""
			# self.currentSizeHashed = 0
			# progress = {
			# 			'verifiedFiles' : self.verifiedFiles,
			# 			'totalHashSize' : self.totalSize,
			# 			'totalHashedFiles': self.totalVerifiedFiles,
			# 			'currentHashFile' : self.currentFile,
			# 			'currentHashSize': self.currentSizeHashed,
			# 			}
			# progress.update(self.stats)
			self.stats['dupDict'] = self.verifiedFiles
			self.updateCallback(self.stats)	
	
	
	def __addFile(self, newso):
		#Check for 'collisions', files already present because they're the same size
		record = self.verifiedFiles.get(newso.hashes, None)
		# self.log.debug("RECORDS: %s" % str(self.verifiedFiles))
		#If there's no record, there is no collision
		if not record:
			self.verifiedFiles[newso.hashes] = [newso]
		#Add record to the queue to be hashed
		else:
			#Make sure we don't add the record twice
			for eachso in record:
				if eachso.filename == newso.filename:
					self.log.debug("Skipping file '%s', already added.", newso.filename)
					return
				else:
					continue
			#Add the record		
			record.append(newso)
			self.log.info("Duplicate file found: %s.", newso.filename)
		self.stats['filesHashed'] += 1
		self.stats['totalHashSize'] += newso.getSize()
		
	# def __addFile(self, newso):
	# 	#Add it to the list
	# 	if (fileHash in outputDict ):
	# 		if( fname not in outputDict[fileHash] ):
	# 			outputDict[fileHash].append(fname)
	# 		else:
	# 			self.log.debug("WARNING: " + fname + " Already hashed!")
	# 	else:
	# 		outputDict[fileHash] = [fname]

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