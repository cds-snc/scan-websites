import os
import threading

from asyncio import new_event_loop
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

    def __init__(self, item, *args, **kwargs):
        super(UrlSpider, self).__init__(*args, **kwargs)
        self.allowed_domains = [urlparse(item["url"]).netloc]
        self.item = item

    def start_requests(self):
        yield Request(self.item["url"], meta={"playwright": True})

    def parse(self, response):
        curr_depth = response.meta.get("depth", 1)

        item = self.item
        item["url"] = response.url
        item["depth"] = curr_depth
        item["referer"] = response.meta.get("referer", "")
        pub_sub.dispatch([item])

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
        yield None


def runner(item):
    runner = CrawlerProcess(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "ASYNCIO_EVENT_LOOP": "uvloop.Loop",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
            "PLAYWRIGHT_LAUNCH_OPTIONS": {
                "args": [
                    "--allow-running-insecure-content",
                    "--autoplay-policy=user-gesture-required",
                    "--disable-component-update",
                    "--disable-domain-reliability",
                    "--disable-features=AudioServiceOutOfProcess,IsolateOrigins,site-per-process",
                    "--disable-print-preview",
                    "--disable-setuid-sandbox",
                    "--disable-site-isolation-trials",
                    "--disable-speech-api",
                    "--disable-web-security",
                    "--disk-cache-size=33554432",
                    "--enable-features=SharedArrayBuffer",
                    "--hide-scrollbars",
                    "--ignore-gpu-blocklist",
                    "--mute-audio",
                    "--no-default-browser-check",
                    "--no-pings",
                    "--no-sandbox",
                    "--no-zygote",
                    "--use-gl=swiftshader",
                    "--window-size=1920,1080",
                    "--single-process",
                ]
            },
        }
    )
    runner.crawl(UrlSpider, item)
    runner.start()


def crawl(item):
    if not item["scan_id"] or not item["url"]:
        log.error(f"scan_id({item['scan_id']}) or url({item['url']}) missing")
        return

    process = Process(target=runner, args=(item,))
    background = threading.Thread(target=process.start(), name="Crawler")
    background.start()
    process.join()
