from WI.interface.twitter import TwitterInterface
from WI.utilities.logger import WILogger


def main(): 
	twitterInterface = TwitterInterface() 
	tweetList = twitterInterface.getTweetsOfAccount("elonmusk", 50)
	for tweetDict in tweetList: 
		print(tweetDict) 
	return
	tweetList = twitterInterface.getTweetsOfAccount("elonmusk", 33)
	for tweetDict in tweetList: 
		print(tweetDict) 
		
	
	# To do: Define behaviour for cases like: 
	'''
	tweetList = twitterInterface.getTweetsOfAccount("nvidia", -3)
	for tweetDict in tweetList: 
		print(tweetDict) 

	tweetList = twitterInterface.getTweetsOfAccount("9084390854jj vnr3", 33)    
	for tweetDict in tweetList: 
		print(tweetDict) 
	'''    

if __name__ == '__main__': 
	main() 