import os
import sys
import logging

#Set basepath for access to various resources. Basepath can change
#depending on where the user executed this file, or if they executed
#it from a bundled 'frozen' app, so basepath is always needed.
if getattr(sys, 'frozen', False):
    BASEPATH = os.path.dirname(sys.executable)
else:
    BASEPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))

IMAGE_DIR = os.path.join(BASEPATH, "assets")


#Time in seconds for uniquity to post progress updates, on both
#the file_manager and the hasher. 
#Low values: create unnessesary load on the CPU
#High values: create lag time and unresponsiveness to the user
UPDATE_INTERVAL = 0.1 # Time in SECONDS

GUI_UPDATE_INTERVAL = 100 # Time in MILLISECONDS
#Time in seconds we wait for all threads to terminate before we terminate anyway
SHUTDOWN_MAX_WAIT = 1.0

WEAK_HASH = "crc32"
STRONG_HASH = "md5"
#Amount of bytes read from a file per 'click' of the hasher when hashing files. 
BLOCK_SIZE = 65536
#Name of db for storing file metadata. Use ":memory: to store in memory instead of on disk"
DB_BASENAME = "uniquity.db"
DB_DIR = os.path.join(BASEPATH, "data")
DBNAME = os.path.join(DB_DIR, DB_BASENAME)
if not os.path.exists(DB_DIR):
	os.mkdir(DB_DIR)

#LOGGING
MAIN_LOG_NAME = "Uniquity"
MAIN_LOG_LEVEL = logging.WARNING

GUI_LOG_NAME = "GUI"
GUI_LOG_LEVEL = logging.WARNING

#console logging
LOG_TO_CONSOLE = True
CONSOLE_LOG_LEVEL = logging.WARNING
CONSOLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

#allow for someone to override config with a separte file. 
try:
	from config_override import *
except ImportError:
	pass

