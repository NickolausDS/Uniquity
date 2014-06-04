import fileObject
import cursor

class ScanParent(fileObject.FileObject):
	
	DB_TABLE_NAME = "ScanParent"
	DB_SAVE_ATTRS = (
		("filename", str),
		)
	
	def __init__(self, filename):
		fileObject.FileObject.__init__(self,filename)
		self.dbid = None
		
		cursor.Cursor.registerTable(ScanParent)