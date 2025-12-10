import scrapy

class ProductItem(scrapy.Item):
    product_id = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    categoryUrl = scrapy.Field()
    categoryName = scrapy.Field()
    descriptionHtml = scrapy.Field()
    descriptionText = scrapy.Field()
    price = scrapy.Field()
    specs = scrapy.Field()
    attributes = scrapy.Field()
    images = scrapy.Field()       # list of {url, filename}
    image_urls = scrapy.Field()   # for ImagesPipeline
