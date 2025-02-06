# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ProductItem(scrapy.Item):
    id = scrapy.Field()
    name = scrapy.Field()
    regular_price = scrapy.Field()
    promo_price = scrapy.Field()
    rating = scrapy.Field()
    image_links = scrapy.Field()
