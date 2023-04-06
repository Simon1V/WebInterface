from fastapi import FastAPI
import uvicorn
from queue import Queue
import logging
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from crochet import setup, wait_for


# Seems to be missing in reddit.py currently
#from WI.interface.reddit import OnepagerSpider
from WI.utilities.logger import WILogger
from WI.utilities.filestate import FileState
from WI.interface.reddit import RedditScraper
from WI.interface.snopes import SnopesScraper

import json
import os

app = FastAPI()
fileState = FileState() 
wiLogger = WILogger()



async def run_snopes(search_term):
    scraper = SnopesScraper()

    response = await scraper.search_snopes(search_term)
    return response
	

@app.get("/serverhello")
def hello(): 
	return {"message": "Hello universe."}

@app.get("/twitter")
def readRoot():
	web_driver = webdriver.Firefox( executable_path=GeckoDriverManager().install())	
	logger = logging.getLogger(__name__)
	# Example:
	twitter_bot = TwitterBot(profile_url, username, password, web_driver, logger)
	twitter_bot.login()
	twitter_bot.fetch_tweets()



@app.get("/reddit")
async def scrapePermalink(permalink: str):
    runner = RedditScraper(permalink=permalink, scraped_data_queue=scraped_data_queue)


    @wait_for(timeout=300)  # Timeout in seconds
    def run_crawl():
        # Run the crawler
        return runner.run()

    # Run the crawl
    run_crawl()
    
    # Retrieve the scraped data from the queue
    scraped_data = scraped_data_queue.get()


    return {"Scraped": scraped_data}

@app.get("/snopes")
async def scrapeSnopes(search_term: str):
    print(search_term)
    response = await run_snopes(search_term)
    return response


if __name__ == "__main__":
	os.system('python -m spacy download en_core_web_sm')
	
	with open(fileState.SCRAPY_SETTINGS_FILE, "r") as f:
		settings = json.load(f)
	
	logger = wiLogger.setupConditionalLogger(logFilePath=fileState.LOG_FILE, debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)	
	logger.debug("Current settings: " + str(settings))
	setup()

	# Create a queue to store the scraped data
	scraped_data_queue = Queue() 
	uvicorn.run(app, host="127.0.0.1", port=8000)