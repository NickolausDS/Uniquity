import os
import scanParent

#A file, derived under a scanParent
class ScanObject(scanParent.ScanParent):
	
	def __init__(self, filename):
		scanParent.ScanParent.__init__(self,filename)
		self.stat = os.stat(filename)
		
		self._weakHash = ""
		self._weakHashFunction = None
		self._strongHash = ""
		self._strongHashFunction = None
		
	def __eq__(self, other):
		if super.__eq__(other):
			return True
		elif self.weakHashFunction != other.weakHashFunction:
			raise ValueError("Attempted to compare '%s' and '%s' with differing hash algorithms '%s' and '%s'."
				% (self, other, self.weakHashFunction, other.weakHashFunction))
		elif self.strongHashFunction != other.strongHashFunction:
			raise ValueError("Attempted to compare '%s' and '%s' with differing hash algorithms '%s' and '%s'."
				% (self, other, self.strongHashFunction, other.strongHashFunction))	
		else:
			if self.weakHash and other.weakHash and self.weakHash == other.weakHash:
				if self.strongHash and other.strongHash and self.strongHash == other.strongHash:
					return True
		return False

		
	def getSize(self):
		return self.stat.st_size

	@property
	def hashes(self):
		return (self.weakHash, self.strongHash)

	@property
	def strongHash(self):
		return self._strongHash	
	
	@property
	def strongHashFunction(self):
		return self._strongHashFunction
		
	# @strongHash.setter
	def setStrongHash(self, strongHash, strongHashFunction):
		self._strongHash = strongHash
		self._strongHashFunction = repr(strongHashFunction)

	@property
	def weakHash(self):
		return self._weakHash
	
	@property	
	def weakHashFunction(self):
		return self._weakHashFunction
		
	def setWeakHash(self, weakHash, weakHashFunction):
		self._weakHash = weakHash
		self._weakHashFunction = repr(weakHashFunction)