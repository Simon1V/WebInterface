import requests
from scrapy.selector import Selector
from queue import Queue
 
class RedditScraper:
    def __init__(self, permalink=None, scraped_data_queue=None):
        self.permalink = permalink
        self.scraped_data_queue = scraped_data_queue if scraped_data_queue else Queue()


    def age_check(self):
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

    def parse_post(self, response_text):
        sel = Selector(text=response_text)

        post_content = ''.join(sel.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[2]/form/div/div//text()').extract()).strip()
        title = sel.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/p[1]/a//text()').extract_first()
        post_karma = sel.xpath('/html/body/div[3]/div[2]/div/div[2]//text()').extract()
        post_score = int(post_karma[0])
        upvote_percentage = post_karma[-1].strip().replace('%', '').replace('(', '').replace(')', '').replace('upvoted', '')
        upvote_percentage = float(upvote_percentage) / 100
        username = sel.xpath('/html/body/div[4]/div[1]/div[1]/@data-author').extract_first()
        subreddit = sel.css('div.content div.sitetable.linklisting div::attr(data-comments-count)').get()
        date = sel.xpath('/html/body/div[4]/div[1]/div[1]/@data-timestamp').extract_first()
        item = {
            "title": title,
            "post_content": post_content,
            "post_score": post_score,
            "upvote_percentage": upvote_percentage,
            "username": username,
            "subreddit": subreddit,
            "date": date
        }

        self.scraped_data_queue.put(item)
        return item

    def run(self):
        age_check_response = self.age_check()
        if age_check_response.url.startswith('https://old.reddit.com/'):
            print('Successfully passed the age check.')
            post_data = self.parse_post(age_check_response.text)
            print(post_data)
        else:
            print('Failed to pass the age check.')


