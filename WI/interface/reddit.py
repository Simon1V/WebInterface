import requests
from scrapy.selector import Selector
from queue import Queue
import logging
from WI.interface.googleSearch import GoogleSearchScraper
from dataclasses import dataclass, asdict
import spacy
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np



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

def cosine_similarity_np(a, b):
    a_norm = np.linalg.norm(a)
    b_norm = np.linalg.norm(b)
    similarity = np.dot(a, b.T) / (a_norm * b_norm)
    return similarity

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
        post_score = int(post_karma[0].replace(',', ''))
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


    def best_match_spacy(self,search_term, search_results_list, title_weight=0.7, desc_weight=0.3):
        nlp = spacy.load('en_core_web_sm')
        search_doc = nlp(search_term)

        max_similarity = -1
        best_result = None

        for result in search_results_list:
            title_doc = nlp(result["title"])
            title_similarity = search_doc.similarity(title_doc)

            desc_doc = nlp(result["description"])
            desc_similarity = search_doc.similarity(desc_doc)

            similarity = title_weight * title_similarity + desc_weight * desc_similarity

            if similarity > max_similarity:
                max_similarity = similarity
                best_result = result

        return best_result["title"], best_result["link"]



    def best_match_cosine(self,search_term, search_results_list, title_weight=0.7, desc_weight=0.3):
        nlp = spacy.load('en_core_web_sm')
        search_doc = nlp(search_term)
        search_vector = search_doc.vector.reshape(1, -1)

        max_similarity = -1
        best_result = None

        for result in search_results_list:
            title_doc = nlp(result["title"].lower())
            title_vector = title_doc.vector.reshape(1, -1)
            title_similarity = cosine_similarity(search_vector, title_vector)[0][0]

            desc_doc = nlp(result["description"].lower())
            desc_vector = desc_doc.vector.reshape(1, -1)
            desc_similarity = cosine_similarity(search_vector, desc_vector)[0][0]

            similarity = title_weight * title_similarity + desc_weight * desc_similarity

            if similarity > max_similarity:
                max_similarity = similarity
                best_result = result

        return best_result["title"], best_result["link"]


    def best_match_jaccard(self,search_term, search_results_list, title_weight=0.7, desc_weight=0.3):
        search_words = set(search_term.lower().split())

        max_similarity = -1
        best_result = None

        for result in search_results_list:
            title_words = set(result["title"].lower().split())
            title_similarity = len(search_words.intersection(title_words)) / len(search_words.union(title_words))

            desc_words = set(result["description"].lower().split())
            desc_similarity = len(search_words.intersection(desc_words)) / len(search_words.union(desc_words))

            similarity = title_weight * title_similarity + desc_weight * desc_similarity

            if similarity > max_similarity:
                max_similarity = similarity
                best_result = result

        return best_result["title"], best_result["link"]


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
        return self.__parse_post(response.text)
    
    def search(self, search_term, engine='google'):
        google_search_term = search_term + "Reddit"
        if engine == 'google':
            google_scraper = GoogleSearchScraper()
            search_result = google_scraper.search(google_search_term)
            first_link = search_result.results[0]["url"].replace('https://www.reddit.com', 'https://old.reddit.com')

            search_results_list = []
            for result in search_result.results:
                if result["url"].startswith('https://www.reddit.com'):
                    if "/comments/" not in result["url"]:
                        continue
                    title = result["title"]
                    link = result["url"].replace('https://www.reddit.com', 'https://old.reddit.com')
                    description = result["description"]

                    result_dict = {"title": title, "link": link, "description": description}
                    search_results_list.append(result_dict)
            # should do spacy stuff here and pass to each best_match_spacy and best_match_cosine to avoid doing it twice
            best_title_spacy, best_link_spacy = self.best_match_spacy(search_term, search_results_list)

            best_title_cosine, best_link_cosine = self.best_match_cosine(search_term, search_results_list) 

            best_title_jaccard, best_link_jaccard = self.best_match_jaccard(search_term, search_results_list)





            page_content = self.get_page(first_link)
            return page_content
        else:
            raise NotImplementedError(f"Search engine {engine} is not implemented yet.")






