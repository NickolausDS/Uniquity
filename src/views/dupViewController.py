import mainDupView


class DupViewController(object):
	
	def __init__(self, model, viewParent):
		self.uniquity = model
		#We don't need to hold on to the parent, just initialize from it.
		self.view = mainDupView.MainDupView(viewParent)
	
	# @property
	# def uniquity(self):
	# 	if not self._uniquity:
	# 		raise AttributeError("The model was never set with setModel()")
	
	# def setModel(self, model):
	# 	self._uniquity = model	
		
	def update(self):
		self.view.update(self.uniquity.getDuplicateFiles())
		
	