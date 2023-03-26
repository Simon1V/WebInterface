import os 
import json

DEFAULT_CREDENTIALS_DIRECTORY_NAME = 'config'
DEFAULT_CREDENTIALS_FILE_NAME = 'credentials.json'

class Credentials: 
	def __init__(self, pw=None): 
		self.pw = pw
		self.THIS_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
		self.WI_ROOT_DIRECTORY = os.path.dirname(self.THIS_DIRECTORY)  
		self.BASE_DIRECTORY = os.path.dirname(self.WI_ROOT_DIRECTORY)
		self.CONFIG_DIRECTORY = os.path.join(self.BASE_DIRECTORY, DEFAULT_CREDENTIALS_DIRECTORY_NAME) 
		self.DEFAULT_CREDENTIALS_FILE_PATH = os.path.join(self.CONFIG_DIRECTORY, DEFAULT_CREDENTIALS_FILE_NAME) 
	

	def getCredentialsDict(self) -> dict: 
		credFile = open(self.DEFAULT_CREDENTIALS_FILE_PATH, 'r') 
		data = json.load(credFile) 
		credFile.close() 
		return data 
		
	def getCredentials(self, service:str, creds:list)->(str, str):
		credDict = self.getCredentialsDict() 
		print(credDict)
		assert credDict != None 
		serviceDict = credDict.get(service.lower()) 
		# To Do: use creds. 
		return (serviceDict.get("username"), serviceDict.get("password"))