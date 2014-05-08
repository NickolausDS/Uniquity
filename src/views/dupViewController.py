import wx
from wx.lib.pubsub import pub
import logging

import data.config as config
import mainDupView

class DupViewController(object):
	
	def __init__(self, model, viewParent):
		self.uniquity = model
		#We don't need to hold on to the parent, just initialize from it.
		self.view = mainDupView.MainDupView(viewParent)
		self.stats = self.uniquity.getUpdate()
			

		
	def update(self):
		newStats = self.uniquity.getUpdate()
		if self.stats != newStats:
			self.stats = newStats
			self.view.update(self.uniquity.getDuplicateFiles())
			
		
	