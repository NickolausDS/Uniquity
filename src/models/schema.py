
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


