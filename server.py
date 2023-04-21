from fastapi import FastAPI
import uvicorn
from queue import Queue
import logging


from WI.utilities.logger import WILogger
from WI.utilities.filestate import FileState
from WI.interface.reddit import RedditScraper
from WI.interface.snopes import SnopesScraper
from WI.interface.googleSearch import GoogleSearchScraper
from WI.utilities.credentials import Credentials 
from WI.interface.twitter import TwitterInterface



app = FastAPI()
fileState = FileState() 
wiLogger = WILogger()
reddit_logger = wiLogger.setupConditionalLogger(logFilePath='logs/reddit.log', debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)	
snopes_logger = wiLogger.setupConditionalLogger(logFilePath='logs/snopes.log', debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)
google_logger = wiLogger.setupConditionalLogger(logFilePath='logs/google.log', debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)
# should use one logger as searching reddit will use the google and reddit logger

# Create a queue to store the scraped data
scraped_data_queue = Queue()

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



@app.get("/twitter/{params}")
def readRoot():
    return {"Hello": "World"}
	
	
def getTweetsOfAccount(): 
	pass 



@app.get("/reddit/get_page/")
def scrapePermalink(permalink: str):


    scraper = RedditScraper( scraped_data_queue=scraped_data_queue, logger=reddit_logger)



    scraper.get_page(permalink=permalink)
    
    # Retrieve the scraped data from the queue
    scraped_data = scraped_data_queue.get()


    return scraped_data


@app.get("/reddit/search/")
def scrapePermalink(search_term: str):


    scraper = RedditScraper( scraped_data_queue=scraped_data_queue, logger=reddit_logger)
	

    scraper.search(search_term=search_term)

	# Retrieve the scraped data from the queue
    scraped_data = scraped_data_queue.get()


    return scraped_data



@app.get("/google/")
def scrapePermalink(search_term: str):


    scraper = GoogleSearchScraper(logger=google_logger)
	

    response = scraper.search(search_term=search_term)
    if response.top_content:
        return response.top_content
    else:
    	return(response.results[0])	



@app.get("/snopes")
async def scrapeSnopes(search_term: str):
    scraper = SnopesScraper(snopes_logger)
    response = await scraper.search(search_term)
    return response


	
if __name__ == "__main__":

	
	logger = wiLogger.setupConditionalLogger(logFilePath=fileState.LOG_FILE, debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)	


	uvicorn.run(app, host="127.0.0.1", port=8000)