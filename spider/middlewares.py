# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import json

from scrapy import signals, Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class SpiderSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class SpiderDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


class MultiAccountAuthMiddleware:
    def __init__(self, tokens_file):
        self.tokens_file = tokens_file
        self.accounts = self.load_tokens()
        self.current_account_index = 0

    @classmethod
    def from_crawler(cls, crawler):
        return cls(tokens_file=crawler.settings.get('TOKENS_FILE'))

    def load_tokens(self):
        with open(self.tokens_file, 'r', encoding='utf-8') as file:
            return json.load(file)

    def save_tokens(self):
        with open(self.tokens_file, 'w', encoding='utf-8') as file:
            json.dump(self.accounts, file, indent=4, ensure_ascii=False)

    def get_current_account(self):
        return self.accounts[self.current_account_index]

    def rotate_account(self):
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts)

    def process_request(self, request, spider):
        account = self.get_current_account()
        request.headers['authorization'] = f'Bearer {account["access_token"]}'
        return None

    def process_response(self, request, response, spider):
        if response.status == 401 or response.status == 407:
            return self.refresh_tokens_and_retry(request, spider)
        return response

    def refresh_tokens_and_retry(self, request, spider):
        account = self.get_current_account()
        refresh_url = 'https://app.chizhik.club/api/v1/x5id/refresh/'
        return Request(
            refresh_url,
            method='POST',
            body=json.dumps({'refresh_token': account['refresh_token']}),
            headers={'Content-Type': 'application/json'},
            callback=self.on_refresh_token_response,
            meta={'original_request': request, 'account_index': self.current_account_index}
        )

    def on_refresh_token_response(self, response):
        account_index = response.meta['account_index']
        account = self.accounts[account_index]
        if response.status == 200:
            data = json.loads(response.text)
            account['access_token'] = data.get('access_token')
            account['refresh_token'] = data.get('refresh_token')
            self.save_tokens()
            original_request = response.meta['original_request']
            original_request.headers['Authorization'] = f'Bearer {account["access_token"]}'
            return original_request.copy()
        else:
            self.rotate_account()
            return self.process_request(response.meta['original_request'], response.meta['spider'])

    def get_headers_for_reload_token(self, account_index):
        account = self.accounts[account_index]
        headers = {
            'accept': 'application/json, text/plain, */*',
            'accept-language': 'ru',
            'appversion': '1.17.0',
            'authorization': f'Bearer {account["access_token"]}',
            'baggage': 'sentry-environment=production,sentry-public_key=d4f93d58429f462cb9ebf00cc7018aa9,sentry-release=chizhik-mobile-app%401.17.0,sentry-trace_id=a88470e807e343c390838714607b1c93',
            'connection': 'keep-alive',
            'content-type': 'application/json',
            'host': 'app.chizhik.club',
            'sentry-trace': 'a88470e807e343c390838714607b1c93-e3eeccc1f8874b92-0',
            'user-agent': 'chizhik_app/394 CFNetwork/1410.1 Darwin/22.6.0',
        }
        return headers
