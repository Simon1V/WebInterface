# -*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler
import logging 
import sys 

class ConditionalFormatter(logging.Formatter):
			def format(self, record):
				if hasattr(record, 'simple') and record.simple:
					return record.getMessage()
				else:
					return logging.Formatter.format(self, record)

class WILogger:
	def __init__(self): 
		pass 
	
	def setupConditionalLogger(self, logFilePath:str, debugLevelConsole:int, debugLevelFile:int, conditionalFormatterForConsole:bool=False):		
		rotatingFile = RotatingFileHandler(logFilePath , mode='a', maxBytes=5 * 1024 * 1024, backupCount=5, encoding=None, delay=0)
			
		rotatingFileFormatter = ConditionalFormatter('%(asctime)s %(levelname)s - %(message)s')
		rotatingFile.setFormatter(rotatingFileFormatter)
		rotatingFile.setLevel(debugLevelFile)
		# The console handler is not conditional, the 'simple' attribute wont work. 
		consoleLogger = logging.StreamHandler(sys.stdout)
		if conditionalFormatterForConsole == False: 
			consoleLoggerFormatter = logging.Formatter('%(asctime)s %(levelname)s - %(message)s')
		else: 
			consoleLoggerFormatter = ConditionalFormatter('%(asctime)s %(levelname)s - %(message)s')
		consoleLogger.setFormatter(consoleLoggerFormatter)
		consoleLogger.setLevel(debugLevelConsole)

		rootLogger = logging.getLogger()
		rootLogger.setLevel(logging.DEBUG)
		rootLogger.addHandler(rotatingFile)
		rootLogger.addHandler(consoleLogger)
		return rootLogger 


	def setupSimpleLogger(self, name:str, logFile:str, level:int=logging.INFO):
		fileHandler = logging.FileHandler(logFile)  
		formatter = logging.Formatter('%(message)s')      
		fileHandler.setFormatter(formatter)
		logger = logging.getLogger(name)
		logger.setLevel(level)
		logger.addHandler(fileHandler)
		return logger

	def setupStandardLogger(self, name:str, logFile:str, level:int=logging.DEBUG):
		formatter = logging.Formatter('%(levelname)s %(asctime)s - %(message)s')      

		consoleHandler = logging.StreamHandler(sys.stdout)
		consoleHandler.setFormatter(formatter)
		consoleHandler.setLevel(level)

		fileHandler = logging.FileHandler(logFile)  
		fileHandler.setFormatter(formatter)
		logger = logging.getLogger(name)
		logger.setLevel(level)
		logger.addHandler(fileHandler)
		logger.addHandler(consoleHandler)
		return logger	


	def setupFileOnlyLogger(self, name:str, logFilePath:str, debugLevelConsole:int, debugLevelFile:int, conditionalFormatterForConsole:bool=False):
		rotatingFile = RotatingFileHandler(logFilePath , mode='a', maxBytes=5 * 1024 * 1024, backupCount=5, encoding=None, delay=0)
		class ConditionalFormatter(logging.Formatter):
			def format(self, record):
				if hasattr(record, 'simple') and record.simple:
					return record.getMessage()
				else:
					return logging.Formatter.format(self, record)

		rotatingFileFormatter = ConditionalFormatter('%(levelname)s %(asctime)s - %(message)s')
		rotatingFile.setFormatter(rotatingFileFormatter)
		rotatingFile.setLevel(debugLevelFile)
		# The console handler is not conditional, the 'simple' attribute wont work. 
		rootLogger = logging.getLogger()
		rootLogger.setLevel(logging.DEBUG)
		rootLogger.addHandler(rotatingFile)
		return rootLogger 