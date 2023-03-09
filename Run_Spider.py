import pandas as pd
import json
import scrapy
from scrapy.crawler import CrawlerProcess,CrawlerRunner
from urllib.parse import urljoin
import re
import sys
from AmazonSearchProductSpider.AmazonSearchProductSpider.spiders import amazon_in_crawler

crawler = amazon_in_crawler.AmazonSearchProductSpider
process = CrawlerProcess(settings={
    "SPIDER_MIDDLEWARES" : {
    #    'amazon_us_toys.middlewares.AmazonUsToysSpiderMiddleware': 543,
        'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
        'AmazonSearchProductSpider.AmazonSearchProductSpider.middlewares.MyHttpErrorMiddleware': 540,
    },
    "FEEDS": {
        "DataStore/Scrapy_Res.csv": {"format": "csv","overwrite":True},
    }
})
#,"overwrite":True
process.crawl(crawler)
process.start()
