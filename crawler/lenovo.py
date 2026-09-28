import os
import re
import sys
from typing import List
from urllib.parse import urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from crawler.base_crawler import BaseCrawler


class LenovoCrawler(BaseCrawler):
    """Lenovo India Laptop Crawler."""

    def __init__(self, delay_min: float = 1.0, delay_max: float = 2.5):
        super().__init__("lenovo", delay_min=delay_min, delay_max=delay_max)

    def is_laptop_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc not in ["www.lenovo.com", "lenovo.com"]:
            return False

        path = parsed.path.lower()
        if "/in/en/p/laptops/" not in path:
            return False

        # Exclude accessories and categories
        blocked = ["/accessory/", "/accessories/", "/cart", "/search"]
        for b in blocked:
            if b in path:
                return False

        return True

    def discover_urls(self, max_products: int) -> List[str]:
        print("Discovering Lenovo India product URLs from sitemap...")
        sitemap_url = "https://www.lenovo.com/sitemap-auto/037-intsitemap-in-en.xml"
        discovered = []
        try:
            resp = self.session.get(sitemap_url, timeout=25)
            if resp.status_code == 200:
                urls = re.findall(r"<loc>(https://www.lenovo.com/in/en/p/laptops/[^<]+)</loc>", resp.text)
                for u in urls:
                    u = u.strip().split("?")[0]
                    if self.is_laptop_url(u) and u not in discovered:
                        discovered.append(u)
                        if len(discovered) >= max_products:
                            break
        except Exception as e:
            print(f"Error fetching Lenovo sitemap: {e}")

        return discovered


if __name__ == "__main__":
    import sys
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 50
    crawler = LenovoCrawler()
    crawler.run(max_products=count)
