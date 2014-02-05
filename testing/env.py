#!/usr/bin/python
import os
import random
#This file creates and destroys the testing environment

#The folder we test in.
TESTENV = "testenv" + os.path.sep


class FileMixer(object):


	def __init__(self):	
		self.STDTEXT = "This is a long string of text!!\n"
		#STDTEXT is 32 bytes long. 
		#32*STDTEXT is 1 Kilobyte.
		#32*STDTEXT*1024 is 1 Megabyte.
		#STDFILESIZE = 32*1024 sets data to 1 megabyte
		self.STDFILESIZE = 32*1024
	

	def genFiles(self, name, number, size):
		for i in xrange(0, number):
			filename =  name + str(i)
			afile = open(filename, 'w+')
			for aline in xrange(0, size):
				afile.write(self.STDTEXT)
			afile.close()

	def create(self):
		if not os.path.exists(os.path.dirname(TESTENV)):
			os.mkdir(os.path.dirname(TESTENV))

		#self.genFiles("stdcopy", 10, self.STDFILESIZE)
		#self.genFiles("stdlarge", 2, self.STDFILESIZE*100)	
		self.getrand("foo", TESTENV, 10, 3, 5)

	#creates a parent dir of depth 'level'  with a bunch of random files
	#'number' with 'size' variance in filesize.
	def getrand(self, name, dirname, number, size, level):
		#Base case for recursion
		if level <= 1:
			return 
		newdir = os.path.join(dirname, "dir" + str(level))
		os.mkdir(newdir)
		self.genFiles(os.path.join(newdir, name), random.randint(0, number), random.randint(0, 5) * self.STDFILESIZE)
		return self.getrand(name, newdir, number, size, level-1)


	def clean():
		pass

#debugging

fm = FileMixer()
fm.create()

