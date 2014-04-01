import data.config as config
import logging

#This file is meant to setup preliminary logging, it shouldn't be perminant. Ideally,
#We will have a logger view window which will handle all logging. For the sake of time and 
#usability at this point, we will only do console logging. 

# create logger
logger = logging.getLogger(config.GUI_LOG_NAME)
logger.setLevel(config.GUI_LOG_LEVEL)

formatter = logging.Formatter(config.CONSOLE_FORMAT)

console = None
if config.LOG_TO_CONSOLE:
	console = logging.StreamHandler()
	console.setLevel(config.CONSOLE_LOG_LEVEL)
	console.setFormatter(formatter)
	logger.addHandler(console)
	logger.debug("Logging is setup for console.")