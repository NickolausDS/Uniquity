import os


#An object we will scan with uniquity, either a file, or directory
class scanObject(object):
	
	def __init__(self, filename):
		self.filename = filename
		self.hasScanned = False
		
	def __str__(self):
		return str(self.filename)
		
	def __unicode__(self):
		return unicode(self.filename)
		
	def getFilename(self):
		return self.filename
		
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