# Basic project settings
BOT_NAME = "xkom_products_scraper"

SPIDER_MODULES = ["xkom_products_scraper.spiders"]
NEWSPIDER_MODULE = "xkom_products_scraper.spiders"

ROBOTSTXT_OBEY = True

# politeness
DOWNLOAD_DELAY = 0.8
RANDOMIZE_DOWNLOAD_DELAY = True
CONCURRENT_REQUESTS = 6
CONCURRENT_REQUESTS_PER_DOMAIN = 2

# product limits (adjustable)
MAX_PRODUCTS_GLOBAL = 3000
MAX_PRODUCTS_PER_CATEGORY = 100

# Images
IMAGES_STORE = "images"  # base folder, pipeline will create subfolders per product
IMAGES_MIN_HEIGHT = 10
IMAGES_MIN_WIDTH = 10

# pipelines
ITEM_PIPELINES = {
    # custom images pipeline (defined in pipelines.py)
    "xkom_products_scraper.pipelines.ProductImagesPipeline": 1,
    # store products and produce products.json + full_tree.json
    "xkom_products_scraper.pipelines.ProductStorePipeline": 300,
}

# default headers
DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
    "Accept-Language": "pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7",
}

# export encoding
FEED_EXPORT_ENCODING = "utf-8"
