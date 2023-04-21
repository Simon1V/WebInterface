from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger


def main(): 
	twitterInterface = TwitterInterface() 
	userID = twitterInterface.getUserIDByName("elonmusk")
	print(userID) 

if __name__ == '__main__': 
	main() 