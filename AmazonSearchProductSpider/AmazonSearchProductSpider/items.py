# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class AmazonsearchproductspiderItem(scrapy.Item):
    url = scrapy.Field()
    title = scrapy.Field()
    ASIN = scrapy.Field()
    image_links = scrapy.Field()
    video_links= scrapy.Field()
    brand=scrapy.Field()
    price = scrapy.Field()
    ratings= scrapy.Field()
    ratings_count = scrapy.Field()
    bullets = scrapy.Field()
    country_of_origin = scrapy.Field()
    weight= scrapy.Field()
    material= scrapy.Field()
    product_path= scrapy.Field()
    item_height = scrapy.Field()
    item_height_unit= scrapy.Field()
    item_length= scrapy.Field()
    item_length_unit= scrapy.Field()
    item_width= scrapy.Field()
    item_width_unit= scrapy.Field()
    MRP= scrapy.Field()
    description= scrapy.Field()
    discount = scrapy.Field()
    offers= scrapy.Field()
    aplus_images= scrapy.Field()
    aplus_text= scrapy.Field()
    special_offers= scrapy.Field()
    stone= scrapy.Field()
    packaging= scrapy.Field()
    warranty_type= scrapy.Field()
    #stone= scrapy.Field()
    date_first_available= scrapy.Field()
    #model_number= scrapy.Field()
    #packer= scrapy.Field()
    #importer= scrapy.Field()
    collection= scrapy.Field()
    metal= scrapy.Field()
    department= scrapy.Field()
    net_quantity= scrapy.Field()
    #best_sellers_rank= scrapy.Field()
    is_discontinued_by_manufacturer= scrapy.Field()
    important_info = scrapy.Field()
    type_of_offers = scrapy.Field()
    offers = scrapy.Field()
    attributes = scrapy.Field()
    # = scrapy.Field()
    dimensions = scrapy.Field()
    ratings_breakdown=scrapy.Field()

    