from crawler import crawler
from unittest.mock import ANY, MagicMock, patch


@patch("crawler.crawler.log")
def test_crawl_id_missing(mock_logger):
    crawler.crawl(None, "url")
    mock_logger.error.assert_called_once_with("scan_id(None) or url(url) missing")


@patch("crawler.crawler.log")
def test_crawl_url_missing(mock_logger):
    crawler.crawl("scan_id", None)
    mock_logger.error.assert_called_once_with("scan_id(scan_id) or url(None) missing")


@patch("crawler.crawler.Process")
@patch("crawler.crawler.runner")
def test_crawl_spawns_process(mock_runner, mock_process_class):
    mock_process = MagicMock()
    mock_process_class.return_value = mock_process

    crawler.crawl("scan_id", "url")

    mock_process_class.assert_called_once_with(
        target=mock_runner, args=("scan_id", "url")
    )
    mock_process.start.assert_called_once()
    mock_process.join.assert_called_once()


@patch("crawler.crawler.CrawlerProcess")
def test_crawl_runner_calls_spider(mock_cawler_class):
    mock_runner = MagicMock()
    mock_cawler_class.return_value = mock_runner

    crawler.runner("scan_id", "url")

    mock_cawler_class.assert_called_once_with(
        settings={
            "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
            "DOWNLOAD_HANDLERS": {
                "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
                "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            },
        }
    )
    mock_runner.crawl.assert_called_once_with(crawler.UrlSpider, "scan_id", "url")
    mock_runner.start.assert_called_once()


def test_UrlSpider_init():
    spider = crawler.UrlSpider("scan_id", "http://example.com")
    assert spider.scan_id == "scan_id"
    assert spider.url == "http://example.com"
    assert spider.allowed_domains == ["example.com"]


@patch("crawler.crawler.Request")
def test_UrlSpider_start_requests(mock_request):
    spider = crawler.UrlSpider("scan_id", "http://example.com")
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
    spider = crawler.UrlSpider("scan_id", "http://example.com")
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

    spider = crawler.UrlSpider("scan_id", "http://example.com")
    res = spider.parse(mock_response)
    next(res)

    mock_link_extractor.assert_called_once_with(["example.com"])
    mock_extractor.extract_links.assert_called_once_with(mock_response)
    mock_response.follow.assert_called_once_with(
        "http://example.com/a",
        callback=ANY,
        meta={"depth": 2, "referer": "http://example.com", "playwright": True},
    )


@patch("crawler.crawler.pub_sub")
@patch("crawler.crawler.LinkExtractor")
def test_UrlSpider_parse_stops_crawling_at_max_depth(
    mock_link_extractor, _mock_pub_sub
):
    mock_response = MagicMock()
    mock_response.meta.get.side_effect = [2, "http://google.com"]

    spider = crawler.UrlSpider("scan_id", "http://example.com")
    res = spider.parse(mock_response)
    next(res)

    mock_link_extractor.assert_not_called()
