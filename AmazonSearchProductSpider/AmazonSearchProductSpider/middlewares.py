from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import NotConfigured
import time
from scrapy import signals
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.exceptions import NotConfigured
from scrapy.utils.response import response_status_message
import scrapy
from fake_headers import Headers
from .settings import PROXIES ,HEADERS
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
import logging
# from fp.fp import FreeProxy
import random

class MyHttpErrorMiddleware(HttpErrorMiddleware):
    logging.info('Now LOADING')
    def process_spider_exception(self, response, exception, spider):
        print("Inside exception ",response.status)
        if response.status==503:
            logging.info('Enter the Dragon!!')
            proxy =random.choice(PROXIES)
            headers =random.choice(HEADERS)
            print(f"Using PROXY : {proxy} for {response.request.url}")
            logging.info(f'TRYING WITH DIFF. PROXY({proxy}) {response.request.url}')
            yield scrapy.Request(response.request.url ,
                                headers= headers,
                                 meta={'retry': True ,'proxy':proxy,'retry_delay':10 })
        else:
            scrapy.Request(response.request.url)


class ShowStatus(RetryMiddleware):
      def process_response(self, request, response, spider):
        print("inside retry mw ",response.status)
        if response.status==503:
            proxy =random.choice(PROXIES)
            print(f"Using PROXY : {proxy}")
            return scrapy.Request(response.request.url , headers=self.headers ,dont_filter=True,
                                  meta={'retry': True ,'proxy':proxy})
        else:
            print("RMW NOT 503")
            return response


class AmazonsearchproductspiderSpiderMiddleware:
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
        spider.logger.info('Spider opened: %s' % spider.name)


class AmazonsearchproductspiderDownloaderMiddleware:
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
        spider.logger.info('Spider opened: %s' % spider.name)
