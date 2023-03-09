import json
import scrapy
from urllib.parse import urljoin
import re
from ..items import AmazonsearchproductspiderItem
import random
from random_user_agent.params import SoftwareName, OperatingSystem
from random_user_agent.user_agent import UserAgent
from scrapy.utils.response import open_in_browser
import numpy as np
import subprocess
from scrapy.utils.project import get_project_settings
import pandas as pd
from loguru import logger
from fake_headers import Headers
import pickle
import streamlit as st
from ..settings import PROXIES,HEADERS ,update_roxy

def get_useragent():
    software_names = [SoftwareName.FIREFOX.value]
    operating_systems = [OperatingSystem.WINDOWS.value]
    user_agent_rotator = UserAgent(software_names=software_names, operating_systems=operating_systems)
    return user_agent_rotator.get_random_user_agent()

class AmazonSearchProductSpider(scrapy.Spider):
    name = "amazon_search_product"
    def start_requests(self):       
        with open('DataStore/keyword_list.pickle', 'rb') as handle:
            keyword_list = pickle.load(handle)
        with open('DataStore/_category.pickle', 'rb') as handle:
            category = pickle.load(handle)
        logger.info('category selected {}'.format(category))
        logger.info('Keyword List before is {}'.format(keyword_list.values()))
        logger.info('Keyword List contains "," {}'.format(',' in list(keyword_list.values())[0]))
        if ',' in list(keyword_list.values())[0]:
            logger.info(keyword_list.values())
            search_text =  [x.strip() for x in list(keyword_list.values())[0].split(',')]
        else:
            logger.info(list(keyword_list.values()))
            search_text = list(keyword_list.values())
        if 'ASIN' in keyword_list.keys():
            for asin in search_text:                
                amazon_search_url = f'https://www.amazon.in/dp/'+str(asin)
                yield scrapy.Request(url=amazon_search_url, 
                                    callback=self.parse,
                                    headers=random.choice(HEADERS))
        else:
            logger.info('In Crawler Category Session State is {}'.format(category))
            for keyword in search_text:
                logger.info('Keyword is {}'.format(keyword))
                if category!='all':
                    amazon_search_url = f'https://www.amazon.in/s?k={keyword}&i='+category+'&page=1'
                else:
                    amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page=1'
                logger.info('URL is {}'.format(amazon_search_url))
                yield scrapy.Request(url=amazon_search_url, 
                                    callback=self.discover_product_urls, 
                                    meta={'keyword': keyword, 'page': 1,},
                                    headers=random.choice(HEADERS))

    def discover_product_urls(self, response):
        page = response.meta['page']
        keyword = response.meta['keyword'] 

        all_asins =[i for i in response.xpath('//*[@data-asin]').xpath('@data-asin').extract() if i!='']

        for asin in all_asins:
             product_url = f'https://www.amazon.in/dp/{asin}'#.split("?")[0]
             print("product_url : ",product_url)
             yield scrapy.Request(url=product_url, callback=self.parse, meta={'keyword': keyword, 'page': page})
        ## Get All Pages
        if page == 1:
            total_pages =int(response.css(".s-pagination-item.s-pagination-disabled::text").getall()[-1])
            available_pages = [pg for pg in range(2,total_pages+1)]
            print(available_pages)
            #available_pages = response.xpath(
            #).getall()
            print("tp_:",available_pages)
#
               #print(f"$$$$$==={page_num}===$$$$$")
            for page_num in available_pages:
                amazon_search_url = f'https://www.amazon.in/s?k={keyword}&page={page_num}'
                yield scrapy.Request(url=amazon_search_url, callback=self.discover_product_urls, meta={'keyword': keyword, 'page': page_num})


    def parse(self, response):
        print(10*"==")
        print(f"Parsing product")
        items= AmazonsearchproductspiderItem()
        #Link = response.css('.a-text-normal').css('a::attr(href)').extract()
        def media_link_cls(img_links):
            images,gif,vid=[],[],[]
            for a in img_links:
                string =a.replace(a.split(".")[-2],"")
                clean_link = string[:-4] + string[-3:]
                ext =clean_link.split('.')[-1]
                if ext in ["jpg", "jpeg", "png","bmp", "tif", "tiff", "svg"]:
                    images.append(clean_link)
                elif ext in ["gif"]:
                    gif.append(clean_link)
                elif ext in ["mp4", "mkv", "flv", "avi", "mov", "wmv", "mpeg", "mpg", "webm"]:
                    vid.append(clean_link)
            return images ,vid 
                
        #image_data = json.loads(re.findall(r"colorImages':.*'initial':\s*(\[.+?\])},\n", response.text)[0])
        #variant_data = re.findall(r'dimensionValuesDisplayData"\s*:\s* ({.+?}),\n', response.text)
        
        feature_bullets = [bullet+'\n' for bullet in response.css("#feature-bullets li ::text").getall()]
        img_links =response.css("#altImages img::attr(src)").getall()

        
        def get_prod_details_table(col):
            try:
                res =response.css(f"#productOverview_feature_div table tr:contains('{col}') td span::text").extract()[1]
                return res
            except:
                pass
            try:
                res =response.css(f"#prodDetails table tr th:contains('{col}') + td::text").extract()[0].strip().replace('\u200e', '')
                return res
            except:
                pass
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('{col}') + td::text").getall()[0]
                return res
            except:
                pass
            try:
                res =response.css(f"#detailBullets_feature_div li:contains('{col}')").css("::text").extract()[-2]
                return res
            except:
                pass
                
        def get_prod_details(col):
            try:
                res =response.css(f"#detailBullets_feature_div li:contains('{col}')").css("::text").extract()[-2]
                return res
            except:
                print(f"[INFO] :{col} NOT FOUND")
                return None 
        def get_prod_specs(col):
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('{col}') + td::text").getall()[0]
                return res
            except:
                print(f"[INFO] :{col} NOT FOUND")
                return None 
        def get_height():
            try:
                if response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Height') + td::text").getall()[0]:
                    res = response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Height') + td::text").getall()[0]
                    return res.strip().split(" ")[0],res.strip().split(" ")[1]
                elif response.css(f"#detailBullets_feature_div li:contains('Item Dimensions LxWxH')").css("::text").extract():
                    res = response.css(f"#detailBullets_feature_div li:contains('Item Dimensions LxWxH')").css("::text").extract()[-2]
                    return res.strip().split("x")[2],res.strip().split("x")[2].strip().split(" ")[1]
            except:
                print(f"[INFO] :Item Height NOT FOUND")
                return None ,None 
        def get_width():
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Width') + td::text").getall()[0]
                return res.strip().split(" ")[0],res.strip().split(" ")[1]
            except:
                print(f"[INFO] :Item Width NOT FOUND")
                return None ,None 
        def get_length():
            try:
                res= response.css(f"#technicalSpecifications_section_1 tr th:contains('Item Length') + td::text").getall()[0]
                return res.strip().split(" ")[0],res.strip().split(" ")[1]
            except:
                print(f"[INFO] :Item Length NOT FOUND")
                return None ,None 

        items["title"]= response.css("#productTitle::text").get("").strip()
        if len(items['title'])>1:

            # BASIC
            items["url"]= response.request.url
            items['ASIN']=str(response.request.url).split('/')[-1]
            items["ratings"]= str(response.css("i[data-hook=average-star-rating] ::text").get("").strip()).split(" ")[0]
            items['image_links'],items['video_links'] = media_link_cls(img_links)
            items["bullets"]= feature_bullets
            items["ratings_count"] = response.css("div[data-hook=total-review-count] ::text").get("").strip()
            items['product_path'] =[i.strip() for i in response.css(f"#wayfinding-breadcrumbs_feature_div li span a").css("::text").getall()]
            items["price"]= response.css("#corePriceDisplay_desktop_feature_div .a-price-whole::text").get()
            items['MRP'] = response.css('#corePriceDisplay_desktop_feature_div .a-size-small .a-offscreen::text').get("")[1:]
            items['discount'] = response.css('#corePriceDisplay_desktop_feature_div div span::text').get("")[1:]
            
            # GET DIMENSIONS
            #items['item_height'],items['item_height_unit'] = get_prod_details_table()
            items['item_height'],items['item_height_unit'] = get_height()
            items['item_length'],items['item_length_unit'] = get_length()
            items['item_width'],items['item_width_unit'] = get_width()
            
    #        # A+ AND DESCRIPTION
            items['aplus_images'] = response.css("#aplus img::attr(src)").getall()
            items['aplus_text'] = ''.join([i.replace("\n"," ").strip() for i in response.css('#aplus p::text').getall()])
            items['description'] = response.css("#productDescription span::text").getall()
            
    #        # PROD SPECS SECTION        
            items['metal']  = get_prod_details_table("Metal")
            items['collection']  = get_prod_details_table("Collection")
            #items['stone']  = get_prod_details_table("Stone")
            items['packaging']  = get_prod_details_table("Packaging")
            items['warranty_type']  = get_prod_details_table("Warranty Type")
            
    #        #items['stone']  = get_prod_specs("Stone")
            #items['model_number']  = get_prod_details_table("Model Number")
            items['brand']=get_prod_details_table('Brand')
            items['material']  = get_prod_details_table("Material")
            items['dimensions'] = get_prod_details_table("Dimensions")
            
            #PROD DETAILS SECTION        
            items["country_of_origin"] = get_prod_details_table("Country of Origin")
            items['weight'] = get_prod_details_table("Item Weight")
            #items['importer']  = get_prod_details_table("Importer")
            #items['packer'] = get_prod_details_table("Packer")
            items['department'] = get_prod_details_table("Department")
            items['date_first_available'] = get_prod_details_table("Date First Available")
            items['is_discontinued_by_manufacturer'] = get_prod_details_table("Is Discontinued By Manufacturer")
            #items['best_sellers_rank'] = get_prod_details_table("Best Sellers Rank")
            items['net_quantity'] = get_prod_details_table("Net Quantity")    
            
            #OFFERS AND INFO
            items['special_offers']="".join([i.strip()  for i in response.css('#quickPromoBucketContent li span::text').getall()])
            items['important_info'] = " ".join(response.css("#important-information p::text").getall())
            items['type_of_offers'] =response.css(".a-carousel-card h6::text").getall()
            items['offers'] =response.css(".a-carousel-card .a-section.a-spacing-none.offers-items-content span::text").getall()

            #Ratings Breakdown
            items['ratings_breakdown'] = response.css("#histogramTable tr::attr('aria-label')").extract()

            
            print(items['title'])          
            yield items
        else:
            yield scrapy.Request(response.request.url)
        
    
    def close_spider(self, spider):
        update_roxy()
        pass
