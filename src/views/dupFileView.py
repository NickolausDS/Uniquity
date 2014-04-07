def setDupFileOutputBackgroundColor(self, string, wxcolor):
	itemID = self.dupFileOutputMap.get(('', unicode(string)), -1)
	if itemID != -1:
		self.mainView.dupFileOutput.SetItemBackgroundColour(itemID, wxcolor)
	else:
		raise Exception("Failed to set LC color, no item named " + str(string) + " Exists.")	

#This returns a nice user-viewable path for a requested duplicate file
#It basically shortenes the beginning of the filename to the basename
#of the hashObject.
def getNiceDupName(self, dup):
	for each in self.hashObjects:
		if each.getFilename() in dup:
			return dup.replace(each.getFilename(), each.getBasename())
	
	#This should oly happen if we're given bad data.
	raise Exception("Variable " + str(dup) + " has no parent")
	
#Get a list of dup names (see above method for singles)
def getNiceDupNames(self, dups):
	thelist = []
	for filename in dups:
		thelist.append(self.getNiceDupName(filename))
	return thelist
	
#Gets all selected duplicate files in list, ignores deleted files
#Note: filenames are in unicode
def getSelectedDups(self):
	selectedFiles = []
	selected = self.getSelectedInListCtrl(self.mainView.dupFileOutput)
	if not selected:
		#return the empty list, nothing was selected
		return selectedFiles
	else:
		for aFile in selected:
			#The text is always a path
			filePath = self.mainView.dupFileOutput.GetItemText(aFile, 1)
			#Ignore empty space or rows that say "Duplicate"
			if filePath == "" or "Duplicate" in filePath:
				continue
			elif not os.path.exists(filePath):
				continue
			else:
				selectedFiles.append(filePath)
	return selectedFiles
			
def getSelectedInListCtrl(self, listctrl):
	selection = []
	# start at -1 to get the first selected item
	current = -1
	while True:
		# next = self.mainView.directoryListings.GetNextSelected(listctrl, current)
		next = listctrl.GetNextSelected(current)
		if next == -1:
			break
		selection.append(next)
		current = next
	return selection

def refreshDuplicateFileOutput(self, dupDict=None):
	if not dupDict:
		return

	#This is a hack as to avoid rewriting this method. Hopefully it is refactored so
	#You won't ever see this message. I hope...
	dups = {}
	for keys, vals in dupDict.items():
		newkey = keys[0]
		newval = [v.filename for v in vals]
		dups[newkey] = newval
	#self.mainView.dupFileOutput.SetValue(self.uniquity.getPrettyOutput())
	# dups = self.uniquity.secondPass
	# self.mainView.leftOutput.ClearAll()
	self.mainView.dupFileOutput.ClearAll()
	self.mainView.dupFileOutput.InsertColumn(0, "Header Column", width=100)
	self.mainView.dupFileOutput.InsertColumn(1, "File Column", width=1000)
	# print self.mainView.leftOutput.GetColumnCount()
	# leftColStr = ""
	tuplelist = []
	#Go through ALL the duplicates we have
	for keys, vals in dups.items():
		#We need atleast 1 dup, so larger than 1
		if len(vals) > 1:
			#For each SET of duplicates, we display two columns.
			#The first row says 'duplicates', the last is empty
			#All the middle rows, second columns, the dups are displayed
			for idx, each in enumerate(vals):
				if idx == 0:
					size = self.getNiceSizeInBytes(os.stat(each).st_size)
					tuplelist.append(("Duplicates", "Size: " + size) )
				tuplelist.append(("", each))
			tuplelist.append(("",""))

	# print str(tuplelist)
	for i in tuplelist:
		index = self.mainView.dupFileOutput.InsertStringItem(sys.maxint, i[0])
		self.dupFileOutputMap[i] = index
		self.mainView.dupFileOutput.SetStringItem(index, 1, i[1])

#Method now considered legacy, future calls moved to fileObject		
def getNiceSizeInBytes(self, size):
	if(size < 1000):
		return str(round(size, 2)) + " Bytes (tiny)"
	elif(size < 1000000):
		return str(round(size/1000.0, 2)) + "KB (tiny)"
	elif(size < 1000000000):
		return str(round(size/1000000.0, 2)) + "MB (small)"
	elif(size < 500000000000):
		return str(round(size/1000000.0, 2)) + "MB (kinda big)"
	elif(size < 1000000000000):
		return str(size/1000000000.0) + "GB (large)"
	elif(size < 1000000000000000):
		return str(size/100000000000000.0 + "TB (HUGE)")
	else:
		return "(These things are huge)"


def refreshModelFileList(self):
	#Go through a list of all the files we scanned, and make sure:
	# 1. the file exists
	# 2. the file is within the list of files to scan
	def fileInMasterList(thefile):
		for userDir in self.files:
			print "THIS IS THE USER DRI> " + userDir
			if userDir in thefile:
				return True
		return False

	for eachList in self.uniquity.secondPass.values():
		for eachFile in eachList:
			if not fileInMasterList(eachFile) or not os.path.exists(eachFile):
				eachList.remove(eachFile)