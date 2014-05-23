import sys
import os
from cx_Freeze import setup, Executable

import subprocess
import shutil

name = "Uniquity"

chlog = open("../changelog.md", "r")
#Read the version number from the first line on the changelog
version = chlog.readline().split()[1]
chlog.close()


# PROJECTPATH = "release"
# PROJECTPATH = os.path.normpath(PROJECTPATH)
# includefiles = [os.path.join(PROJECTPATH, 'assets/')]
includefiles = ["assets"]

# Dependencies are automatically detected, but it might need fine tuning.
build_exe_options = {
	"packages": ["os"], 
	"excludes": ["tkinter"], 
	"include_files":includefiles,
	# "path": sys.path + [PROJECTPATH],
	# "build_exe": PROJECTPATH,
	}

# GUI applications require a different base on Windows (the default is for a
# console application).
base = None
if sys.platform == "win32":
    base = "Win32GUI"

setup(  name = name,
        version = version,
		# path = sys.path + [PROJECTPATH],
        description = "The Unique File Analyzer",
        options = {"build_exe": build_exe_options},
        executables = [Executable("Uniquity.py", base=base)])

if sys.platform == "darwin":
	print "Preparing to package for mac"
	packagename = '-'.join([name, version]) + ".app"
	pathname = "../release/"
	if os.path.exists(pathname+packagename):
		print "Removing old build..."
		shutil.rmtree(pathname+packagename)
	shutil.move("build/" + packagename, "../release/" + packagename)
	print packagename
	os.chdir(pathname)
	print os.path.abspath(".")
	print subprocess.call(["../release/mac_build.sh", packagename], shell=True)
	
