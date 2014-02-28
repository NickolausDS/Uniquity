import sys
import os
sys.path.insert(0, os.path.abspath("../src"))

import models.fileManager
from models import *
import Queue
import time

def testFileManager():
	inq = Queue.Queue()
	outq = Queue.Queue()
	fm = fileManager.FileManager(inq, outq)
	fm.start()
	sp = scanParent.ScanParent('env')
	inq.put(sp)

	fm.shutdown(True)
	inq.join()
	
	assert(inq.empty())
	assert(outq.qsize() == 1)
	assert(len(fm.files) > 0)
	

