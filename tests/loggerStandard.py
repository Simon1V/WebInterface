# -*- coding: utf-8 -*-
from WI.utilities.logger import WILogger 

def main(): 
	wiLogger = WILogger() 
	scrapperLogger = wiLogger.setupStandardLogger("scrapperLogger", "log.txt")
	scrapperLogger.debug("This is a logger test at debug level")
	scrapperLogger.info("This is a logger test at info level")
	scrapperLogger.warning("This is a logger test at warning level")
	scrapperLogger.error("This is a logger test at error level")
	scrapperLogger.critical("This is a logger test at critical level")
	
if __name__ == '__main__': 
	main() 