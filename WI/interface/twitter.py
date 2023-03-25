# -*- coding: utf-8 -*-
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from WI.utilities.logger import WILogger 
from selenium.webdriver.common.by import By

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
import os, time 

# Harvest Twitter data :) 
# Twitter is slighty tougher on the bots but can't defeat Selenium. 

TWITTER_BASE = 'https://www.twitter.com/'

class TwitterInterface():
	def __init__(self,username:str="", password:str="", headless:bool=False): 
		#Config vars. 
		self.username = username
		self.password = password
		
		#State vars. 
		self.loggedIn = False 
		self.headless = False 
		self.tweetsList = [] 
		self.tweetData = dict() 
		
		Options = Options()
		if headless == True:
			Options.headless = True
			
		self.webDriver = webdriver.Firefox(options=Options, executable_path=GeckoDriverManager().install())		

		
		# See docs/tweetExtraction.txt for reasoning for this approach.  
	def getTweetsOfAccount(self, accountName:str, nLastTweets:int ) -> list:
		assert isinstance(accountName, str) and isinstance(nLastTweets, int) and nLastTweets > 0
        # Get the page source until enough of the page is visible for nLastTweets to be extracted. 
        # There is very likely a better way to get the number of currently loaded tweets. 
		twitterAccountURL = TWITTER_BASE + accountName
		enoughDataAvailable = False 
		pageSource = getPageSource(accountName, nLastTweets)
		# Enough data has been loaded, fill up self.tweetsList fit dictionaries containing tweet data. 
		for i in range(0, nLastTweets): 
			pass 
		return self.tweetsList

	def getTweetsWithReplosAccount(self, accountName:str, nLastTweets:int)-> list: 
		pass 

    # for possible future direct multimodal evaluation of tweet. 
	def getTweetScreenshots(self, accountName:str, nLastTweets:int) ->list: 
		pass 

    
	def getTweetScreenshotByURL(self, tweetURL:str) -> list: 
		assert isinstance(tweetURL, str)
		pass 
    
	def getPageSource(self, url:str,nLastTweets:int ) -> str: 
		while(enoughDataAvailable == False): 
			self.webDriver.get(url)
			tweetCount = self.getNumberOfContainedTweets(self.webDriver.page_source)
			if (nLastTweets >= tweetCount): 
				#load more of the page.  
				self.webDriver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
				continue 
			# In case we are done or nLastTweets< tweetCount, terminate loop.
			enoughDataAvailable = True         
		soup = BeautifulSoup(self.webDriver.page_source, features="lxml")
		return str(soup.encode('utf-8'))

    # Only used for debugging. 
	def getPageSourceDbg(self, url:str): 
		self.webDriver.get(url)
		#self.webDriver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
		soup = BeautifulSoup(self.webDriver.page_source, features="lxml")
		return str(soup.encode('utf-8'))

	def getNumberOfContainedTweets(self, htmlSource:str) -> int: 
        
		return 10 
	
	def login(self)->bool:
		assert isinstance(self.username, str) and self.username != "" 
		self.webDriver.get('https://twitter.com/login')
		username = self.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input")
		key.send_keys(self.username)
		
		# Get continue button. 
		continueButton  = self.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")
		self.webDriver.execute_script("arguments[0].click();", key);
		time.sleep(10)
		

		password = self.webDriver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input")
		# sends the password to the password input
		password.send_keys(self.password)
		continueButton = self.webDriver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div")
		self.webDriver.execute_script("arguments[0].click();", key)
		time.sleep(2)
		self.loggedIn = False
		return True 

	def tweet(self, message:str)->bool: 
		assert self.loggedIn == True and isinstance(message, str)  
		pass 
			
	def retweet(self):
		pass 
		
	def like(self): 
		pass 
		
	def follow(self, accountName:str): 
		pass 
	
	def unfollow(self, accountName:str): 
		pass 
		

class TwitterSpiderScrapy(): 
    def __init__(self): 
        pass 

