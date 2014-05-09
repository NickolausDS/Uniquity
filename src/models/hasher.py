import threading
import Queue
import logging
import time
import zlib
import hashlib
import copy

import data.config as config

import fileObject

class Hasher(threading.Thread):
	def __init__(self, hashQueue, verifiedFiles, duplicateFiles, updateCallback):
		threading.Thread.__init__(self)
		self.hashQueue = hashQueue
		self.updateCallback = updateCallback
		self.verifiedFiles = verifiedFiles
		self.duplicateFiles = duplicateFiles
		
		#Indexes used for efficiency
		self.duplicateFilesSortedIndex = []
		self.duplicateFilesNewItems = []
		
		self.UPDATE_INTERVAL = config.UPDATE_INTERVAL
		self.log = logging.getLogger('.'.join((config.MAIN_LOG_NAME, 'Hasher')))
		
		self.SHUTDOWN_FLAG = False
		self.lastUpdateTime = time.time()
		
		self.weakHashAlgorithm = config.WEAK_HASH
		self.strongHashAlgorithm = config.STRONG_HASH
		self.blockSize = config.BLOCK_SIZE

		#Stats
		self.status = "Idle"
		self.hashed = 0
		self.hashedSize = 0
		self.duplicates = 0
		self.duplicateSize = 0
		self.unique = 0
		self.uniqueSize = 0
		self.current = None
	
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
				self.current = self.hashQueue.get(True, self.UPDATE_INTERVAL)
				self.status = 'running'
				self.__hash(self.current)
				self.hashQueue.task_done()
				if self.hashQueue.empty():
					self.status = "Done"
					self.current = None
					self.log.info("Hasher finished current queue.")
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


	def __hash(self, ho):		
		#Note: the weak hasher is a function, the strong hasher is an object
		#For more info, see zlib and hashlib for weak and strong hashes respectfully
		weakHasher = self.weakHashAlgorithm
		strongHasher = self.strongHashAlgorithm()
		#Weak hash needs to start at 0, so zlib can add to it
		weakHash = 0
		strongHash = ""
		#Do the open() in a separate try block, so if it fails further down the line, we
		#don't forget to close it.
		try:
			theFile = open(ho.filename, 'rb')
			try:
				buf = theFile.read(self.blockSize)
				while len(buf) > 0:
					#Do some hashing
					weakHash = weakHasher(buf, weakHash)
					strongHasher.update(buf)
					#Tell the world what we're up to
					self.hashedSize += len(buf)
					self.__update()
					if self.__shouldShutdown():
						return
					#Get more junk to hash
					buf = theFile.read(self.blockSize)
				theFile.close()
				#set the weak hash
				ho.setWeakHash("%X"%(weakHash & 0xFFFFFFFF), self.weakHashAlgorithm )
				ho.setStrongHash(strongHasher.hexdigest(), self.strongHashAlgorithm )
				self.__addFile(ho)
			except IOError as ioe:
				#We will consider these as predictable failures, and so log them as errors
				#instead of exceptions, because we don't need 
				self.log.error(ioe)
			except Exception as e:
				self.log.exception(e)
			finally:
				theFile.close()
		except IOError as ioe:
				self.log.error("Failed to open %s: %s", ho.filename, str(ioe))
		except Exception as e:
				self.log.exception(e)
					
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
			
			# del self.stats['hashedFiles']
			# statsCopy = copy.deepcopy(self.stats)
			# statsCopy['hashedFiles'] = self.verifiedFiles
			# self.stats['hashedFiles'] = self.verifiedFiles
			
			#Consider moving this work onto a different thread. It doesn't really
			#make sense for the hasher to do this work, and it's CPU intensive.
			self.duplicateFilesSortedIndex.extend(self.duplicateFilesNewItems)
			self.duplicateFilesSortedIndex.sort(reverse=True)
			self.duplicateFilesNewItems = []
			
			# self.updateCallback(statsCopy)
			
	def getStats(self, sizeFormat="formatted", fileFormat="fullname"):
		sizeFormatter = fileObject.FileObject.sizeFormats.get(sizeFormat)
		fileFormatter = fileObject.FileObject.fileFormats.get(fileFormat)
		
		cur = ""
		if self.current:
			cur = fileFormatter(self.current)

		return (	self.status, cur, 
					unicode(self.hashed), sizeFormatter(self.hashedSize),
					unicode(self.duplicates), sizeFormatter(self.duplicateSize),
					unicode(self.unique), sizeFormatter(self.uniqueSize)
					)	
	
	#Note: This method hasn't been tested, or the speed increase of the above in the _update 
	#method. Date: 04/07/2014
	def getDuplicateFilesSortedBySize(self, nItems=0):
		return [self.duplicateFiles[item] for item in self.duplicateFilesStortedIndex[0:nItems]]
		
	def __addFile(self, newho):
		#Check if a record already exists
		record = self.verifiedFiles.get(newho.hashes, None)
		#If there's no record, this file is unique
		if record == None:
			self.verifiedFiles[newho.hashes] = [newho]
			self.unique += 1
			self.uniqueSize += newho.size
		#Add record to the queue to be hashed
		else:
			#Make sure we don't add the record twice
			for eachho in record:
				if eachho.filename == newho.filename:
					self.log.error("Skipping file '%s', already added.", newho.filename)
					return
			#Add the record		
			record.append(newho)
			self.log.info("Duplicate file found: %s.", newho.filename)
			self.duplicates += 1
			self.duplicateSize += newho.size
			if len(record) == 2:
				self.duplicateFiles[record[0].hashes] = record
				self.duplicateFilesNewItems.append(record[0].size)
				self.unique -= 1
				self.uniqueSize -= newho.size
		self.hashed += 1
		self.current = newho
				
		