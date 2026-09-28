import os
import re
import sys
from typing import List
from urllib.parse import urljoin, urlparse

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from crawler.base_crawler import BaseCrawler
from bs4 import BeautifulSoup


class HpCrawler(BaseCrawler):
    """HP India Laptop Crawler."""

    def __init__(self, delay_min: float = 1.5, delay_max: float = 3.0):
        super().__init__("hp", delay_min=delay_min, delay_max=delay_max)

    def is_laptop_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        if "/laptops" not in path and "/product/" not in path:
            return False
        blocked = ["/accessories", "/printers", "/ink-toner", "/support", "/drivers"]
        return not any(b in path for b in blocked)

    def discover_urls(self, max_products: int) -> List[str]:
        print("Discovering HP India laptop product URLs...")
        discovered = []
        start_urls = [
            "https://www.hp.com/in-en/shop/laptops-tablets.html",
            "https://www.hp.com/in-en/shop/laptops-tablets/personal-laptops.html",
            "https://www.hp.com/in-en/shop/laptops-tablets/gaming-laptops.html"
        ]
        for start_url in start_urls:
            if len(discovered) >= max_products:
                break
            try:
                resp = self.session.get(start_url, timeout=20)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml")
                    for a in soup.find_all("a", href=True):
                        full_url = urljoin(start_url, a["href"]).split("?")[0]
                        if self.is_laptop_url(full_url) and full_url not in discovered:
                            discovered.append(full_url)
                            if len(discovered) >= max_products:
                                break
            except Exception as e:
                print(f"Error fetching HP URL {start_url}: {e}")
            self.sleep_polite()

        return discovered


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    crawler = HpCrawler()
    crawler.run(max_products=count)
