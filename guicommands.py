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
		self.fileBank = uniquity.Uniquity()		
		self.mainGUI = theMainWindow
		self.MAXDIRDEPTH = 0
		self.VERBOSITY = "NORMAL"
		self.OUTPUTFORMAT = "LIST"
		self.MAXFILESIZE = 0
		self.HASHALG = "md5"
		self.DEPTH = 0 #Zero means no max self.DEPTH (go forever)
		self.files = []
		# self.filesToScan = []
		# self.filesScanned = []
		
		self.fileBank.log = logging.getLogger("main")
		
		self.fileBank.log.setLevel(logging.DEBUG)
		self.log = LogRedirecter(None)
		
		self.logh = logging.StreamHandler(self.log)
		self.logh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
		self.logh.setLevel(logging.DEBUG)
		
		self.fileBank.log.removeHandler(logging.StreamHandler())
		self.fileBank.log.addHandler(self.logh)
		


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

		for selected in selection:
			self.mainGUI.directoryListings.DeleteItem(selected)
		# selected = self.mainGUI.directoryListings.GetFocusedItem()
		
	def toolbarViewFile(self, e):
		selected = self.getSelectedInListCtrl(self.mainGUI.dupFileOutput)
		if not selected:
			print "ERROR IN TOOLBAR"
		else:
			selection = self.mainGUI.dupFileOutput.GetItemText(selected[0])
			if sys.platform == "win32":
				os.startfile(selected[0])
			elif sys.platform == "darwin":
				print "SELECTED> " + selection
				subprocess.Popen(['open', '-R', selection])
			
		
	def toolbarDeleteFile(self, e):
		selected = self.getSelectedInListCtrl(self.mainGUI.dupFileOutput)
		selection = self.mainGUI.dupFileOutput.GetItemText(selected[0])
		if not selection:
			print "ERROR, NOT IMPLEMENTED YET"
		else:
			os.remove(selection)
			
		self.refreshModelFileList()
		self.refreshDuplicateFileOutput()

	def fileMenuAbout(self,e):
	   # Create a message dialog box
	   dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
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
	

	