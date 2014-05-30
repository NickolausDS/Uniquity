"""
A way to test the model without running the GUI
"""

from models.uniquity import Uniquity

u = Uniquity()

print u.addFile("/Users/goodcat/projects/uniquity/testing/env", True)

# print u.getDuplicateFiles()

print u.getSortedDuplicateFiles()
