import os

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