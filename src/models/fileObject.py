import os
import stat
import math


class FileObject(object):
	
	fileFormats = {
				"basename":lambda fo: fo.basename,
				"shortname":lambda fo: fo.basename,
				"fullname":lambda fo: fo.filename
				}
	sizeFormats = {
				"raw":lambda x: x,
				"formatted":lambda x: FileObject.getNiceSizeInBytes(x, desc=False),
				"formatteddesc":lambda x: FileObject.getNiceSizeInBytes(x, desc=True)
	}
	
	def __init__(self, filename, scanParent=None):
		self._filename = unicode(filename)
		self._stat = None
		if scanParent:
			self._scanParent = scanParent.filename
		else:
			self._scanParent = ""
		
	@property
	def filename(self):
		return self._filename
		
	@property
	def basename(self):
		return os.path.basename(self.filename)
		
	@property
	def shortname(self):
		return self.filename.replace(os.path.abspath(os.path.join(self._scanParent, os.path.pardir)) + os.path.sep, "")
		
	@property
	def scanParent(self):
		return self._scanParent
		
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
		
	@property
	def data(self):
		return (self.filename, self.size)
		
	@property
	def niceSize(self):
		return self.getNiceSizeInBytes(self.size, False)
		
	@property
	def niceSizeAndDesc(self):
		return self.getNiceSizeInBytes(self.size, True)	
		
	def __unicode__(self):
		return unicode(self._filename)
		
	def __eq__(self, other):
		"""returns true only if filenames match"""
		if self._filename == other.filename:
			return True
		return False
		
	def __repr__(self):
		return repr(self.data)
		
	def isRegularFile(self):
		return stat.S_ISREG(self.stat.st_mode)	
		
	def getFilename(self):
		return os.path.abspath(self._filename)
		
	def getBasename(self):
		return os.path.basename(self._filename)
		
	#A 'shortname' is kinda like the middle ground between a full filename and a basename
	#We give just enough of the full filename so the user knows	generally where the file
	#is. 
	def getShortname(self, parent):
		assert(self is not parent)
		junk = parent.filename.replace(parent.basename, u'')
		return self.filename.replace(junk, u'')
		
	def isParent(self, parent):
		if parent.filename in self.filename:
			return True
		return False
		
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
		if size == 0:
			retVal = "0 Bytes "
			if desc:
				retVal += "(Empty)"
			return retVal
		
		mag = int(math.floor(math.log(size, 1000)))
		#There was a strange problem once, where the round() builtin function
		#started complaining about an Integer Value Error for seemingly no reason
		#It hasn't done it since, but these two lines solved it last time. I have
		#no idea why it complained the first time.
		# abrev = size / (1000.0 ** mag)
		# retVal = str(int(abrev))
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
		