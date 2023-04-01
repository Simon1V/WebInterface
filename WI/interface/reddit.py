from scrapy import Spider, Request, FormRequest
from scrapy.loader import ItemLoader
from scrapy.item import Item, Field

class Redditv3Item(Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = Field()
    subreddit = Field()
    username = Field()
    post_content = Field()
    post_score = Field()
    upvote_percentage = Field()
    date = Field()
    
class OnepagerSpider(Spider):
    name = "onepager"
    allowed_domains = ["old.reddit.com"]
    start_urls = ["https://old.reddit.com/over18?dest=https%3A%2F%2Fold.reddit.com%2F"]

    def __init__(self, permalink=None, scraped_data_queue=None, *args, **kwargs):
        super(OnepagerSpider, self).__init__(*args, **kwargs)
        self.permalink = permalink
        self.scraped_data_queue = scraped_data_queue

    def parse(self, response):
        formdata = {
            'over18': 'yes',
        }
        yield FormRequest.from_response(response, formdata=formdata, callback=self.after_age_check)

    def after_age_check(self, response):
        if response.url.startswith('https://old.reddit.com/'):
            self.logger.info('Successfully passed the age check.')
            if self.permalink:
                yield Request(url=self.permalink, callback=self.parse_post)
        else:
            self.logger.error('Failed to pass the age check.')


    def parse_post(self, response):
        item_loader = ItemLoader(item=Redditv3Item())
        post_content = ''.join(response.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[2]/form/div/div//text()').extract()).strip()
        item_loader.add_value("post_content", post_content)
        title = response.xpath('/html/body/div[4]/div[1]/div[1]/div[2]/div[1]/p[1]/a//text()').extract_first()
        item_loader.add_value("title", title)
        post_karma = response.xpath('/html/body/div[3]/div[2]/div/div[2]//text()').extract()
        post_score = post_karma[0]
        print(post_score)
        # filter so it can be converted to int "19,615" -> 19615
        post_score = int(post_score.replace(',', ''))
        print(post_score)
        item_loader.add_value("post_score", post_score)
        upvote_percentage = post_karma[-1].strip().replace('%', '').replace('(', '').replace(')', '').replace('upvoted', '')
        upvote_percentage = float(upvote_percentage) / 100
        item_loader.add_value("upvote_percentage", upvote_percentage)
        username = response.xpath('/html/body/div[4]/div[1]/div[1]/@data-author').extract_first()
        item_loader.add_value("username", username)
        subreddit = response.xpath('/html/body/div[4]/div[1]/div[1]/@data-subreddit').extract_first()
        item_loader.add_value("subreddit", subreddit)
        date = response.xpath('/html/body/div[4]/div[1]/div[1]/@data-timestamp').extract_first()
        item_loader.add_value("date", date)
        # Load the item from the item_loader
        item = item_loader.load_item()

        # Put the loaded item into the scraped_data_queue
        self.scraped_data_queue.put(item)

        # Yield the item as usual
        yield item
