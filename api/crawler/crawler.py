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

    def __init__(self, job_id, url, *args, **kwargs):
        super(UrlSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [urlparse(url).netloc]
        self.job_id = job_id
        self.url = url

    def start_requests(self):
        yield Request(self.url, meta={"playwright": True})

    def parse(self, response):
        curr_depth = response.meta.get("depth", 1)

        item = {}
        item["job_id"] = self.job_id
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


def runner(job_id, url):
    runner = CrawlerProcess(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        }
    )
    runner.crawl(UrlSpider, job_id, url)
    runner.start()


def crawl(job_id, url):
    if not job_id or not url:
        log.error(f"job_id({job_id}) or url({url}) missing")
        return

    process = Process(target=runner, args=(job_id, url))
    process.start()
    process.join()
