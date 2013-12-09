#!/usr/bin/python

import sys
import os
import inspect
from os.path import isfile, isdir
import logging
import hashlib
import wx

import uniquity
import gui

#Handles a Command Line Interface syle input menu
class Commander(object):
	
	def __init__(self, commandLineArgs):
		self.commandName = commandLineArgs.pop(0)
		
		self.VERBOSITY = "NORMAL"
		self.OUTPUTFORMAT = "LIST"
		self.MAXFILESIZE = 0
		self.HASHALG = "md5"
		self.DEPTH = 0 #Zero means no max self.DEPTH (go forever)
		self.files = []
		
		self.parseArgs(commandLineArgs)
		

	def printUsageAndExit(self):
		msg =["Usage: Find files that are EXACTLY the same within the directories provided.",
			"The relationship is many-to-many, so every file will be checked against",
			"every other file across all directories specified.",
			"Example: " + self.commandName + " -h file1 directoryFoo/",
			"FLAGS:",
			"\t(no args): This help message.",
			"\t-g --gui: start the interactive gui",
			"\t-l: list all similar groups of matching files on the same line(default).",
			"\t-h: list all similar groups of matching files in human readable format",
			"\t-v --verbose: Print filename and completion while scanning.",
			"\t-qe: Suppress extraneous output, but print errors.",
			"\t-q --quiet: Suppress errors and extraneous output.",
			"\t-d: specify max depth to traverse directories",
			"\t-s --maxsize: files over size in megabytes given will not be scanned.",
			"\t--algorithm: use a different hash algorithm for verification. (def sha512)",
			"\t\tChoices: " + str(hashlib.algorithms),
			]
			
		print "\n".join(msg)
		exit(1)
	
	def parseArgs(self, argv):
	
		for idx, val in enumerate(argv):
			if(val[0] == '-'):
				if(val == '-v' or val == '--verbose'):
					self.VERBOSITY = "VERBOSE"
				elif(val == '-q' or val == '--quiet'):
					self.VERBOSITY = "QUIET"
				elif(val == '-qe'):
					self.VERBOSITY = "QUIETWITHERRORS"
				elif(val == '-l'):
					self.OUTPUTFORMAT = "LIST"
				elif(val == '-h'):
					self.OUTPUTFORMAT = "HUMAN"
				elif(val == '-d'):
					self.DEPTH = self.__getPosNumFlagArgument('-d', argv, idx)
				elif(val == '-s' or val == "--maxsize"):
					self.MAXFILESIZE = self.__getPosNumFlagArgument('-s', argv, idx)
				elif(val == '-g' or val == '--gui'):
					app = wx.App(False)
					frame = gui.MainWindow(None, "Uniquity -- The Unique File Analyzer")
					app.MainLoop()
					exit(0)
				elif(val == '--algorithm'):
					self.HASHALG = self.__getStrArgument(idx)
					if(self.HASHALG not in hashlib.algorithms):
						sys.stderr.write("Error: '"+self.HASHALG+"' Not an available algorithm.\n")
						exit(1)
				else:
					sys.stderr.write("Flag: '" + val + "' Not recognized.\n")
					exit(1)
			else:
				self.files.append(val)
	def __getStrArgument(self, argNum):
		try:
			arg = sys.argv.pop(argNum + 1)
		except IndexError:
			sys.stderr.write("ERROR: must give a number with the "+name+" flag\n")
			exit(1)
		return arg
		

	def __getPosNumFlagArgument(self, name, argv, argNum):
		try:
			arg = int(sys.argv.pop(argNum + 1))
		except ValueError:
			sys.stderr.write("ERROR: must give a number with the "+name+" flag\n")
			exit(1)
		except IndexError:
			sys.stderr.write("ERROR: must give a number with the "+name+" flag\n")
			exit(1)
		if(arg < 0):
			sys.stderr.write("ERROR: What the hell is a negative directory depth? ("+name+" " + str(self.DEPTH) + ")\n")
			exit(1)
		return arg

	
	def start(self):
		if(len(self.files) == 0):
			self.printUsageAndExit()
		
		fileBank = uniquity.Uniquity()

		if(self.VERBOSITY == "VERBOSE"):
			fileBank.log.setLevel(logging.DEBUG)
		elif(self.VERBOSITY == "QUIET"):
			fileBank.log.setLevel(logging.CRITICAL)
		elif(self.VERBOSITY == "QUIETWITHERRORS"):
			fileBank.log.setLevel(logging.ERROR)
	
		fileBank.addFiles(self.files, self.DEPTH)
		
		fileBank.setHashAlgorithm(self.HASHALG)
		
		fileBank.setMaxFileSize(self.MAXFILESIZE)
		fileBank.start()

		if(self.OUTPUTFORMAT == "HUMAN"):
			fileBank.printPretty()
		else:
			fileBank.printList()



com = Commander(sys.argv)
com.start()
# if (len(sys.argv) == 0):
# 	print "DOING STDIN"
# 	try:
# 		while (True):
# 			fileBank = uniquity.Uniquity()
# 			fileBank.addFiles(raw_input())
# 			fileBank.start()
# 			fileBank.printList()
# 	except EOFError:
# 		pass
	

			
			
			