from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger


def main(): 
	twitterInterface = TwitterInterface() 
	tweetList = twitterInterface.fetchTweets("elonmusk")
	for tweetDict in tweetList: 
		print(tweetDict)  

if __name__ == '__main__': 
	main() 