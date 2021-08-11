import os
from urllib.parse import urlparse
from multiprocessing.context import Process

from scrapy import Request, Spider
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor

from logger import log
from pub_sub import pub_sub


class UrlSpider(Spider):
    name = "url_spider"
    max_depth = os.environ.get("API_CRAWLER_DEPTH", 2)

    def __init__(self, id, url, *args, **kwargs):
        super(UrlSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [urlparse(url).netloc]
        self.id = id
        self.url = url

    def start_requests(self):
        yield Request(self.url, meta={"playwright": True})

    def parse(self, response):
        curr_depth = response.meta.get("depth", 1)

        item = {}
        item["parent_id"] = self.id
        item["url"] = response.url
        item["depth"] = curr_depth
        item["referer"] = response.meta.get("referer", "")
        pub_sub.dispatch(item)

        if curr_depth < self.max_depth:
            for a in LinkExtractor(self.allowed_domains).extract_links(response):
                yield response.follow(
                    a,
                    callback=self.parse,
                    meta={
                        "depth": curr_depth + 1,
                        "referer": response.url,
                        "playwright": True,
                    },
                )
        yield True


def runner(id, url):
    runner = CrawlerProcess(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        }
    )
    runner.crawl(UrlSpider, id, url)
    runner.start()


def crawl(id, url):
    if not id or not url:
        log.error(f"id({id}) or url({url}) missing")
        return

    process = Process(target=runner, args=(id, url))
    process.start()
    process.join()
