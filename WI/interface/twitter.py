# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from selenium.webdriver.firefox.options import Options
from WI.utilities.logger import WILogger 
from WI.utilities.filestate import FileState 
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
		self.fileState = FileState() 
		
		options = Options()
		if headless == True:
			Options.headless = True
		# Passing options is causing trouble currently. 	
		#self.webDriver = webdriver.Firefox(options=Options, executable_path=GeckoDriverManager().install())		
		self.webDriver = webdriver.Firefox( executable_path=GeckoDriverManager().install())		
		self.cookies = 
	
	# We should agree on a convention camel case vs underscore! 	
	def fetch_tweets(self):
        session = requests.Session()
        for cookie in self.webDriver.get_cookies():
            session.cookies.set(cookie['name'], cookie['value'])


        url_builder = UrlBuilder(self.profile_url)

        guest_token_request = url_builder.get_guest_token()
        csfr_token = url_builder._get_csrf()

        response = requests.post(guest_token_request["url"], headers=guest_token_request["headers"])

        if response.status_code == 200:
            guest_token = response.json()["guest_token"]
            print(f"Guest token: {guest_token}")
        else:
            print("Error fetching guest token:", response.status_code, response.text)


        url_builder.guest_token = guest_token


        # count seems to be able to be set to whataver you want, max I've tested is 100 though
        variables = {"userId":"44196397","count":100,"includePromotedContent":True,"withQuickPromoteEligibilityTweetFields":True,"withDownvotePerspective":False,"withReactionsMetadata":False,"withReactionsPerspective":False,"withVoice":True,"withV2Timeline":True}

        features = {
            "blue_business_profile_image_shape_enabled": False,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "tweetypie_unmention_optimization_enabled": True,
            "vibe_api_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": False,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": False,
            "interactive_text_enabled": True,
            "responsive_web_text_conversations_enabled": False,
            "longform_notetweets_richtext_consumption_enabled": False,
            "responsive_web_enhance_cards_enabled": False,
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
            "Accept": "*/*",
            "Accept-Language": "en-US,en;q=0.5",
            "content-type": "application/json",
            "x-csrf-token": csfr_token,
            "x-guest-token": guest_token,
            "x-twitter-client-language": "en",
            "x-twitter-active-user": "yes",
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
        }

        params = {
            "variables": variables,
            "features": features,
        }

        def get_next_cursor(response_json):
            for entry in response_json['data']['user']['result']['timeline_v2']['timeline']['instructions']:
                if 'entries' in entry:
                    for content_entry in entry['entries']:
                        content = content_entry['content']
                        if content['__typename'] == 'TimelineTimelineCursor' and content['cursorType'] == 'Bottom':
                            return content['value']
            return None



        response = requests.get(url, headers=headers, json=params)

        response_json = response.json()

        print(response_json)



        next_cursor = get_next_cursor(response_json)
        if next_cursor:
            variables['cursor'] = next_cursor

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
    
		
	# Debugging function. Thx GPT, this works better. 
	def getPageSourceDbg(self, url:str) -> str: 
		self.webDriver.get(url)
		time.sleep(10)
		htmlSource = self.webDriver.execute_script("return document.documentElement.outerHTML")
		return htmlSource
		

	
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
			
			
	#Fix always returns true.
	def reloadSession()->bool: 
		cookies = pickle.load(open("cookies.pkl", "rb"))
		for cookie in cookies:
			driver.add_cookie(cookie)
		return true 
