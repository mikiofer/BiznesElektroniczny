BOT_NAME = "xkom_crawler"

SPIDER_MODULES = ["xkom_crawler.spiders"]
NEWSPIDER_MODULE = "xkom_crawler.spiders"

ROBOTSTXT_OBEY = True

# safe crawl speeds
DOWNLOAD_DELAY = 1.0
RANDOMIZE_DOWNLOAD_DELAY = True

# polite concurrency
CONCURRENT_REQUESTS = 4
CONCURRENT_REQUESTS_PER_DOMAIN = 2

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

ITEM_PIPELINES = {
    "xkom_crawler.pipelines.XkomCrawlerPipeline": 300,
}


FEED_EXPORT_ENCODING = "utf-8"
