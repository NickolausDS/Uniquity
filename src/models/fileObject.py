import os
import stat
import math


class FileObject(object):
	
	def __init__(self, filename):
		self._filename = unicode(filename)
		self._stat = None
		
	@property
	def filename(self):
		return self._filename
		
	#Since getting file statistics is a system call, we won't stat a file
	#unless we *Must* do so. System calls are expensive in large quantities. 
	@property
	def stat(self):
		if self._stat == None:
			self._stat = os.stat(self.filename)
		return self._stat
		
	@property
	def size(self):
		return self.stat.st_size	
		
	def __str__(self):
		return str(self._filename)
		
	def __unicode__(self):
		return unicode(self._filename)
		
	def __eq__(self, other):
		if self._filename == other.filename:
			return True
		return False
		
	def isRegularFile(self):
		return stat.S_ISREG(self.stat.st_mode)	
		
	def getFilename(self):
		return os.path.abspath(self._filename)
		
	def getBasename(self):
		return os.path.basename(self._filename)
		
	def getSize(self):
		return self.stat.st_size
		
	def isInDir(self, directory):
		
		#Make sure it is a directory
		assert(os.path.isdir(directory))
		
		if self._filename in directory:
			return True
		else:
			return False			
		
	@staticmethod
	def getNiceSizeInBytes(size, desc=False):
		mag = int(math.floor(math.log(size, 1000)))
		retVal = unicode(round(size / (1000.0 ** mag), 2))
		namesByMag = {
			0:("Bytes", "(tiny)"),
			1:("KB", "(tiny)"), 
			2:("MB", "(small)"), 
			3:("GB", "(large)"),
			4:("TB", "(HUGE)"),
			5:("PB", "(MASSIVE)"),
			6:("EB", "(SO MUCH DATA!!!)"),
			7:("ZB", "(AHHHH!!!)"),
			}
		if desc:
			retVal += " ".join(namesByMag[mag])
		else:
			retVal += namesByMag[mag][0]
		return retVal
		