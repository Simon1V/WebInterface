# -*- coding: utf-8 -*-
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
from WI.utilities.logger import WILogger 
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
#from selenium.webdriver.chrome.options import Options
from selenium.webdriver.firefox.options import Options
import os
import time 
import logging 
from datetime import datetime 
import pickle 


# Harvest Twitter data :) 
# Twitter is slighty tougher on the bots but can't defeat Selenium. 

TWITTER_BASE = 'https://www.twitter.com/'

class TwitterInterface():
	def __init__(self,username:str="", password:str="", headless:bool=False): 
		#Config vars. 
		self.username = username
		self.password = password
		
		# Get currently initialized custom logger.
		self.logger = logging.getLogger()
		#State vars. 
		self.loggedIn = False 
		self.headless = False 
		self.tweetsList = [] 
		self.tweetData = dict() 
		
		options = Options()
		if headless == True:
			Options.headless = True
		# Passing options is causing trouble currently. 	
		#self.webDriver = webdriver.Firefox(options=Options, executable_path=GeckoDriverManager().install())		
		self.webDriver = webdriver.Firefox( executable_path=GeckoDriverManager().install())		
		
		# See docs/tweetExtraction.txt for reasoning for this approach.  
	def getTweetsOfAccount(self, accountName:str, nLastTweets:int ) -> list:
		assert isinstance(accountName, str) and isinstance(nLastTweets, int) and nLastTweets > 0
        # Get the page source until enough of the page is visible for nLastTweets to be extracted. 
        # There is very likely a better way to get the number of currently loaded tweets. 
		twitterAccountURL = TWITTER_BASE + accountName
		pageSource = self.getPageSource(twitterAccountURL, nLastTweets)
		print(pageSource)
		return 
		for i in range(0, nLastTweets): 
			pass 
		return self.tweetsList

	def getTweetsWithRepliesAccount(self, accountName:str, nLastTweets:int) -> list: 
		pass 

    # for possible future direct multimodal evaluation of tweet. 
	def getTweetScreenshots(self, accountName:str, nLastTweets:int) -> list: 
		pass 

    # Some tweetURLs require to be logged in (example: visibility only for followers), ignore for now. 
	def getTweetScreenshotByURL(self, tweetURL:str) -> bool : 
		assert isinstance(tweetURL, str)
		now = datetime.now() 
		timestring = now.strftime("%d_%m_%Y, %H_%M_%S")
		try: 
			self.webDriver.get(tweetURL)
			time.sleep(3)
			self.webDriver.save_screenshot(timestring + '.png') 
		except Exception as err: 
			return False 
		return True 
    
	def getPageSource(self, url:str,nLastTweets:int ) -> str: 
		self.webDriver.get(url)
		
		htmlSource = ""
		enoughDataAvailable=False 
		
		while(enoughDataAvailable == False): 
			htmlSource = self.webDriver.execute_script("return document.documentElement.outerHTML")
			time.sleep(10)
			tweetCount = self.getNumberOfContainedTweets(htmlSource)
			if (nLastTweets >= tweetCount): 
				#load more of the page.  
				self.webDriver.execute_script("window.scrollTo(0,document.body.scrollHeight)")
				continue 
			# In case we are done or nLastTweets< tweetCount, terminate loop.
			enoughDataAvailable = True         
		#soup = BeautifulSoup(self.webDriver.page_source, features="lxml")
		#return str(soup.encode('utf-8'))
		return htmlSource
		
	# Debugging function. Thx GPT, this works better. 
	def getPageSourceDbg(self, url:str) -> str: 
		self.webDriver.get(url)
		time.sleep(10)
		htmlSource = self.webDriver.execute_script("return document.documentElement.outerHTML")
		return htmlSource
		
	def getNumberOfContainedTweets(self, htmlSource:str) -> int: 
		s1 = r'data-testid="tweetText"'
		s2 = r'data-testid="tweetPhoto"'
		nTweets = htmlSource.count(s1) + htmlSource.count(s2) 
		print(nTweets) 
		#assert nTweets > 0 
		return nTweets 
	
	def login(self)->bool:
		assert isinstance(self.username, str) and self.username != "" 
		self.webDriver.get('https://twitter.com/login')
		# Wait for the page to load otherwise the next method will usually fail. 
		time.sleep(5)
		
		try: 
			#username = self.webDriver.find_element(By.XPATH,"/html/body/div/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input")
			username = self.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input")
		except Exception as err: 
			self.logger.error("Could not find username input field.")
			return False 
		username.send_keys(self.username)
		# Wait a bit until pressing the button, we would not want to appear as bots :). 
		time.sleep(2)
		# Get continue button. 
		try: 
			continueButton  = self.webDriver.find_element(By.XPATH, "/html/body/div[1]/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")
		except Exception as err: 
			self.logger.error("Could not find username/email continue button.") 
			return False 
		self.webDriver.execute_script("arguments[0].click();", continueButton);
		time.sleep(5)
		
		# Twitter doesn't always generate the same password input field, so to determine which XPATH to use first. 
		# For now: Brute force until the proper XPATH string can be queried by some function. 
		XPATH1_PW = "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input"
		XPATH2_PW = "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"
		try: 
			# Add brute force here. 
			password=self.webDriver.find_element(By.XPATH, XPATH1_PW) 
		except Exception as err: 
			self.logger.error("Could not find password field.") 
			return False 
		# sends the password to the password input
		password.send_keys(self.password)
		# Wait a bit until pressing the button, we would not want to appear as bots :). 
		time.sleep(2)
		XPATH_PW_CONTINUE_1 = "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[2]/div/div[1]/div/div/div/div"
		try: 
			#continueButton = self.webDriver.find_element(By.XPATH, "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[6]/div")
			continueButton = self.webDriver.find_element(By.XPATH, XPATH_PW_CONTINUE_1) 
		except Exception as err: 
			self.logger.error("Could not find password continue button.")
			return False 
		self.webDriver.execute_script("arguments[0].click();", continueButton)
		time.sleep(2)
		
		self.loggedIn = False
		return True 

	def tweet(self, message:str, picture:None) -> bool: 
		assert self.loggedIn == True and isinstance(message, str)  
		return True  
			
	def retweet(self, messageURL:str) -> bool:
		assert self.loggedIn == True and isinstance(messageURL, str)  
		return True  
		
	def like(self,messageURL:str) -> bool: 
		assert self.loggedIn == True and isinstance(messageURL, str)  
		return True  
		
	def follow(self, accountName:str) -> bool: 
		assert self.loggedIn == True and isinstance(accountName, str)
		return True 
	
	def unfollow(self, accountName:str): 
		assert self.loggedIn == True and isinstance(accountName, str)
		return True 
	
	def getFollowerList(): 
		pass 
	
	def getFollowingList(): 
		pass 
		
	def saveSession()->bool:
		try: 
			pickle.dump(self.webDriver.get_cookies(), open("cookies.pkl", "wb")) 
		except Exception as err: 
			return False 
	
	def reloadSession()->bool: 
		pass 

class TwitterSpiderScrapy(): 
    def __init__(self): 
        pass 

