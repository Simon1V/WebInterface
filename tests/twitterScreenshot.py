# -*- coding: utf-8 -*-
from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger
import logging

def main(): 
	wiLogger = WILogger() 
	logger = wiLogger.setupStandardLogger("wiLogger", "log.txt", logging.DEBUG)
	twitterInterface = TwitterInterface() 
	url = "https://twitter.com/nvidia/status/1640477201479901185"
	logger.info("Getting screenshot from URL " + url)
	twitterInterface.getTweetScreenshotByURL(url)
	
	
if __name__ == "__main__": 
	main() 