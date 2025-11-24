import scrapy

class CategoryItem(scrapy.Item):
    name = scrapy.Field()
    url = scrapy.Field()
    parent = scrapy.Field()      # parent category name (None for root)
    level = scrapy.Field()       # depth in hierarchy
