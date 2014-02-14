import uniquity
import wx
import logging
import os
import sys
import subprocess

import scanObject

# import thread

from cStringIO import StringIO


class GuiCommands(object):
	
	def __init__(self, theMainWindow):
		self.mainGUI = theMainWindow
		
		#Set options (Consider using a dictionary)
		self.MAXDIRDEPTH = 0
		self.VERBOSITY = "NORMAL"
		self.OUTPUTFORMAT = "LIST"
		self.MAXFILESIZE = 0
		self.HASHALG = "md5"
		self.DEPTH = 0 #Zero means no max self.DEPTH (go forever)
		
		#Set data
		self.fileBank = uniquity.Uniquity()	
		#List of files and dirs we will scan with uniquity	
		self.scanObjects = []
		self.fileMenuNew(None)
		# self.filesToScan = []
		# self.filesScanned = []

		self.dupFileOutputMap = {}


	#TOOLBAR MENU EVENTS
	def toolbarStart(self, e):
		index = 0
		files = []
		while(index != self.mainGUI.directoryListings.GetItemCount() ):
			files.append(self.mainGUI.directoryListings.GetItemText(index))
			index += 1
		
		# files = self.mainGUI.directoryListings.GetColumn(0)
		# print "FILES>" + files
		if not files:
			# self.toolbarAddFiles(e)
			return False
			
		
		self.fileBank.addFiles(files, self.MAXDIRDEPTH)
		self.fileBank.start()
		self.fileBank.log.info("Finished.")
		
		self.refreshDuplicateFileOutput()
		return True
		
	def toolbarAddFiles(self, e):
		dirname = "."
		""" Open a file"""
		dlg = wx.DirDialog(self.mainGUI, "Choose a Directory", ".")
		if dlg.ShowModal() == wx.ID_OK:
			self.addFiles([dlg.GetPath()])
		dlg.Destroy()
				
	def toolbarRemoveFile(self, e):
		selection = self.getSelectedInListCtrl(self.mainGUI.directoryListings)
		if not selection:
			self.mainGUI.printStatusError("Select a file or directory to remove it")
		else:
			self.removeFiles(selection)
				
		# selected = self.mainGUI.directoryListings.GetFocusedItem()
		
	def toolbarViewFile(self, e):
		selected = self.getSelectedDups()
		if not selected:
			self.mainGUI.printStatusError("Select a file in the duplicate list to view it")
		else:
			#We only support opening one file at a time
			selection = selected[0]
			print "DEBUG: " + selection
			# selection = self.mainGUI.dupFileOutput.GetItemText(selected[0], 1)
			if sys.platform == "win32":
				os.startfile(selected[0])
			elif sys.platform == "darwin":
				subprocess.Popen(['open', '-R', selection])
			else:
				self.mainGUI.printStatusERror("I'm sorry, but this tool failed to work for your current platform")
		
	def toolbarDeleteFile(self, e):
		toDelete = self.getSelectedDups()
		if toDelete:
			message = "Are you sure you want to delete these files:\n"
			message += "\n".join(self.getNiceDupNames(toDelete))
			title = "They will never bother you again."
			askDialog = wx.MessageDialog(None, 
										title, 
										message, 
										style=wx.YES_NO | wx.NO_DEFAULT | wx.ICON_EXCLAMATION)
			result = askDialog.ShowModal()
			askDialog.Destroy()	
			if result == wx.ID_YES:
				for theFile in toDelete:
					try:
						os.remove(theFile)
						self.setDupFileOutputBackgroundColor(theFile, "RED")
					except Exception as e:
						self.setDupFileOutputBackgroundColor(theFile, "YELLOW")
		else:
			self.mainGUI.printStatusError("Select one or more duplicate files from the list to delete.")
		
	def fileMenuNew(self, e):
		#Set files to empty
		self.files = []
		
		#If the program is started up for the first time, this won't exist
		try:
			self.mainGUI.directoryListings.ClearAll()
			self.mainGUI.mainSplitter.Unsplit(self.mainGUI.tabHolder)
		except AttributeError:
			pass
				
		#Reset the logger
		self.fileBank = uniquity.Uniquity()
		
		self.fileBank.log = logging.getLogger("main")
		
		self.fileBank.log.setLevel(logging.DEBUG)
		self.log = LogRedirecter(None)
		
		self.logh = logging.StreamHandler(self.log)
		self.logh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
		self.logh.setLevel(logging.DEBUG)
		
		self.fileBank.log.removeHandler(logging.StreamHandler())
		self.fileBank.log.addHandler(self.logh)
		
		
		
		

	def fileMenuAbout(self,e):
		# Create a message dialog box
		message = "A program to find all of the duplicate files on your computer\n\n"
		message += "A creation by Nickolaus Saint at \nWindward Productions"
		dlg = wx.MessageDialog(self.mainGUI, message, "About Uniquity", wx.OK)
		dlg.ShowModal() # Shows it
		dlg.Destroy() # finally destroy it when finished.

	def fileMenuExit(self,e):
	   self.mainGUI.Close(True)  # Close the frame.
	
	def refreshDuplicateFileOutput(self):
		#self.mainGUI.dupFileOutput.SetValue(self.fileBank.getPrettyOutput())
		dups = self.fileBank.secondPass
		# self.mainGUI.leftOutput.ClearAll()
		self.mainGUI.dupFileOutput.ClearAll()
		self.mainGUI.dupFileOutput.InsertColumn(0, "Header Column", width=100)
		self.mainGUI.dupFileOutput.InsertColumn(1, "File Column", width=1000)
		# print self.mainGUI.leftOutput.GetColumnCount()
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
			index = self.mainGUI.dupFileOutput.InsertStringItem(sys.maxint, i[0])
			self.dupFileOutputMap[i] = index
			self.mainGUI.dupFileOutput.SetStringItem(index, 1, i[1])
					
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
					
		for eachList in self.fileBank.secondPass.values():
			for eachFile in eachList:
				if not fileInMasterList(eachFile) or not os.path.exists(eachFile):
					eachList.remove(eachFile)
	
	#Add new files or directories to scan with uniquity
	def addFiles(self, files):
		for each in files:
			newSO = scanObject.scanObject(each)
			self.scanObjects.append(newSO)
			self.mainGUI.directoryListings.InsertStringItem(0, newSO.getFilename())
	
	#Remove files or directories from the list of scanObjects to scan with uniqutiy.		
	def removeFiles(self, files):
		for each in files:
			newSO = scanObject.scanObject(each)
			self.mainGUI.directoryListings.DeleteItem(newSO.getFilename())
			self.scanObjects.remove(newSO)
			
		
	#
	def updateFiles(self):
		pass
	
	def setDupFileOutputBackgroundColor(self, string, wxcolor):
		itemID = self.dupFileOutputMap.get(('', unicode(string)), -1)
		if itemID != -1:
			self.mainGUI.dupFileOutput.SetItemBackgroundColour(itemID, wxcolor)
		else:
			raise Exception("Failed to set LC color, no item named " + str(string) + " Exists.")
	
	#This returns a nice user-viewable path for a requested duplicate file
	#It basically shortenes the beginning of the filename to the basename
	#of the scanObject.
	def getNiceDupName(self, dup):
		for each in self.scanObjects:
			if each.contains(dup):
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
		selected = self.getSelectedInListCtrl(self.mainGUI.dupFileOutput)
		if not selected:
			#return the empty list, nothing was selected
			return selectedFiles
		else:
			for aFile in selected:
				#The text is always a path
				filePath = self.mainGUI.dupFileOutput.GetItemText(aFile, 1)
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
			# next = self.mainGUI.directoryListings.GetNextSelected(listctrl, current)
			next = listctrl.GetNextSelected(current)
			if next == -1:
				break
			selection.append(next)
			current = next
		return selection
		
	def getStatus(self):
		pass
		

# class ProgressUpdater(threading.Thread):
# 
# class GUIWorkerQueue(threading.Thread):
# 	def __init__(self):
# 		#init thread
# 		
# 	def run(self):
# 		toScan = [files if files not in self.filesScanned for files in self.filesToScan]
# 		for each in toScan:
# 			
# 		#While there are still files in filesToScan
# 			#Start the progress updater
# 			#Scan a directory
		
		
		
class LogRedirecter(object):	
	def __init__(self, newLocation):
		if not newLocation:
			newLocation = sys.stderr
		self.debug = newLocation
		self.info = newLocation
		self.warning = newLocation
		self.error = newLocation
		self.critical = newLocation
		
	def write(self, thelog):
		string = thelog.split(":")
		thetype = string.pop(0)
		string = ":".join(string)

		if thetype == "DEBUG":
			self.printTo(self.debug, string)
		elif thetype == "INFO":
			self.printTo(self.info, string)
		elif thetype == "WARNING":
			self.printTo(self.warning, string)
		elif thetype == "ERROR":
			self.printTo(self.error, string)
		elif thetype == "CRITICAL":
			self.printTo(self.critical, string)	
		else:
			sys.stderr.write("LOGGER ERROR")
			sys.stderr.write(string)
			
	def printTo(self, outputMethod, string):
			if type(outputMethod) == list:
				outputMethod.append(string)
			if type(outputMethod) == file:
				outputMethod.write(string)
			if type(outputMethod) == type(lambda x: x):
				outputMethod(string)
			else:
				raise LogRedirectionException("The logged message: '"+string+"' was passed to an invalidly set type.")
				
	class LogRedirectionException(Exception):
		def __init__(self, message):
			self.message = message
	

	