from crawler import crawler
from unittest.mock import ANY, MagicMock, patch


def mock_item():
    return {"scan_id": "scan_id", "url": "url"}


@patch("crawler.crawler.log")
def test_crawl_id_missing(mock_logger):
    item = mock_item()
    item["scan_id"] = None
    crawler.crawl(item)
    mock_logger.error.assert_called_once_with("scan_id(None) or url(url) missing")


@patch("crawler.crawler.log")
def test_crawl_url_missing(mock_logger):
    item = mock_item()
    item["url"] = None
    crawler.crawl(item)
    mock_logger.error.assert_called_once_with("scan_id(scan_id) or url(None) missing")


@patch("crawler.crawler.Process")
@patch("crawler.crawler.runner")
def test_crawl_spawns_process(mock_runner, mock_process_class):
    mock_process = MagicMock()
    mock_process_class.return_value = mock_process
    item = mock_item()
    crawler.crawl(item)

    mock_process_class.assert_called_once_with(target=mock_runner, args=(item,))
    mock_process.start.assert_called_once()
    mock_process.join.assert_called_once()


@patch("crawler.crawler.CrawlerProcess")
def test_crawl_runner_calls_spider(mock_cawler_class):
    mock_runner = MagicMock()
    mock_cawler_class.return_value = mock_runner

    item = mock_item()
    crawler.runner(item)

    mock_cawler_class.assert_called_once_with(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "ASYNCIO_EVENT_LOOP": ANY,
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
    mock_runner.crawl.assert_called_once_with(crawler.UrlSpider, item)
    mock_runner.start.assert_called_once()


def test_UrlSpider_init():
    item = mock_item()
    item["url"] = "http://example.com"
    spider = crawler.UrlSpider(item)
    assert spider.item == item
    assert spider.allowed_domains == ["example.com"]


@patch("crawler.crawler.Request")
def test_UrlSpider_start_requests(mock_request):
    item = mock_item()
    item["url"] = "http://example.com"
    spider = crawler.UrlSpider(item)
    res = spider.start_requests()
    next(res)
    mock_request.assert_called_once_with(
        "http://example.com", meta={"playwright": True}
    )


@patch("crawler.crawler.pub_sub")
@patch("crawler.crawler.LinkExtractor")
def test_UrlSpider_parse_calls_dispatch(_mock_extractor, mock_pub_sub):
    mock_response = MagicMock()
    mock_response.url = "http://example.com"
    mock_response.meta.get.side_effect = [1, "http://google.com"]
    item = mock_item()
    item["url"] = "http://example.com"
    spider = crawler.UrlSpider(item)
    res = spider.parse(mock_response)
    next(res)
    mock_pub_sub.dispatch.assert_called_once_with(
        {
            "scan_id": "scan_id",
            "url": "http://example.com",
            "depth": 1,
            "referer": "http://google.com",
        }
    )


@patch("crawler.crawler.pub_sub")
@patch("crawler.crawler.LinkExtractor")
def test_UrlSpider_parse_crawls_deeper(mock_link_extractor, _mock_pub_sub):
    mock_response = MagicMock()
    mock_response.meta.get.side_effect = [1, "http://google.com"]
    mock_response.url = "http://example.com"

    mock_extractor = MagicMock()
    mock_link_extractor.return_value = mock_extractor
    mock_extractor.extract_links.return_value.__iter__.return_value = [
        "http://example.com/a"
    ]
    item = mock_item()
    item["url"] = "http://example.com"
    spider = crawler.UrlSpider(item)
    res = spider.parse(mock_response)
    next(res)

    mock_link_extractor.assert_called_once_with(["example.com"])
    mock_extractor.extract_links.assert_called_once_with(mock_response)
    mock_response.follow.assert_called_once_with(
        "http://example.com/a",
        callback=ANY,
        meta={
            "depth": 2,
            "referer": "http://example.com",
            "playwright": True,
        },
    )


@patch("crawler.crawler.pub_sub")
@patch("crawler.crawler.LinkExtractor")
def test_UrlSpider_parse_stops_crawling_at_max_depth(
    mock_link_extractor, _mock_pub_sub
):
    mock_response = MagicMock()
    mock_response.meta.get.side_effect = [2, "http://google.com"]
    item = mock_item()
    item["url"] = "http://example.com"
    spider = crawler.UrlSpider(item)
    res = spider.parse(mock_response)
    next(res)

    mock_link_extractor.assert_not_called()
