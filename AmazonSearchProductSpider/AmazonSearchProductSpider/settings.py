# Scrapy settings for AmazonSearchProductSpider project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
# import os
# from loguru import logger

# logger.info('os working directory is {}'.format(os.getcwd()))
BOT_NAME = 'AmazonSearchProductSpider'
SPIDER_MODULES = ['AmazonSearchProductSpider.spiders']
NEWSPIDER_MODULE = 'AmazonSearchProductSpider.spiders'

ROBOTSTXT_OBEY = True
CONCURRENT_REQUESTS = 1
#CONCURRENT_REQUESTS_PER_DOMAIN = 5
#CONCURRENT_REQUESTS_PER_IP = 5
RETRY_HTTP_CODES= [503]
DOWNLOAD_DELAY = 5

AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 2
AUTOTHROTTLE_MAX_DELAY = 8
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.5

DUPEFILTER_CLASS = 'scrapy.dupefilters.BaseDupeFilter'

DOWNLOADER_MIDDLEWARES = {
    # ...
     #'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
     #'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
    #'scrapy.downloadermiddlewares.retry.RetryMiddleware': None,
    #'amazon_us_toys.middlewares.ChangeProxyOn503RetryMiddleware': 543,
    #'amazon_us_toys.middlewares.ShowStatus': 540,
    # ...
}
SPIDER_MIDDLEWARES = {
    #    'amazon_us_toys.middlewares.AmazonUsToysSpiderMiddleware': 543,
        'scrapy.spidermiddlewares.httperror.HttpErrorMiddleware': None,
        'AmazonSearchProductSpider.AmazonSearchProductSpider.middlewares.MyHttpErrorMiddleware': 540,
}

#>>>>>>>>>>>>>>>>>>>>>>>HEADERS AND PROXIES<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

import random
from fake_headers import Headers
from scrapy.spidermiddlewares.httperror import HttpErrorMiddleware
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
import os
def get_useragent():
        software_names = [SoftwareName.FIREFOX.value , SoftwareName.CHROME.value]
        operating_systems = [OperatingSystem.WINDOWS.value,OperatingSystem.MAC.value,OperatingSystem.LINUX.value]
        user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
        return user_agent_rotator.get_random_user_agent()

referer = ['https://www.amazon.in/','https://www.google.com/'] 
HEADERS = [{
            'User-Agent': str(random.choice(get_useragent())),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            # 'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            #'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            # Requests doesn't support trailers
            # 'TE': 'trailers',
            }, Headers(headers=True).generate() 
         ]  

# logger.info('THis is running')
filename = r'AmazonSearchProductSpider/AmazonSearchProductSpider/clean_proxy_list_us.txt'
with open(filename) as file:
    data= file.read()
# logger.info('clean proxy text = {}'.format(data))
PROXIES =data.split("\n")

import urllib.request
import requests
import random
import os
def update_roxy():
    url = 'http://list.didsoft.com/get?email=yogesh.a@goglocal.com&pass=rp49j2&pid=http1000&showcountry=yes&https=yes&country=IN'
    local_filename = r"AmazonSearchProductSpider/AmazonSearchProductSpider/fetched_proxy_list.txt"
    response = requests.get(url)
    response.raise_for_status()

    with open(local_filename, 'w') as file:
        file.write(response.content.decode('utf-8'))
    with open(local_filename,'r') as f:
        data = f.read()

    proxies = data.split("\n")

    with open(r"AmazonSearchProductSpider/AmazonSearchProductSpider/clean_proxy_list_us.txt"),'w' as f:
            for i in proxies:
                if i!="":
                    f.write("https://"+i.split("#")[0]+"\n")
    filename = r"AmazonSearchProductSpider/AmazonSearchProductSpider/clean_proxy_list_us.txt"
    with open(filename) as file:
        proxies = file.read()
    
    print(proxies)
    print("Proxies Updated")
    print("random : ",random.choice(proxies.split('\n')))

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 100
#CONCURRENT_REQUESTS_PER_IP = 100

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'AmazonSearchProductSpider.middlewares.AmazonsearchproductspiderSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    'AmazonSearchProductSpider.middlewares.AmazonsearchproductspiderDownloaderMiddleware': 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    'AmazonSearchProductSpider.pipelines.AmazonsearchproductspiderPipeline': 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
