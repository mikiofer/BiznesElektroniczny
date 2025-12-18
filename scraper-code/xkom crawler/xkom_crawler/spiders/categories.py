import scrapy
from urllib.parse import urljoin
from xkom_crawler.items import CategoryItem

class XkomCategoriesSpider(scrapy.Spider):
    name = "categories"
    allowed_domains = ["x-kom.pl"]
    start_urls = ["https://www.x-kom.pl/"]

    visited = set()  # avoid crawling the same category twice

    def parse(self, response):
        """
        Parse homepage and extract top-level categories.
        """
        # <a role="menuitem"> contains the root categories
        menu_links = response.css('a[role="menuitem"]::attr(href)').getall()

        for link in menu_links:
            url = urljoin(response.url, link)
            if url not in self.visited:
                self.visited.add(url)
                yield CategoryItem(
                    name=response.css(f'a[href="{link}"]::text').get() or "",
                    url=url,
                    parent=None,
                    level=0
                )
                yield scrapy.Request(
                    url,
                    callback=self.parse_category,
                    meta={"parent_name": None, "level": 1}
                )

    def parse_category(self, response):
        """
        Parse a category page. Extracts either:
        - subcategories (in nested <ul>)
        - or ends if no more subcategories exist
        """
        parent_name = response.meta.get("parent_name")
        level = response.meta.get("level")

        # detect category name from page header
        category_name = response.css("h1::text").get() or response.css("title::text").get()
        if category_name:
            category_name = category_name.strip()

        # All category links in the nested menu on category pages
        subcats = response.css("ul > li > a::attr(href)").getall()

        # Filter only category links
        subcats = [u for u in subcats if "/g-" in u or "/g/" in u]

        for sub in subcats:
            url = urljoin(response.url, sub)
            if url not in self.visited:
                self.visited.add(url)

                yield CategoryItem(
                    name=url.split("/")[-1].replace(".html", "").replace("-", " ").title(),
                    url=url,
                    parent=category_name,
                    level=level,
                )

                yield scrapy.Request(
                    url,
                    callback=self.parse_category,
                    meta={"parent_name": category_name, "level": level + 1},
                )
