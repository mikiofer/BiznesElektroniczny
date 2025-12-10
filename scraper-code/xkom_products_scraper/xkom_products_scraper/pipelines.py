import os
import json
import re
from urllib.parse import urlparse
from scrapy.pipelines.images import ImagesPipeline
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.utils.python import to_bytes

def sanitize_name_for_folder(name: str) -> str:
    """
    Convert name to lowercase, replace spaces and unsafe chars with hyphens,
    collapse multiple hyphens.
    """
    if not name:
        return "unknown"
    s = name.lower()
    # replace slashes and backslashes with space
    s = re.sub(r"[\\/]+", " ", s)
    # keep alphanum, spaces, hyphens
    s = re.sub(r"[^a-z0-9\s\-ąćęłńóśżź]+", "", s)
    s = re.sub(r"\s+", "-", s).strip("-")
    s = re.sub(r"-{2,}", "-", s)
    return s or "unknown"

class ProductImagesPipeline(ImagesPipeline):
    """
    Custom ImagesPipeline that:
    - downloads images listed in item['image_urls'] (we will only pass up to 2)
    - stores them under IMAGES_STORE/<sanitized-name>/
    - uses filenames: <product_id>_1.jpg, <product_id>_2.jpg
    - sets item['images'] to list of dicts {url, filename}
    """

    def get_media_requests(self, item, info):
        urls = item.get("image_urls") or []
        # limit to first 2
        for idx, url in enumerate(urls[:2], start=1):
            # pass product info to build filename later
            req = Request(url)
            req.meta["product_id"] = item.get("product_id")
            req.meta["product_name"] = item.get("title")
            req.meta["img_index"] = idx
            yield req

    def file_path(self, request, response=None, info=None, *, item=None):
        # Build safe path: <sanitized-name>/<product_id>_<index>.<ext>
        pid = request.meta.get("product_id") or "noid"
        pname = request.meta.get("product_name") or ""
        idx = request.meta.get("img_index") or 1
        sanitized = sanitize_name_for_folder(pname)
        # extension from url
        parsed = urlparse(request.url)
        ext = os.path.splitext(parsed.path)[1] or ".jpg"
        filename = f"{pid}_{idx}{ext}"
        return os.path.join(sanitized, filename)

    def item_completed(self, results, item, info):
        images = []
        for ok, info_dict in results:
            if ok:
                path = info_dict.get("path")
                url = info_dict.get("url")
                images.append({"url": url, "filename": os.path.join(path)})
        # attach to item
        item["images"] = images
        return item

class ProductStorePipeline:
    """
    Collects product items and writes products.json at the end.
    If categories_tree.json exists in the working dir, it will also produce full_tree.json
    by inserting products into leaf categories matching categoryUrl.
    """

    def __init__(self):
        self.products = []

    def process_item(self, item, spider):
        # item is a ProductItem; convert to dict and append
        self.products.append(dict(item))
        return item

    def close_spider(self, spider):
        # write products.json
        with open("products.json", "w", encoding="utf-8") as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)

        # attempt to merge with categories_tree.json if it exists
        if os.path.exists("categories_tree.json"):
            try:
                with open("categories_tree.json", "r", encoding="utf-8") as f:
                    categories = json.load(f)
            except Exception as e:
                spider.logger.error(f"Failed to read categories_tree.json: {e}")
                return

            # build mapping from categoryUrl -> list of products
            mapping = {}
            for p in self.products:
                cat = p.get("categoryUrl")
                if cat:
                    mapping.setdefault(cat, []).append(p)

            def attach_products(node):
                # node is dict with 'url', 'subcategories'
                node_products = mapping.get(node.get("url"), [])
                node["products"] = node_products
                for sub in node.get("subcategories", []):
                    attach_products(sub)

            for root in categories:
                attach_products(root)

            with open("full_tree.json", "w", encoding="utf-8") as f:
                json.dump(categories, f, ensure_ascii=False, indent=2)
