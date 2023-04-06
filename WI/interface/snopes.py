from lxml import html
import spacy
from scrapy import Selector
from sklearn.metrics.pairwise import cosine_similarity
import multiprocessing
from bs4 import BeautifulSoup
import aiohttp
import asyncio
from aiohttp import ClientSession
from queue import Queue
from threading import Thread


class SnopesScraper:
    def __init__(self):
        self.html_docs = {}
        self.similarity_cache = {}
        self.nlp = spacy.load('en_core_web_sm')

    async def fetch(self, session: ClientSession, url: str) -> str:
        async with session.get(url) as response:
            return await response.text()
        


    async def async_filter_fact_check_titles(self, title_link_dict):
        fact_check_titles = {}
        tasks = []
        async with aiohttp.ClientSession() as session:
            for title, link in title_link_dict.items():
                tasks.append(asyncio.ensure_future(self.check_article_type(link)))

            article_types = await asyncio.gather(*tasks)

        for (title, link), article_type in zip(title_link_dict.items(), article_types):
            if article_type.lower() == "fact check": # can handle other article types later
                fact_check_titles[title] = link
            else:
                print(f"Skipping {title} because it is not a fact check article. Article type: {article_type}")

        return fact_check_titles
    


    async def check_article_type(self, link):
        if link not in self.html_docs:
            async with aiohttp.ClientSession() as session:
                response_text = await self.fetch(session, link)
            self.html_docs[link] = response_text

        response = Selector(text=self.html_docs[link])
        article_type = response.css('.section_title::text').getall()[1].strip()

        return article_type

    def process_titles(self, titles, search_doc, search_vector, search_words):
        title_queue = Queue()

        # Put all titles in the queue
        for title in titles:
            title_queue.put(title)

        def worker():
            while not title_queue.empty():
                title = title_queue.get()
                self.similarity_worker(title, search_doc, search_vector, search_words)
                title_queue.task_done()

        # Spawn worker threads
        num_worker_threads = min(multiprocessing.cpu_count(), title_queue.qsize())
        threads = []
        for _ in range(num_worker_threads):
            t = Thread(target=worker)
            t.start()
            threads.append(t)

        # Wait for all threads to finish
        for t in threads:
            t.join()

        # Find the best title based on the max_similarity
        max_similarity = -1
        best_title = None
        for title in titles:
            _, jaccard_similarity, spacy_similarity, cosine_similarity_score = self.similarity_cache[title]
            weighted_similarity = 0.33 * jaccard_similarity + 0.4 * spacy_similarity + 0.27 * cosine_similarity_score

            if weighted_similarity > max_similarity:
                max_similarity = weighted_similarity
                best_title = title

        return best_title

    

    async def async_extract_verdict(self, link):
        if link not in self.html_docs:
            async with aiohttp.ClientSession() as session:
                response_text = await self.fetch(session, link)
            self.html_docs[link] = response_text


        response = Selector(text=self.html_docs[link])



        claim = response.css('#fact_check_rating_container > div.claim_wrapper > div::text').get().strip()
        verdict = response.css('div.rating_title_wrap::text').get().strip()
        publish_date = response.css('h3.publish_date::text').get().strip()
        update_date = response.css('span.updated_date::text').get()
        if update_date:
            update_date = update_date.strip()
        else:
            update_date = None

        # get post content and remove the first element
        post_content = response.css('#article-content p:not(:has(img)):not(.advertisment_text)').getall()
        post_content.pop(0)

        cleaned_content = []
        for paragraph in post_content:
            tree = html.fromstring(paragraph)
            for a_tag in tree.xpath('//a'):
                a_tag.drop_tree()
            cleaned_content.append(tree.text_content())

        post_content = "\n".join(cleaned_content).strip().replace('\n', ' ')

        return verdict, claim, post_content, publish_date, update_date

    def similarity_worker(self, title, search_doc, search_vector, search_words):
        if title in self.similarity_cache:
            return self.similarity_cache[title]

        title_doc = self.nlp(title.lower())
        title_vector = title_doc.vector.reshape(1, -1)
        title_words = set(title.lower().split())

        jaccard_similarity = len(search_words.intersection(title_words)) / len(search_words.union(title_words))
        spacy_similarity = search_doc.similarity(title_doc)
        cosine_similarity_score = cosine_similarity(search_vector, title_vector)[0][0]

        self.similarity_cache[title] = (title, jaccard_similarity, spacy_similarity, cosine_similarity_score)
        return self.similarity_cache[title]

    async def search_snopes(self, search_term, jaccard_weight=0.33, spacy_weight=0.4, cosine_weight=0.27):
        url = f'https://www.snopes.com/search/{search_term}/'

        async with aiohttp.ClientSession() as session:
            response_text = await self.fetch(session, url)

        soup = BeautifulSoup(response_text, 'lxml')
        titles = soup.find_all('h3', class_='article_title')
        links = soup.find_all('a', class_='outer_article_link_wrapper')

        title_link_dict = {}
        for title, link in zip(titles, links):
            title_text = title.text
            link_href = link['href']
            title_link_dict[title_text] = link_href

        fact_check_titles = await self.async_filter_fact_check_titles(title_link_dict)

        search_doc = self.nlp(search_term.lower())
        search_vector = search_doc.vector.reshape(1, -1)
        search_words = set(search_term.lower().split())

        best_title = self.process_titles(list(fact_check_titles.keys()), search_doc, search_vector, search_words)


        verdict, claim, post_content, publish_date, update_date = await self.async_extract_verdict(fact_check_titles[best_title])


        response_object = {
            'claim': claim,
            'verdict': verdict,
            'post_content': post_content,
            'publish_date': publish_date,
            'update_date': update_date
        }
        return response_object

