import sys
import os
from cx_Freeze import setup, Executable

#Setup the packager
BASEPATH = os.path.dirname(__file__)
PACKAGEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
PACKAGEPATH = os.path.join(PACKAGEPATH, "release")
sys.path.append(PACKAGEPATH)
import packager


#Setup name and version
name = "Uniquity"

chlog = open("../changelog.md", "r")
#Read the version number from the first line on the changelog
version = chlog.readline().split()[1]
chlog.close()


#Files to include within the package
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

#Package the application
curpath = os.path.abspath(".")
buildpath =  os.path.abspath("build")
os.chdir(PACKAGEPATH)
pkg = packager.Packager("-".join((name, version)), buildpath, version)
os.chdir(curpath)
	
