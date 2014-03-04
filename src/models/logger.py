import data.config as config
import logging

# create logger
main = logging.getLogger('Uniquity')
main.setLevel(config.MAIN_LOG_LEVEL)

formatter = logging.Formatter(config.CONSOLE_FORMAT)

console = None
if config.LOG_TO_CONSOLE:
	console = logging.StreamHandler()
	console.setLevel(config.CONSOLE_LOG_LEVEL)
	console.setFormatter(formatter)
	main.addHandler(console)