BOT_NAME = "spider"

SPIDER_MODULES = ["spider.spiders"]
NEWSPIDER_MODULE = "spider.spiders"

ROBOTSTXT_OBEY = False

CONCURRENT_REQUESTS_PER_DOMAIN = 16
CONCURRENT_REQUESTS_PER_IP = 16

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

DOWNLOADER_MIDDLEWARES = {
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
    'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    # 'spider.middlewares.MultiAccountAuthMiddleware': 543,
}

ROTATING_PROXY_LIST_PATH = 'proxies.txt'
ROTATING_PROXY_PAGE_RETRY_TIMES = 5

RETRY_ENABLED = True
RETRY_TIMES = 10
RETRY_HTTP_CODES = [500, 502, 503, 504, 522, 524, 408, 429]

TOKENS_FILE = 'accounts.json'
