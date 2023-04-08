# -*- coding: utf-8 -*-
import os 
import logging 

DEFAULT_CONFIG_DIRECTORY_NAME = 'config'
DEFAULT_LOGS_DIRECTORY_NAME = 'logs'

DEFAULT_LOGS_FILE_NAME = 'scan.txt'
DEFAULT_CREDENTIALS_FILE_NAME = 'credentials.json'
DEFAULT_TWITTER_COOKIE_FILE_NAME = 'cookies.pkl'

class FileState: 
	def __init__(self):
		self.THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
		self.MODULES_DIRECTORY = os.path.dirname(self.THIS_DIRECTORY)  
		self.BASE_DIRECTORY = os.path.dirname(self.MODULES_DIRECTORY)
		self.CONFIG_DIRECTORY = os.path.join(self.BASE_DIRECTORY, DEFAULT_CONFIG_DIRECTORY_NAME) 
		self.LOG_DIRECTORY = os.path.join(self.BASE_DIRECTORY, DEFAULT_LOGS_DIRECTORY_NAME) 
		self.LOG_FILE = os.path.join(self.LOG_DIRECTORY, DEFAULT_LOGS_FILE_NAME)
		self.CREDENTIALS_FILE = os.path.join(self.CONFIG_DIRECTORY, DEFAULT_CREDENTIALS_FILE_NAME)
		self.TWITTER_COOKIES_FILE = os.path.join(self.CONFIG_DIRECTORY, DEFAULT_TWITTER_COOKIE_FILE_NAME)
	
	def printDirs(self)-> None: 
		print('File State in: ', self.THIS_DIRECTORY)
		print('Modules Directory: ', self.MODULES_DIRECTORY)
		print('Base Directory: ', self.BASE_DIRECTORY)
		print('Config Directory: ', self.CONFIG_DIRECTORY)
		print('Log Directory: ', self.LOG_DIRECTORY)
	