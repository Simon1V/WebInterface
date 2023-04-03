from fastapi import FastAPI
from queue import Queue
import logging
from scrapy.crawler import CrawlerRunner
from scrapy.utils.log import configure_logging
from crochet import setup, wait_for

from WI.interface.reddit import OnepagerSpider
from WI.utilities.logger import WILogger
import json

with open("scrapy_settings.json", "r") as f:
    settings = json.load(f)

# Setup crochet
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
def scrapePermalink(permalink: str):
    # Create a CrawlerRunner
    runner = CrawlerRunner(settings)

    # New changes broke the logger, so I disabled it for now
    #logger = WILogger()
    #logger.setupConditionalLogger("logger", logFilePath="logs/scrapy.log",debugLevelConsole=logging.DEBUG, debugLevelFile=logging.INFO,conditionalFormatterForConsole=False)
	#logger.setupStandardLogger("logger", logFilePath="logs/scrapy.log",debugLevelConsole=logging.DEBUG)
    
	# # Configure logging
    # configure_logging(install_root_handler=False)
    # configure_logging(settings=settings)

    # Use crochet's wait_for function to run the crawl in a synchronous manner
    @wait_for(timeout=300)  # Timeout in seconds
    def run_crawl():
        d = runner.crawl(OnepagerSpider, permalink=permalink, scraped_data_queue=scraped_data_queue)
        return d

    # Call the synchronous run_crawl function
    run_crawl()

    # Retrieve the scraped data from the queue
    scraped_data = scraped_data_queue.get()

    return {"Scraped": scraped_data}