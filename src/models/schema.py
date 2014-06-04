"""
This file shouldn't be used as of 0.4.2. It's still used by some objects. When they're 
refactored, this will go away.
"""


#Register the types here
TYPES = ["FILE", "SCANPARENT"]

FILE = (
	("filename", str),
	("shortname", str),
	("basename", str),
	("rootParent", str),
	("size", int),
	("niceSize", str),
	("niceSizeAndDesc", str),
	("weakHash", str),
	("weakHashFunction", str),
	("strongHash", str),
	("strongHashFunction", str),
	)

SCANPARENT = (
	("filename", str),
	)


