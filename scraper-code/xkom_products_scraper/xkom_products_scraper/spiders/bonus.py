import scrapy
from xkom_products_scraper.spiders.products import ProductsSpider

class BonusSpider(ProductsSpider):
    name = "bonus"
    
    # Custom settings to ensure we don't overwrite products.json
    # and we don't use the full tree logic.
    custom_settings = {
        # Disable the hardcoded pipeline that writes to products.json
        'ITEM_PIPELINES': {
            'xkom_products_scraper.pipelines.ProductImagesPipeline': 1,
            # We disable ProductStorePipeline by not including it here
        },
        # We can rely on command line -O for output, or set FEED_URI here
    }

    def __init__(self, url=None, limit=10, *args, **kwargs):
        # Initialize the parent class (ProductsSpider)
        super(BonusSpider, self).__init__(*args, **kwargs)
        
        # Store the target URL
        self.target_url = url
        
        # Override the limits from settings.py with the argument provided
        self.limit = int(limit)
        self.max_per_cat = self.limit
        self.max_global = self.limit
        
        # Reset counters
        self.global_count = 0

    def start_requests(self):
        if not self.target_url:
            self.logger.error("No URL provided! Usage: scrapy crawl bonus -a url='...' -a limit=10")
            return

        yield scrapy.Request(
            self.target_url, 
            callback=self.parse_listing, 
            meta={
                "cat_url": self.target_url, 
                "count": 0
            }
        )