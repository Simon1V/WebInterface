# -*- coding: utf-8 -*-
from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger
from WI.utilities.credentials import Credentials 


def main(): 
	# Abstracted so there can be added a cryptographic pipeline but it's likely overkill for this project at this point. 
	logger = WILogger.setupStandardLogger("logger", "log.txt",level=logging.DEBUG) 
	credentials = Credentials(pw=None) 
	username, password = credentials.getCredentials("twitter", ["username", "password"]) 
	# username and password would not be necessary for scrapping!
	twitterInterface = TwitterInterface(username, password) 
	# Test Login. 
	twitterInterface.login() 

if __name__ == '__main__': 
	main() 