import os
import logging

#Note: trailing slash shouldn't be there.
IMAGE_DIR=os.path.join(os.getcwd(), "assets/")


#Time in seconds for uniquity to post progress updates, on both
#the file_manager and the hasher. 
#Low values: create unnessesary load on the CPU
#High values: create lag time and unresponsiveness to the user
UPDATE_INTERVAL = 0.1

WEAK_HASH = "crc32"
STRONG_HASH = "md5"
#Amount of bytes read from a file per 'click' of the hasher when hashing files. 
BLOCK_SIZE = 65536

#LOGGING
MAIN_LOG_NAME = "Uniquity"
MAIN_LOG_LEVEL = logging.DEBUG

GUI_LOG_NAME = "UniquityGUI"
GUI_LOG_LEVEL = logging.DEBUG

#console logging
LOG_TO_CONSOLE = True
CONSOLE_LOG_LEVEL = logging.DEBUG
CONSOLE_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
