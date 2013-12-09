import uniquity
import wx
import logging
import os
import sys
import subprocess

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
		self.files = []
		self.fileMenuNew(None)
		# self.filesToScan = []
		# self.filesScanned = []

		


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
			self.mainGUI.directoryListings.InsertStringItem(0, dlg.GetPath())
		dlg.Destroy()
				
	def toolbarRemoveFile(self, e):
		selection = self.getSelectedInListCtrl(self.mainGUI.directoryListings)
		if not selection:
			self.mainGUI.printStatusError("Select a file or directory to remove it")
		else:
			for selected in selection:
				self.mainGUI.directoryListings.DeleteItem(selected)
				
		# selected = self.mainGUI.directoryListings.GetFocusedItem()
		
	def toolbarViewFile(self, e):
		selected = self.getSelectedInListCtrl(self.mainGUI.dupFileOutput)
		if not selected:
			self.mainGUI.printStatusError("Select a scanned file in the duplicate list to view it")
		else:
			selection = self.mainGUI.dupFileOutput.GetItemText(selected[0])
			if sys.platform == "win32":
				os.startfile(selected[0])
			elif sys.platform == "darwin":
				subprocess.Popen(['open', '-R', selection])
			else:
				self.mainGUI.printStatusERror("I'm sorry, but this tool failed to work for your current platform")
		
	def toolbarDeleteFile(self, e):
		selected = self.getSelectedInListCtrl(self.mainGUI.dupFileOutput)
		if not selected:
			self.mainGUI.printStatusError("Select a scanned duplicate file to delete it. WARNING! THIS BUTTON IS DANGEROUS!!!")
		else:
			errors = False
			skipped = 0
			for each in selected:
				#Skip the display rows (that say "Duplicate:")
				if self.mainGUI.dupFileOutput.GetItemText(each, 1) == "" or "Duplicate" in self.mainGUI.dupFileOutput.GetItemText(each, 1):
					#If this was the only thing selected (and it can't be deleted)
					# selected.remove(each)
					skipped += 1
					continue
				# print self.mainGUI.dupFileOutput.GetItemText(each, 0)
				thefile = self.mainGUI.dupFileOutput.GetItemText(each, 1)
				print thefile
				if thefile:
					if not os.path.exists(thefile):
						self.mainGUI.printStatusError("Already deleted '"+thefile+"', I can't delete it any further!")
						# selected.remove(each)
						skipped += 1
					else:
						try:
							os.remove(thefile)
							self.mainGUI.dupFileOutput.SetItemBackgroundColour(each, "RED")
						except Exception as e:
							errors = True
							self.mainGUI.dupFileOutput.SetItemBackgroundColour(each, "YELLOW")
							skipped += 1
			if errors:
				self.mainGUI.printStatusError("Unable to remove the files marked in yellow")
			else:
				numDs = len(selected) - skipped
				if numDs == 1:
					self.mainGUI.SetStatusText("Deleted " + self.mainGUI.dupFileOutput.GetItemText(each, 1))
				elif numDs > 1:
					self.mainGUI.SetStatusText("Deleted " + str(numDs) + " files.")
				else:
					return
						
				
			
			
		# self.refreshModelFileList()
		# self.refreshDuplicateFileOutput()
		
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
		for keys, vals in dups.items():
			if len(vals) > 1:
				for idx, each in enumerate(vals):
					if idx == 0:
						tuplelist.append(("Duplicates", "") )
					tuplelist.append(("", each))
				tuplelist.append(("",""))
					
		# print str(tuplelist)
		for i in tuplelist:
			# print str(i)
			index = self.mainGUI.dupFileOutput.InsertStringItem(sys.maxint, i[0])
			self.mainGUI.dupFileOutput.SetStringItem(index, 1, i[1])
			# self.mainGUI.dupFileOutput.SetItemBackgroundColour(index, "RED")
					
	
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
	

	