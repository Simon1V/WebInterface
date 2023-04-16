import requests
from scrapy.selector import Selector
from queue import Queue
import logging
from WI.interface.googleSearch import GoogleSearchScraper
from dataclasses import dataclass, asdict


@dataclass
class RedditResult:
    title: str
    url: str
    post_text: str
    post_score: int
    upvote_ratio: float
    username: str
    subreddit: str
    date: float

def clean_post_content(value):
    return value.strip().replace('\n', ' ')

class RedditScraper:
    def __init__(self, scraped_data_queue=None, logger=None):
        self.scraped_data_queue = scraped_data_queue if scraped_data_queue else Queue()
        self.logger = logger if logger else logging.getLogger(__name__)
        # change log directory
        self.logger.info("RedditScraper initialized.")


    def __age_check(self):
        url = "https://old.reddit.com/over18"
        querystring = {"dest": self.permalink}
        payload = "over18=yes"
        headers = {
            "authority": "old.reddit.com",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "content-type": "application/x-www-form-urlencoded",
            "origin": "https://old.reddit.com",
            "referer": self.permalink,
            "sec-fetch-dest": "document",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        }
        response = requests.post(url, data=payload, headers=headers, params=querystring)
        return response

    def __parse_post(self, response_text):
        self.logger.info("Starting to parse the post.")
        sel = Selector(text=response_text)

        post_content = ''.join(sel.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[2]/form/div/div//text()').extract()).strip()
        post_content = clean_post_content(post_content)
        title = sel.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/p[1]/a//text()').extract_first()
        post_karma = sel.xpath('/html/body/div[3]/div[2]/div/div[2]//text()').extract()
        post_score = int(post_karma[0])
        upvote_percentage = post_karma[-1].strip().replace('%', '').replace('(', '').replace(')', '').replace('upvoted', '')
        upvote_percentage = float(upvote_percentage) / 100
        username = sel.xpath('/html/body/div[4]/div[1]/div[1]/@data-author').extract_first()
        subreddit = sel.css('div.content div.sitetable.linklisting div::attr(data-comments-count)').get()
        date = sel.xpath('/html/body/div[4]/div[1]/div[1]/@data-timestamp').extract_first()
        reddit_page_results = RedditResult(
            title=title,
            url=self.permalink,
            post_text=post_content,
            post_score=post_score,
            upvote_ratio=upvote_percentage,
            username=username,
            subreddit=subreddit,
            date=date
        )
        self.logger.info(f"Parsed post: {reddit_page_results}")
        self.scraped_data_queue.put(reddit_page_results)
        return asdict(reddit_page_results)

    def get_page_nsfw(self, permalink):
        self.permalink = permalink
        age_check_response = self.__age_check() 
        if age_check_response.url.startswith('https://old.reddit.com/'):
            self.logger.debug('Passed the age check.')
            return self.__parse_post(age_check_response.text)

        else:
            self.logger.error('Age check failed.')
            return None
        
    def get_page(self, permalink):
        self.permalink = permalink
        headers = {
            "authority": "old.reddit.com",
            "accept-language": "en-US,en;q=0.9",
            "cache-control": "max-age=0",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36 Edg/111.0.1661.62"
        }
        response = requests.get(permalink, headers=headers)
        print(response.url)
        return self.__parse_post(response.text)
    
    def search(self, search_term, engine='google'):
        search_term = search_term + "Reddit"
        if engine == 'google':
            google_scraper = GoogleSearchScraper()
            search_result = google_scraper.search(search_term)
            first_link = search_result.results[0]["url"].replace('https://www.reddit.com', 'https://old.reddit.com')
            page_content = self.get_page(first_link)
            return page_content
        else:
            raise NotImplementedError(f"Search engine {engine} is not implemented yet.")






