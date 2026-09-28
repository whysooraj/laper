import abc
import hashlib
import json
import logging
import os
import random
import re
import time
from typing import Dict, List, Optional
import sys
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

# Configure console encoding for Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from urllib.parse import urlparse
import requests
from parser import parse_html

# Set up logging
os.makedirs("logs", exist_ok=True)
logging.basicConfig(
    filename="logs/crawler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("BaseCrawler")


class BaseCrawler(abc.ABC):
    """
    Base crawler for brand-specific laptop data gathering.
    Manages session pooling, polite rate limiting, raw HTML storage,
    failed URL tracking, and uniform output schemas.
    """

    def __init__(
        self,
        brand_name: str,
        delay_min: float = 1.5,
        delay_max: float = 3.0,
        timeout: int = 30
    ):
        self.brand_name = brand_name.lower()
        self.delay_min = delay_min
        self.delay_max = delay_max
        self.timeout = timeout

        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
            "Accept-Language": "en-IN,en;q=0.9",
        })

        self.raw_dir = os.path.join("data", "raw", self.brand_name)
        self.parsed_file = os.path.join("data", "parsed", f"{self.brand_name}.jsonl")
        self.urls_file = os.path.join("data", "raw", f"{self.brand_name}_urls.json")
        self.failed_file = os.path.join("logs", f"{self.brand_name}_failed_urls.jsonl")

        os.makedirs(self.raw_dir, exist_ok=True)
        os.makedirs("data/parsed", exist_ok=True)
        os.makedirs("logs", exist_ok=True)

    @abc.abstractmethod
    def discover_urls(self, max_products: int) -> List[str]:
        """Discover product URLs for this brand up to max_products."""
        pass

    def sleep_polite(self):
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def save_raw_html(self, url: str, html: str) -> str:
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
        url_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", urlparse(url).path.strip("/"))[-40:]
        filename = os.path.join(self.raw_dir, f"{url_slug}_{url_hash}.html")
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html)
        return filename

    def log_failed_url(self, url: str, reason: str):
        record = {
            "brand": self.brand_name,
            "url": url,
            "reason": reason,
            "timestamp": time.time()
        }
        with open(self.failed_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record) + "\n")
        logger.warning(f"Failed URL [{self.brand_name}]: {url} - {reason}")

    def save_parsed_record(self, record: Dict):
        with open(self.parsed_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def scrape_url(self, url: str, index: int, total: int) -> Optional[Dict]:
        print(f"[{index}/{total}] Scraping {self.brand_name.upper()}: {url}")
        try:
            resp = self.session.get(url, timeout=self.timeout)
            if resp.status_code != 200:
                self.log_failed_url(url, f"HTTP {resp.status_code}")
                return None

            html = resp.text
            if len(html) < 2000:
                self.log_failed_url(url, "HTML payload too small")
                return None

            # Archive raw HTML
            self.save_raw_html(url, html)

            # Parse with central parser
            record = parse_html(html, url, self.brand_name)
            if not record.get("brand"):
                record["brand"] = self.brand_name.upper()

            return record

        except Exception as e:
            self.log_failed_url(url, str(e))
            return None

    def run(self, max_products: int = 50) -> int:
        print(f"=== Starting {self.brand_name.upper()} Crawl (Target: {max_products}) ===")
        urls = self.discover_urls(max_products)
        print(f"Discovered {len(urls)} unique URLs.")

        # Save discovered URLs
        with open(self.urls_file, "w", encoding="utf-8") as f:
            json.dump(urls, f, indent=2)

        # Clear previous parsed file for fresh run
        if os.path.exists(self.parsed_file):
            os.remove(self.parsed_file)

        saved_count = 0
        for i, url in enumerate(urls, start=1):
            record = self.scrape_url(url, i, len(urls))
            if record and record.get("model"):
                self.save_parsed_record(record)
                saved_count += 1
                print(f"  -> Saved: {record.get('model')} (Price: {record.get('price_current')})")
            else:
                print(f"  -> Skipped: {url}")
            self.sleep_polite()

        print(f"=== Completed {self.brand_name.upper()} Crawl. Saved {saved_count}/{len(urls)} records. ===")
        return saved_count
