from urllib.parse import urlparse

from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor


class UrlSpider(Spider):
    name = "url_spider"
    max_depth = 2

    def __init__(self, url="", *args, **kwargs):
        super(UrlSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [urlparse(url).netloc]
        self.url = url  # py36

    def start_requests(self):
        yield Request(self.url, meta={"playwright": True})

    def parse(self, response):

        curr_depth = response.meta.get('depth', 1)

        item = {}
        item["url"] = response.url
        item["depth"] = curr_depth
        item['referer'] = response.meta.get('referer', '')
        yield item

        for a in LinkExtractor(allow_domains=['canada.ca']).extract_links(response):
            if curr_depth < self.max_depth:
                yield response.follow(a, callback=self.parse, meta={'depth': curr_depth + 1, 'referer': response.url, "playwright": True})


def crawl(url):
    process = CrawlerProcess(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        }
    )
    process.crawl(UrlSpider, url=url)
    process.start()
