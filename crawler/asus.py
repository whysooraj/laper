import re
from typing import List
from urllib.parse import urlparse

from crawler.base_crawler import BaseCrawler


class AsusCrawler(BaseCrawler):
    """ASUS India Laptop Crawler."""

    def __init__(self, delay_min: float = 1.5, delay_max: float = 3.0):
        super().__init__("asus", delay_min=delay_min, delay_max=delay_max)

    def is_laptop_url(self, url: str) -> bool:
        parsed = urlparse(url)
        if parsed.netloc not in ["www.asus.com", "asus.com"]:
            return False

        path = parsed.path.lower()
        if "/in/laptops/" not in path:
            return False

        blocked = [
            "/all-series",
            "/filter",
            "/compare",
            "/search",
            "/support",
            "/review",
            "/helpdesk",
            "/where-to-buy",
            "/accessories"
        ]
        for b in blocked:
            if b in path:
                return False

        parts = [p for p in path.split("/") if p]
        return len(parts) >= 5

    def discover_urls(self, max_products: int) -> List[str]:
        print("Discovering ASUS laptop URLs via Indian sitemaps...")
        discovered = []
        for i in range(1, 9):
            sm_url = f"https://www.asus.com/in/sitemap/in{i}.xml"
            try:
                r = self.session.get(sm_url, timeout=20)
                if r.status_code == 200:
                    urls = re.findall(r"<loc>(https://www.asus.com/in/laptops/[^<]+)</loc>", r.text)
                    for u in urls:
                        u = u.strip().split("#")[0].split("?")[0]
                        if self.is_laptop_url(u) and u not in discovered:
                            discovered.append(u)
                            if len(discovered) >= max_products:
                                return discovered
            except Exception as e:
                print(f"Sitemap notice ({sm_url}): {e}")
        return discovered


if __name__ == "__main__":
    crawler = AsusCrawler()
    crawler.run(max_products=100)
