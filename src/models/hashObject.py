import os
import fileObject

#A file, derived under a fileObject
class HashObject(fileObject.FileObject):
	
	def __init__(self, filename):
		fileObject.FileObject.__init__(self,filename)
		
		self._weakHash = ""
		self._weakHashFunction = None
		self._strongHash = ""
		self._strongHashFunction = None
		
	def __eq__(self, other):
		"""Extends eq of fileObject, any object with matching hashes is also equal"""
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

	def __repr__(self):
		"""Overrides the parents repr to provide more information"""
		return repr(self.data)

	@property
	def data(self):
		return super(HashObject, self).data + ( 
						self.weakHash, self.weakHashFunction, 
						self.strongHash, self.strongHashFunction,
						)

	@property
	def hashes(self):
		"""two hex-string tuple of weak and strong hash respectively"""
		return (self.weakHash, self.strongHash)

	@property
	def strongHash(self):
		"""hex-string representation for strong hash"""
		return self._strongHash	
	
	@property
	def strongHashFunction(self):
		"""the name of the hash algorithm"""
		return self._strongHashFunction
		
	# @strongHash.setter
	def setStrongHash(self, strongHash, strongHashFunction):
		"""Set the hex-string representation for strong hash, along with the algorithm used"""
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