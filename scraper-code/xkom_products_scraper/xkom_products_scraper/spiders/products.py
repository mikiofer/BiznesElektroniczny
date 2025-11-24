import scrapy
import json
import re
from urllib.parse import urljoin, urlparse, parse_qs
from xkom_products_scraper.items import ProductItem
from scrapy.utils.project import get_project_settings
from w3lib.html import remove_tags

def find_product_id_from_url(url):
    # example: /p/1349345-...html
    m = re.search(r"/p/(\d+)-", url)
    if m:
        return m.group(1)
    # fallback: search last number in url
    m2 = re.search(r"/p/(\d+)\.html", url)
    if m2:
        return m2.group(1)
    return None

def merge_html_blocks(sel_list):
    # sel_list: list of selectors or raw html snippets; join and return html string
    return "\n".join([s.get() if hasattr(s, "get") else str(s) for s in sel_list if s])

def extract_price(response):
    """
    Price extraction per your description:
    - inside div[data-name="productPrice"] find spans with class containing parts__Price,
      parts__DecimalPrice, parts__Currency (they may be separate).
    We'll try a few fallbacks and return a single joined string like "1 234,56 zł".
    """
    base = response.css('div[data-name="productPrice"]')
    if not base:
        return None
    # try full price span
    price_whole = base.css('span[class*="parts__Price"]::text').get()
    price_decimal = base.css('span[class*="parts__DecimalPrice"]::text').get()
    price_currency = base.css('span[class*="parts__Currency"]::text').get()
    # sometimes the price is in a single element
    if not price_whole:
        combined = base.css('span::text').getall()
        combined = [x.strip() for x in combined if x.strip()]
        if combined:
            return " ".join(combined)
        return None

    price = price_whole.strip()
    if price_decimal:
        price = price + (price_decimal.strip())
    if price_currency:
        price = price + " " + price_currency.strip()
    return price

class ProductsSpider(scrapy.Spider):
    name = "products"
    allowed_domains = ["x-kom.pl"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        settings = get_project_settings()
        self.max_global = settings.getint("MAX_PRODUCTS_GLOBAL", 1000)
        self.max_per_cat = settings.getint("MAX_PRODUCTS_PER_CATEGORY", 50)
        self.global_count = 0

        # load category tree produced by category spider
        # assumes categories_tree.json exists in working directory
        try:
            with open("categories_tree.json", "r", encoding="utf-8") as f:
                self.categories = json.load(f)
        except FileNotFoundError:
            self.logger.error("categories_tree.json not found. Please run category scraper first.")
            self.categories = []

    def start_requests(self):
        # iterate over category nodes and yield requests only for leaf categories (or categories with /c/ in URL)
        for url in self.iter_category_urls(self.categories):
            # only categories that appear to be product categories, e.g. '/c/' in url
            yield scrapy.Request(url, callback=self.parse_listing, meta={"cat_url": url, "count": 0})

    def iter_category_urls(self, nodes):
        for node in nodes:
            url = node.get("url")
            # yield this node if it's a product category (contains /c/) else still descend
            if url and "/c/" in url:
                yield url
            for sub in node.get("subcategories", []):
                yield from self.iter_category_urls([sub])

    def parse_listing(self, response):
        # stop if global limit reached
        if self.global_count >= self.max_global:
            return

        cat_url = response.meta.get("cat_url")
        count = response.meta.get("count", 0)

        # find product links: use robust selector - links to /p/
        product_hrefs = response.css("a[href*='/p/']::attr(href)").getall()
        # dedupe preserving order
        seen = set()
        product_hrefs = [h for h in product_hrefs if not (h in seen or seen.add(h))]

        for href in product_hrefs:
            if count >= self.max_per_cat or self.global_count >= self.max_global:
                break
            product_url = urljoin(response.url, href)
            self.global_count += 1
            count += 1
            yield scrapy.Request(product_url, callback=self.parse_product, meta={"categoryUrl": cat_url})

        # pagination: x-kom uses ?page=... or rel="next" possibly
        if count < self.max_per_cat and self.global_count < self.max_global:
            # try rel=next
            next_span = response.css('span[class*="parts__Next"]')
            if next_span:
                parent_a = next_span.xpath('ancestor::a[1]/@href').get()
                if parent_a:
                    yield response.follow(parent_a, callback=self.parse_listing, meta={"cat_url": cat_url, "cat_count": cat_count})
                    return
            # fallback: try to detect current page and increment page param
            parsed = urlparse(response.url)
            qs = parse_qs(parsed.query)
            page = int(qs.get("page", ["1"])[0])
            next_page = page + 1
            # construct next url
            base = response.url.split("?")[0]
            next_url = f"{base}?page={next_page}"
            # verify that next page link exists by checking for a pagination next button
            if response.css("a.pagination__next") or response.css("a[aria-label*='następna'], a[aria-label*='dalej']"):
                yield scrapy.Request(next_url, callback=self.parse_listing, meta={"cat_url": cat_url, "count": count})

    def parse_product(self, response):
        item = ProductItem()
        item["url"] = response.url
        pid = find_product_id_from_url(response.url) or ""
        item["product_id"] = pid

        # title
        title = response.css('h1[data-name="productTitle"]::text').get()
        if not title:
            title = response.css("h1::text").get()
        if title:
            title = title.strip()
        item["title"] = title

        # category fields: get meta categoryUrl and try to get a readable name from page breadcrumbs
        cat_url = response.meta.get("categoryUrl")
        item["categoryUrl"] = cat_url
        # breadcrumbs: try to extract last breadcrumb element as category name
        breadcrumb_name = response.css('ul.breadcrumbs li a::text').getall()
        if not breadcrumb_name:
            breadcrumb_name = response.css('ul.sc-15ih3hi-1 li::text').getall()
        cat_name = None
        if breadcrumb_name:
            # last non-empty text
            cat_name = next((t.strip() for t in reversed(breadcrumb_name) if t.strip()), None)
        item["categoryName"] = cat_name

        # description HTML: gather content block(s)
        # primary selector: div.content (may be multiple)
        desc_blocks = response.css("div.content")
        # fallback: any block with data-name containing description
        if not desc_blocks:
            desc_blocks = response.css('div[data-name*="productDescription"], div[data-name*="description"]')
        description_html = ""
        if desc_blocks:
            description_html = "\n".join([b.get() for b in desc_blocks])
        item["descriptionHtml"] = description_html

        # descriptionText: plain text from description_html
        description_text = remove_tags(description_html or "")
        description_text = re.sub(r'\s+', ' ', description_text).strip()
        item["descriptionText"] = description_text

        # price
        item["price"] = extract_price(response)

        # specs - structured table under data-name="productSpecification" or table-like structures
        specs = {}
        spec_block = response.css('div[data-name="productSpecification"], section[data-name="productSpecification"]')
        if spec_block:
            # rows: many x-kom pages use <tr><th>Key</th><td>Value</td></tr>
            rows = spec_block.css("tr")
            if rows:
                for r in rows:
                    key = r.css("th::text").get() or r.css("td:nth-child(1)::text").get()
                    val = r.css("td::text").get()
                    if not val:
                        # sometimes value in span or div
                        val = r.css("td *::text").getall()
                        if val:
                            val = " ".join([v.strip() for v in val if v.strip()])
                        else:
                            val = None
                    if key:
                        key = key.strip()
                        specs[key] = val.strip() if isinstance(val, str) else val
            else:
                # fallback: key/value pairs in <div class="spec-row"> or dl/dt/dd
                rows2 = spec_block.css("div.sc-spec-row, dl")
                if rows2:
                    # handle dl
                    keys = spec_block.css("dt::text").getall()
                    vals = spec_block.css("dd::text").getall()
                    for k, v in zip(keys, vals):
                        if k:
                            specs[k.strip()] = v.strip() if v else None
        item["specs"] = specs

        # attributes: find groups with class containing parts__ModifierGroup
        attributes = []
        groups = response.xpath('//*[contains(@class,"parts__ModifierGroup")]')
        for g in groups:
            name = g.xpath('.//span[contains(@class,"parts__GroupTitle")]/text()').get()
            if not name:
                # fallback - first span text
                name = g.xpath('.//span/text()').get()
            name = name.strip() if name else None

            options = []
            default_value = None
            opt_nodes = g.xpath('.//*[contains(@class,"parts__ModifierButton") or contains(@class,"parts__ProductLink") or name(@*)]')
            # better: select direct buttons / anchors inside group
            opt_nodes = g.xpath('.//a[contains(@class,"parts__ModifierButton") or contains(@class,"parts__ProductLink")] | .//div[contains(@class,"parts__ModifierButton")] | .//button[contains(@class,"parts__ModifierButton")]')
            for opt in opt_nodes:
                val = opt.xpath('./@title').get()
                if not val:
                    # maybe text child
                    val = opt.xpath('.//*[contains(@class,"parts__Title")]/text()').get()
                if val:
                    val = val.strip()
                priceDiff = opt.xpath('.//span[contains(@class,"parts__Price")]/text()').get()
                if priceDiff:
                    priceDiff = priceDiff.strip()
                url = opt.xpath('./@href').get()
                # default determination
                classes = opt.xpath('./@class').get() or ""
                if "parts__CurrentProductFeature" in classes or "CurrentProductFeature" in classes:
                    default_value = val
                options.append({"value": val, "priceDiff": priceDiff, "url": url})

            if name or options:
                attributes.append({
                    "name": name,
                    "options": options,
                    "default": default_value
                })

        item["attributes"] = attributes

        # images: select first two images with data-cy="thumbnail_img" and transform url
        thumb_urls = response.css('img[data-cy="thumbnail_img"]::attr(src)').getall()
        # fallback: other imgs in gallery
        if not thumb_urls:
            thumb_urls = response.css('img::attr(src)').getall()
        # transform urls to product-new-big if needed
        final_urls = []
        for u in thumb_urls:
            if not u:
                continue
            # ensure absolute url
            u = urljoin(response.url, u)
            # replace product-small -> product-new-big if present
            u2 = u.replace("product-small", "product-new-big")
            final_urls.append(u2)
        # only keep first two
        final_urls = final_urls[:2]
        item["image_urls"] = final_urls

        yield item
