import uniquity


	def sta1import uniquityrt(self):
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

