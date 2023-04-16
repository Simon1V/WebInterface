# -*- coding: utf-8 -*-
from WI.interface.twitter import TwitterInterface

def main(): 
	twitterInterface = TwitterInterface() 
	# Reload session. 
	twitterInterface.reloadSession() 
	
if __name__ == '__main__': 
	main() 