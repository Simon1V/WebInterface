# -*- coding: utf-8 -*-
#from bs4 import BeautifulSoup
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
import requests
import random
import string
from urllib.parse import urlencode
from functools import wraps
import json

TWITTER_BASE = 'https://www.twitter.com/'
TWITTER_BASE_EXPLORE = 'https://www.twitter.com/explore'
TWITTER_URL_API = "https://twitter.com/i/api/graphql/BeHK76TOCY3P8nO-FWocjA/UserTweets"
REQUEST_USER_AGENT = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36'
REQUEST_PLATFORMS = ['Linux', 'Windows']

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
	
	# We should agree on a convention camel case vs underscore! 	
	def fetchTweets(self, accountName:str):
		session = requests.Session()
		for cookie in self.webDriver.get_cookies():
			session.cookies.set(cookie['name'], cookie['value'])

		# Get that 
		urlBuilder = UrlBuilder(accountName)

		guestTokenRequest = urlBuilder.getGuestToken()
		print(guestTokenRequest)
		csrfToken = urlBuilder.getCSRF()

		response = requests.post(guestTokenRequest["url"], headers=guestTokenRequest["headers"])
		guestToken = ""
		try: 
			guestToken = response.json()["guestToken"]
			print(f"Guest token: {guestToken}")
		except Exception as err: 
			self.logger.warning("Already logged in. ")
		
		urlBuilder.guestToken = guestToken
		

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
			"x-csrf-token": csrfToken,
			"x-guest-token": guestToken,
			"x-twitter-client-language": "en",
			"x-twitter-active-user": "yes",
			"authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
		}

		params = {
			"variables": variables,
			"features": features,
		}

		def getNextCursor(response_json:list):
			for entry in response_json['data']['user']['result']['timeline_v2']['timeline']['instructions']:
				if 'entries' in entry:
					for content_entry in entry['entries']:
						content = content_entry['content']
						if content['__typename'] == 'TimelineTimelineCursor' and content['cursorType'] == 'Bottom':
							return content['value']
			return None

		response = requests.get(url, headers=headers, json=params)
		response_json = response.json()
		self.logger.debug(response_json) 



		next_cursor = getNextCursor(response_json)
		if next_cursor:
			variables['cursor'] = next_cursor

	def getUserIDByName(self, accountName:str)->int: 
		variables = {
		"screen_name": accountName,
		"withSafetyModeUserFields": True
		}
		features = {
		"blue_business_profile_image_shape_enabled": False,
		"responsive_web_graphql_exclude_directive_enabled": True,
		"verified_phone_label_enabled": False,
		"responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
		"responsive_web_graphql_timeline_navigation_enabled": True
		}
		headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
		"Accept": "/",
		"Accept-Language": "en-US,en;q=0.5",
		"content-type": "application/json",
		"x-csrf-token": "eb504ef2b36b2c48428713d51441b1c4",
		"x-guest-token": "1643097079949000708",
		"x-twitter-client-language": "en",
		"x-twitter-active-user": "yes",
		"authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
		}
		response = requests.get(url, headers=headers)
		userData = response.json()
		URL_BASE = "https://twitter.com/i/api/graphql/k26ASEiniqy4eXMdknTSoQ/UserByScreenName"
		url_params = {
		"variables": json.dumps(variables),
		"features": json.dumps(features)
		}
		url = URL_BASE + "?" + urlencode(url_params)
		self.logger.debug("User ID: "  + str(userID))
		return userID
		
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
		self.webDriver.execute_script("arguments[0].click();", continueButton)
		time.sleep(5)
		
		# Twitter doesn't always generate the same password input field, so to determine which XPATH to use first. 
		# For now: Brute force until the proper XPATH string can be queried by some function. 
		#XPATH1_PW = "/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div/div/div/div[5]/label/div/div[2]/div/input"
		#XPATH2_PW = 		"/html/body/div/div/div/div[1]/div/div/div/div/div/div/div[2]/div[2]/div/div/div[2]/div[2]/div[1]/div/div/div[3]/div/label/div/div[2]/div[1]/input"
		try: 
			# Add brute force here. 
			password=webDriver.find_element(By.XPATH, XPATH1_PW) 
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
		XPATH_TWEET_BUTTON = "/html/body/div[1]/div/div/div[2]/header/div/div/div/div[1]/div[3]/a/div"
		XPATH_TWEET_INPUT = "/html/body/div[1]/div/div/div[1]/div[2]/div/div/div/div/div/div[2]/div[2]/div/div/div/div[3]/div[2]/div[1]/div/div/div/div/div[2]/div[1]/div/div/div/div/div/div[2]/div/div/div/div/label/div[1]/div/div/div/div/div/div[2]/div/div/div/div"
		try: 	
			tweetButton = self.webDriver.find_element(By.XPATH, XPATH_TWEET_BUTTON) 
		except Exception as err: 
			self.logger.error("Could not find tweet button.")
			return False 
		
		return True  
			
	def retweet(self, messageURL:str) -> bool:
		assert self.loggedIn == True and isinstance(messageURL, str)  
		return True  
		
	def like(self, messageURL:str) -> bool: 
		assert self.loggedIn == True and isinstance(messageURL, str)  
		return True  
		
	def follow(self, accountName:str) -> bool: 
		assert self.loggedIn == True and isinstance(accountName, str)
		return True 
	
	def unfollow(self, accountName:str): 
		assert self.loggedIn == True and isinstance(accountName, str)
		return True 
	
	def getFollowerList(self): 
		pass 
	
	def getFollowingList(self): 
		pass 
	
	# Session Management. 	
	def saveSession(self)->bool:
		try: 
			pickle.dump(self.webDriver.get_cookies(), open(self.fileState.DEFAULT_TWITTER_COOKIES_FILE, "wb")) 
		except Exception as err: 
			return False 
			
			
	def reloadSession(self)->bool: 
		try: 
			self.webDriver.get(TWITTER_BASE_EXPLORE) 
		except Exception as err: 
			self.logger.error("Could not reload session due to " + err)
			return False 
		time.sleep(5)
		cookies = pickle.load(open(self.fileState.TWITTER_COOKIES_FILE, "rb"))
		for cookie in cookies:
			self.webDriver.add_cookie(cookie)
		return True 

class UrlBuilder:
	URL_guestToken = "https://api.twitter.com/1.1/guest/activate.json"
	URL_API_INIT = "https://twitter.com/i/api/1.1/branch/init.json"
	URL_userByScreenName = "https://api.twitter.com/graphql/rePnxwe9LZ51nQ7Sn_xN_A/UserByScreenName"
	URL_USER_TWEETS = "https://twitter.com/i/api/graphql/OXXUyHfKYZ-xLx4NcL9-_Q/UserTweets"
	URL_USER_TWEETS_WITH_REPLIES = "https://twitter.com/i/api/graphql/nrdle2catTyGnTyj1Qa7wA/UserTweetsAndReplies"
	URL_TRENDS = "https://twitter.com/i/api/2/guide.json"
	URL_SEARCH = "https://twitter.com/i/api/2/search/adaptive.json"
	URL_TWEET_DETAILS = "https://api.twitter.com/graphql/NNiD2K-nEYUfXlMwGCocMQ/TweetDetail"

	def __init__(self, accountName):
		self.username = accountName.split("/")[-1] if accountName else None
		self.userID = None
		self.guestToken = None
	
	def return_with_headers(func):
		@wraps(func)
		def wrapper(self, *arg, **kw):
			url = func(self, *arg, **kw)
			return dict(headers=self._get_headers(), url=TWITTER_URL_API)
		return wrapper


	def _get_headers(self):
		headers = {
			'authority': 'twitter.com',
			'accept': '*/*',
			'accept-language': 'en-PK,en;q=0.9',
			'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA',
			'content-type': 'application/x-www-form-urlencoded',
			'referer': 'https://twitter.com/',
			'sec-ch-ua': '"Not_A Brand";v="99", "Google Chrome";v="109", "Chromium";v="109"',
			'sec-ch-ua-mobile': '?0',
			'sec-ch-ua-platform': f'"{random.choice(REQUEST_PLATFORMS)}"',
			'sec-fetch-dest': 'empty',
			'sec-fetch-mode': 'cors',
			'sec-fetch-site': 'same-site',
			'user-agent': REQUEST_USER_AGENT,
			'x-csrf-token': self.getCSRF(),
			'x-twitter-active-user': 'yes',
			'x-twitter-client-language': 'en',
		}

		if self.guestToken:
			headers['content-type'] = 'application/json'
			headers['referer'] = f'https://twitter.com/{self.username}'
			headers['sec-fetch-site'] = 'same-origin'
			headers['x-guest-token'] = self.guestToken

		return headers

	@staticmethod
	def getCSRF():
		return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

	@staticmethod
	def _build(url, params):
		return "?".join([url, params])

	@return_with_headers
	def getGuestToken(self):
		return self.URL_guestToken

	@return_with_headers
	def initAPI(self):
		return self.URL_API_INIT

	@return_with_headers
	def userByScreenName(self, username:str):
		params = {
			'variables': f'{{"screen_name":"{username}","withSafetyModeUserFields":true,"withSuperFollowsUserFields":true}}',
			'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true}',
		}
		return self._build(self.URL_userByScreenName, urlencode(params))

	@return_with_headers
	def user_tweets(self, userID:int, replies:bool=False, cursor=None):
		if replies:
			if not cursor:
				params = {
					'variables': f'{{"userId":"{}","count":40,"includePromotedContent":true,"withCommunity":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true}}',
					'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":false}',
				}
			else:
				params = {
					'variables': f'{{"userId":"{userID}","count":40,"cursor":"{cursor}","includePromotedContent":true,"withCommunity":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true}}',
					'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":false}',
				}
			return self._build(self.URL_USER_TWEETS_WITH_REPLIES, urlencode(params))

		if not cursor:
			params = {
				'variables': f'{{"userId":"{userID}","count":40,"includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true}}',
				'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":false}',
			}
		else:
			params = {
				'variables': f'{{"userId":"{userID}","count":40,"cursor":"{cursor}","includePromotedContent":true,"withQuickPromoteEligibilityTweetFields":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true}}',
				'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":false}',
			}
		return self._build(self.URL_USER_TWEETS, urlencode(params))

	@return_with_headers
	def trends(self):
		params = {
			'include_profile_interstitial_type': '1',
			'include_blocking': '1',
			'include_blocked_by': '1',
			'include_followed_by': '1',
			'include_want_retweets': '1',
			'include_mute_edge': '1',
			'include_can_dm': '1',
			'include_can_media_tag': '1',
			'include_ext_has_nft_avatar': '1',
			'include_ext_is_blue_verified': '1',
			'include_ext_verified_type': '1',
			'skip_status': '1',
			'cards_platform': 'Web-12',
			'include_cards': '1',
			'include_ext_alt_text': 'true',
			'include_ext_limited_action_results': 'false',
			'include_quote_count': 'true',
			'include_reply_count': '1',
			'tweet_mode': 'extended',
			'include_ext_collab_control': 'true',
			'include_ext_views': 'true',
			'include_entities': 'true',
			'include_user_entities': 'true',
			'include_ext_media_color': 'true',
			'include_ext_media_availability': 'true',
			'include_ext_sensitive_media_warning': 'true',
			'include_ext_trusted_friends_metadata': 'true',
			'send_error_codes': 'true',
			'simple_quoted_tweet': 'true',
			'count': '20',
			'requestContext': 'launch',
			'candidate_source': 'trends',
			'include_page_configuration': 'false',
			'entity_tokens': 'false',
			'ext': 'mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo,editControl,collab_control,vibe',
		}
		return self._build(self.URL_TRENDS, urlencode(params))

	@return_with_headers
	def search(self, keyword:str, cursor, filter_:str):
		params = {
			'include_profile_interstitial_type': '1',
			'include_blocking': '1',
			'include_blocked_by': '1',
			'include_followed_by': '1',
			'include_want_retweets': '1',
			'include_mute_edge': '1',
			'include_can_dm': '1',
			'include_can_media_tag': '1',
			'include_ext_has_nft_avatar': '1',
			'include_ext_is_blue_verified': '1',
			'include_ext_verified_type': '1',
			'skip_status': '1',
			'cards_platform': 'Web-12',
			'include_cards': '1',
			'include_ext_alt_text': 'true',
			'include_ext_limited_action_results': 'false',
			'include_quote_count': 'true',
			'include_reply_count': '1',
			'tweet_mode': 'extended',
			'include_ext_views': 'true',
			'include_entities': 'true',
			'include_user_entities': 'true',
			'include_ext_media_color': 'true',
			'include_ext_media_availability': 'true',
			'include_ext_sensitive_media_warning': 'true',
			'include_ext_trusted_friends_metadata': 'true',
			'send_error_codes': 'true',
			'simple_quoted_tweet': 'true',
			'q': keyword,
			'query_source': '',
			'count': '20',
			'requestContext': 'launch',
			'pc': '1',
			'spelling_corrections': '1',
			'include_ext_edit_control': 'true',
			'ext': 'mediaStats,highlightedLabel,hasNftAvatar,voiceInfo,enrichments,superFollowMetadata,unmentionInfo,editControl,vibe',
		}

		if filter_ and filter_ == "latest":
			params['tweet_search_mode'] = "live"
		elif filter_ and filter_ == "users":
			params['result_filter'] = "user"
		elif filter_ and filter_ == "photos":
			params['result_filter'] = "image"
		elif filter_ and filter_ == "videos":
			params['result_filter'] = "video"

		if cursor:
			params['cursor'] = cursor

		return self._build(self.URL_SEARCH, urlencode(params))

	@return_with_headers
	def tweet_detail(self, tweetID:int):
		params = {
			'variables': f'{{"focalTweetId":"{tweetID}","with_rux_injections":false,"includePromotedContent":true,"withCommunity":true,"withQuickPromoteEligibilityTweetFields":true,"withBirdwatchNotes":false,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true}}',
			'features': '{"responsive_web_twitter_blue_verified_badge_is_enabled":true,"responsive_web_graphql_exclude_directive_enabled":false,"verified_phone_label_enabled":false,"responsive_web_graphql_timeline_navigation_enabled":true,"responsive_web_graphql_skip_user_profile_image_extensions_enabled":false,"tweetypie_unmention_optimization_enabled":true,"vibe_api_enabled":true,"responsive_web_edit_tweet_api_enabled":true,"graphql_is_translatable_rweb_tweet_is_translatable_enabled":true,"view_counts_everywhere_api_enabled":true,"longform_notetweets_consumption_enabled":true,"tweet_awards_web_tipping_enabled":false,"freedom_of_speech_not_reach_fetch_enabled":false,"standardized_nudges_misinfo":true,"tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled":false,"interactive_text_enabled":true,"responsive_web_text_conversations_enabled":false,"responsive_web_enhance_cards_enabled":false}',
		}
		return self._build(self.URL_TWEET_DETAILS, urlencode(params))



