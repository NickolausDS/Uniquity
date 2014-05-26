import os
import sys

import shutil
import subprocess

class Packager(object):
	
	def __init__(self, name, src, dest):
		self.name = name
		self.src = src
		self.dest = dest
		
		#Just a list of successful packages created, its up to the packager
		#method to report on each successful package
		self.packaged = []
		
		self.setup()
				
		self.package()
		
		print ("Successfully packaged: \n\t%s" % "\n\t".join(self.packaged) )
		
		
	def setup(self):
		if not os.path.exists(self.dest):
			os.mkdir(self.dest)
		
	#Last time I implemented this, it cleaned *itself* up. So no, I'm not
	#implementing this right now!
	def cleanup(self):
		pass
		
		
	def package(self):
		
		if sys.platform == "darwin":
			print ("Packaging for MacOSX...")
			#Check if an old version of the package exists
			mac_name = self.name
			if ".app" in mac_name:
				if "/" in mac_name:
					if mac_name.index("/") == len(mac_name) - 1:
						packaged_name = mac_name.replace(".app/", ".dmg")
				else:
					packaged_name = mac_name.replace(".app", ".dmg")
			else:
				packaged_name = mac_name + ".dmg"
				mac_name += ".app"
				
			pn_path = os.path.join(self.dest, packaged_name)
			#remove old version
			if os.path.exists(pn_path):
				print ("Removing old package (%s) so we can create a new one." % pn_path)
				os.remove(pn_path)
			#If the .app isn't in this directory, move it here
			if os.path.abspath(self.src) != os.path.abspath("."):
				if os.path.exists(mac_name):
					print ("Removing old build (%s) so we can package the new one." % mac_name)
					shutil.rmtree(mac_name)
				shutil.copytree(os.path.join(self.src, mac_name), "./" + mac_name)
			#Run the mac dmg packager
			subprocess.call(["./mac_makedmg.sh " + self.name], shell=True)
			#Cleanup
			shutil.move(packaged_name, self.dest)
			#Report success!
			self.packaged.append("MacOSX -- %s" % packaged_name)
			
			
			
if __name__ == "__main__":
	if len(sys.argv) != 4:
		print ("Usage: %s name src dest" % sys.argv[0] )
	else:
		pkg = Packager(sys.argv[1], sys.argv[2], sys.argv[3])
	
				
			