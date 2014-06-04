import fileObject

class ScanObject(fileObject.FileObject):
	
	def __init__(self, filename, rootParent):
		fileObject.FileObject.__init__(self,filename, rootParent)
		self.dbid = None