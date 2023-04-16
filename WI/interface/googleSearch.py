import aiohttp
import asyncio
from selectolax.parser import HTMLParser
from dataclasses import dataclass, asdict
import logging

@dataclass
class Result:
    title: str or None
    url: str
    description: str
    source: str

@dataclass
class ResultPage:
    top_content: Result or None
    results: list[Result]


SOURCE_SELECTOR = ".VuuXrf"

TOP_TEXT_SELECTOR = ".LGOjhe"

TOP_HEADER_SELECTOR = ".IZ6rdc"

RESULLTS_SELECTOR = "#search"

TOP_LIST_SELECTOR = ".di3YZe"

class GoogleSearchScraper:
    def __init__(self, logger = None):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        self.logger = logger if logger else logging.getLogger(__name__)

    async def fetch(self, query_string):
        query_string = {
            "q": query_string
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get("https://www.google.com/search", params=query_string, headers=self.headers) as response:


                self.logger.debug("Status: %s", response.status)
                self.logger.debug("Scraping URL: %s", response.url)

                html = await response.text()
                return html
            

    async def get_top_content(self, parser, selector):
        top_content = parser.css_first(selector)

        top_source = top_content.css_first(SOURCE_SELECTOR)
        if top_content.css_matches(TOP_LIST_SELECTOR) is False:  
            top_text = top_content.css_first(TOP_TEXT_SELECTOR)
            top_header = top_content.css_first(TOP_HEADER_SELECTOR)
        else:
            top_text_content = top_content.css_first(TOP_LIST_SELECTOR)
            top_text = top_content.css_first("[role='heading']") 
            top_header = top_text_content.css_first("ul") 


        g_div = top_content.css_first(".g") # location with all site info
        url_tag = g_div.css_first("a")

        return Result(title=top_header.text(deep=True, separator=' ', strip=True) if top_header else None,
                            url=url_tag.attributes["href"], 
                            description=top_text.text(deep=True, separator=' ',strip=True), 
                            source=top_source.text(deep=True, separator=' '))



    async def process_result(self, result):
        source = result.css_first(".VuuXrf")
        title = result.css_first("h3")

        if result.css_matches("[class='g']") == True:
            g_claas = result.css("[class='g'] > div")
            for g in g_claas:
                a_tag = g.css_first("a")
                if a_tag:
                    post_url = a_tag.attributes["href"]
        else:
            a_tag = result.css_first("a")
            post_url = a_tag.attributes["href"]

        span_tags = result.css("span")
        description_text = ""

        for span in span_tags:
            if span.parent.tag != 'cite' and span.parent.parent.css_matches(".byrV5b") == False:
                spannns = span.css_first(":not(.VuuXrf)")
                if spannns:
                    spannns.merge_text_nodes()
                    if len(spannns.css("span")) == 1:
                        if spannns.text(deep=True, separator=' ', strip=True):
                            if spannns.text() == "Translate this page":
                                continue
                            description = spannns.text(deep=True, separator=' ', strip=True)

                            description_text += description

        main_result = Result(title=title.text(deep=True, separator=' ', strip=True) if title else None,
                            url=post_url,
                            description=description_text,
                            source=source.text(deep=True, separator=' ', strip=True) if source else None)
        self.results.append(asdict(main_result))



    async def process_main_results(self, main_results):
        async with aiohttp.ClientSession() as session:
            tasks = [self.process_result(result) for result in main_results]
            await asyncio.gather(*tasks)


    async def async_search(self, search_term):
        self.results = []
        html = await self.fetch(search_term)

        parser = HTMLParser(html)
        res_body = parser.css_first(RESULLTS_SELECTOR)
        main_results = res_body.css(".g ")


        await(self.process_main_results(main_results))
        if parser.css_matches(".xpdopen") is True:
            top_results = await(self.get_top_content(parser, ".xpdopen"))
            page_results = ResultPage(results=self.results, top_content=top_results)
            return page_results
        else:
            page_results = ResultPage(results=self.results, top_content=None)
            return page_results
        


    def search(self, search_term):
        self.results = []
        html = asyncio.run(self.fetch(search_term))
        parser = HTMLParser(html)
        # save html to file
        with open("test.html", "w") as f:
            f.write(html)
        res_body = parser.css_first(RESULLTS_SELECTOR)
        main_results = res_body.css(".g ")

        asyncio.run(self.process_main_results(main_results))
        if parser.css_matches(".xpdopen") is True and parser.css_first(".xpdopen").css_matches(".g") is True:
            top_results = asyncio.run(self.get_top_content(parser, ".xpdopen"))
            page_results = ResultPage(results=self.results, top_content=top_results)
            return page_results
        else:
            self.logger.debug("No top content")
            page_results = ResultPage(results=self.results, top_content=None)
            return page_results
        


