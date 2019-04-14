# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class ScannerItem(scrapy.Item):
    name = scrapy.Field()
    stockx_size = scrapy.Field()
    style_id = scrapy.Field()
    stockx_price = scrapy.Field()
    flightclub_price = scrapy.Field()
    flightclub_size = scrapy.Field()
    stockx_url = scrapy.Field()
    flightclub_url = scrapy.Field()


    pass
class Shoe(scrapy.Item):
    name = scrapy.Field()
    style_id = scrapy.Field()
    size = scrapy.Field()
    profit =scrapy.Field()
    stockx_price = scrapy.Field()
    flightclub_price = scrapy.Field()
    stockx_url = scrapy.Field()
    flightclub_url = scrapy.Field()