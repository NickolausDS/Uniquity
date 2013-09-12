import uniquity
import wx
import logging
import os
import sys

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
		
		self.fileBank.log = logging.getLogger("main")
		
		self.fileBank.log.setLevel(logging.DEBUG)
		self.log = LogRedirecter(None)
		
		self.logh = logging.StreamHandler(self.log)
		self.logh.setFormatter(logging.Formatter("%(levelname)s:%(message)s"))
		self.logh.setLevel(logging.DEBUG)
		
		self.fileBank.log.removeHandler(logging.StreamHandler())
		self.fileBank.log.addHandler(self.logh)
		


	#TOOLBAR MENU EVENTS
	def toolbarMenuAdd(self, e):
		if not self.fileBank.fileListings:
			self.fileMenuOpen(e)
		self.fileBank.start()
		self.fileBank.log.info("Finished.")
		
		self.mainGUI.dupFileOutput.SetValue(self.fileBank.getPrettyOutput())
		# self.mainGUI.dupFileOutput.AppendText("self.mystderr.getvalue()")

	def fileMenuAbout(self,e):
	   # Create a message dialog box
	   dlg = wx.MessageDialog(self, " A sample editor \n in wxPython", "About Sample Editor", wx.OK)
	   dlg.ShowModal() # Shows it
	   dlg.Destroy() # finally destroy it when finished.

	def fileMenuExit(self,e):
	   self.mainGUI.Close(True)  # Close the frame.

	def fileMenuOpen(self,e):
		dirname = "."
		""" Open a file"""
		#dlg = wx.DirDialog(self.mainGUI, "Choose a file", dirname, "", "*.*", wx.OPEN)
		dlg = wx.DirDialog(self.mainGUI, "Choose a Directory", ".")
		if dlg.ShowModal() == wx.ID_OK:
			#self.filename = dlg.GetFilename()
			#self.dirname = dlg.GetDirectory()
			print dlg.GetPath()
			self.fileBank.addFiles([os.path.abspath(dlg.GetPath())], self.MAXDIRDEPTH)
			self.mainGUI.directoryListings.AppendText(dlg.GetPath())
		dlg.Destroy()
		
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
	
	
	
	