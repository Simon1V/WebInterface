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
from WI.utilities.credentials import Credentials 
from WI.interface.twitter import TwitterInterface



app = FastAPI()
fileState = FileState() 
wiLogger = WILogger()
reddit_logger = wiLogger.setupConditionalLogger(logFilePath='logs/reddit.log', debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)	
snopes_logger = wiLogger.setupConditionalLogger(logFilePath='logs/snopes.log', debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)

@app.get("/")
def hello(): 
	return {"message": "Hello universe."}


@app.get("/twitter")
def readRoot():
	logger = logging.getLogger(__name__)
	credentials = Credentials(pw=None) 
	username, password = credentials.getCredentials("twitter", ["username", "password"])
	logger.debug("Got credentials.")
	# Example:
	twitterInterface = TwitterInterface(username, password)
	twitterInterface.login()
	return 
	twitterInterface.fetch_tweets()



async def run_snopes(search_term):
    scraper = SnopesScraper(snopes_logger)
    response = await scraper.search_snopes(search_term)
    return response


setup()

# Create a queue to store the scraped data
scraped_data_queue = Queue()

app = FastAPI() 

@app.get("/twitter/{params}")
def readRoot():
    return {"Hello": "World"}
	
	
def getTweetsOfAccount(): 
	pass 



@app.get("/reddit")
async def scrapePermalink(permalink: str):


    runner = RedditScraper(permalink=permalink, scraped_data_queue=scraped_data_queue, logger=reddit_logger)


    @wait_for(timeout=300)  # Timeout in seconds
    def run_crawl():
        # Run the crawler
        return runner.run()

    # Run the crawl
    run_crawl()
    
    # Retrieve the scraped data from the queue
    scraped_data = scraped_data_queue.get()


    return scraped_data




@app.get("/snopes")
async def scrapeSnopes(search_term: str):
    print(search_term)
    response = await run_snopes(search_term)
    return response


	
if __name__ == "__main__":

	
	logger = wiLogger.setupConditionalLogger(logFilePath=fileState.LOG_FILE, debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)	
	setup()

	# Create a queue to store the scraped data
	scraped_data_queue = Queue() 
	uvicorn.run(app, host="127.0.0.1", port=8000)