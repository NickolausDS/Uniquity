import os
import math

class FileObject(object):
	
	def __init__(self, filename):
		self.filename = unicode(filename)
		self.hasScanned = False
		
	def __str__(self):
		return str(self.filename)
		
	def __unicode__(self):
		return unicode(self.filename)
		
	def __eq__(self, other):
		if self.filename == other.filename:
			return True
		return False
		
	def equals(self, othersp):
		if self.filename == othersp.filename:
			return True
		else:
			return False
		
	def getFilename(self):
		return os.path.abspath(self.filename)
		
	def getBasename(self):
		return os.path.basename(self.filename)
		
	def contains(self, filename):
		if self.filename in filename:
			return True
		else:
			return False
		
	#Set if the directory has been scanned
	def setHasScanned(self, boolean_status):
		self.hasScanned = boolean_status
		
	#Returns true if the file or directory has been scanned		
	def hasScanned(self):
		return self.hasScanned
		
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
		