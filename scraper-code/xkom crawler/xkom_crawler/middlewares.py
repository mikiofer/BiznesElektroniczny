from scrapy import signals

class XkomCrawlerSpiderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()

class XkomCrawlerDownloaderMiddleware:
    @classmethod
    def from_crawler(cls, crawler):
        return cls()
