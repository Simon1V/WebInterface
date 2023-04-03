# -*- coding: utf-8 -*-
from WI.spiders.twitter import TwitterInterface
from WI.utilities.logger import WILogger

def main(): 
	logger = WILogger.setupStandardLogger("logger", "log.txt",level=logging.DEBUG)
	twitterInterface = TwitterInterface() 
	source = twitterInterface.getPageSourceDbg("https://twitter.com/elonmusk")
	print(source) 
if __name__ == "__main__": 
	main() 