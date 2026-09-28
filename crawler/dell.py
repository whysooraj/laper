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


class DellCrawler(BaseCrawler):
    """Dell India Laptop Crawler."""

    def __init__(self, delay_min: float = 1.5, delay_max: float = 3.0):
        super().__init__("dell", delay_min=delay_min, delay_max=delay_max)

    def is_laptop_url(self, url: str) -> bool:
        path = urlparse(url).path.lower()
        if "/en-in/shop/laptops" not in path:
            return False
        blocked = ["/accessories", "/monitors", "/deals", "/compare"]
        return not any(b in path for b in blocked)

    def discover_urls(self, max_products: int) -> List[str]:
        print("Discovering Dell India laptop product URLs...")
        discovered = []
        start_urls = [
            "https://www.dell.com/en-in/shop/laptops-2-in-1-pcs/sr/laptops",
            "https://www.dell.com/en-in/shop/gaming-laptops/sr/game-laptops"
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
                print(f"Error fetching Dell URL {start_url}: {e}")
            self.sleep_polite()

        return discovered


if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    crawler = DellCrawler()
    crawler.run(max_products=count)
