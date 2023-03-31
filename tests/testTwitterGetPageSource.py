# -*- coding: utf-8 -*-
from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger
import logging

def main(): 
	wiLogger = WILogger() 
	logger = wiLogger.setupStandardLogger("wiLogger", "log.txt", logging.DEBUG)
	twitterInterface = TwitterInterface() 
	logger.info("Getting page source")
	source = twitterInterface.getPageSourceDbg("https://twitter.com/elonmusk")
	print(source) 
	
if __name__ == "__main__": 
	main() 