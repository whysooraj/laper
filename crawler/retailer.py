import hashlib
import json
import logging
import os
import random
import re
import sys
import time
from typing import Dict, List
from urllib.parse import urljoin

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import requests
from bs4 import BeautifulSoup
from parser import parse_html

logger = logging.getLogger("RetailerCrawler")

RAW_PRICES_DIR = os.path.join("data", "raw", "prices")
PARSED_RETAILER_FILE = os.path.join("data", "parsed", "retailer_laptops.jsonl")


class RetailerCrawler:
    """
    Crawls Indian retailers (Flipkart, store search) for multi-brand laptops.
    Captures live selling prices (price_current), MRP (price_original), discounts,
    and complete hardware specifications.
    """

    def __init__(self, delay_min: float = 1.0, delay_max: float = 2.0):
        self.delay_min = delay_min
        self.delay_max = delay_max
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
        os.makedirs(RAW_PRICES_DIR, exist_ok=True)
        os.makedirs("data/parsed", exist_ok=True)

    def sleep_polite(self):
        time.sleep(random.uniform(self.delay_min, self.delay_max))

    def scrape_query(self, query: str, max_pages: int = 5) -> List[Dict]:
        print(f"\n--- Searching Retailer for: '{query}' (up to {max_pages} pages) ---")
        discovered_records = []
        seen_urls = set()

        for page in range(1, max_pages + 1):
            url = f"https://www.flipkart.com/search?q={query.replace(' ', '+')}&page={page}"
            print(f"Fetching page {page}: {url}")

            try:
                resp = self.session.get(url, timeout=20)
                if resp.status_code != 200:
                    print(f"  HTTP error {resp.status_code}")
                    break

                html = resp.text
                if len(html) < 5000:
                    print("  Payload too small, ending query crawl.")
                    break

                # Save raw HTML in data/raw/prices/
                safe_q = re.sub(r"[^a-zA-Z0-9_-]", "_", query)
                raw_path = os.path.join(RAW_PRICES_DIR, f"{safe_q}_page_{page}.html")
                with open(raw_path, "w", encoding="utf-8") as f:
                    f.write(html)

                soup = BeautifulSoup(html, "lxml")
                product_links = [a for a in soup.find_all("a", href=True) if "/p/" in a["href"]]

                page_records = 0
                for a in product_links:
                    prod_url = urljoin("https://www.flipkart.com", a["href"].split("?")[0])
                    if prod_url in seen_urls:
                        continue
                    seen_urls.add(prod_url)

                    card = a.find_parent("div", class_=lambda c: c and any(k in str(c) for k in ["_75nlfW", "tUxRFH", "_1sdMkc", "cPHDOP", "_1AtVbE"])) or a.parent.parent or a
                    card_html = str(card)
                    card_record = parse_html(card_html, prod_url, "flipkart")

                    # Basic sanity check
                    if card_record.get("model") and (card_record.get("price_current") or card_record.get("ram_gb")):
                        discovered_records.append(card_record)
                        page_records += 1

                print(f"  Page {page}: Scraped {page_records} valid laptop configurations.")

                if page_records == 0:
                    print(f"  Page {page}: No valid records found, proceeding to next page.")

            except Exception as e:
                print(f"  Error on page {page}: {e}")
                break

            self.sleep_polite()

        return discovered_records

    def run(self, queries: List[str] = None, max_pages_per_query: int = 5) -> int:
        if queries is None:
            queries = [
                "asus laptops",
                "lenovo laptops",
                "hp laptops",
                "dell laptops",
                "acer laptops",
                "msi laptops",
                "apple macbook",
                "samsung galaxy book",
                "gaming laptops",
                "intel core i5 laptop",
                "intel core i7 laptop",
                "amd ryzen 5 laptop",
                "amd ryzen 7 laptop",
                "core ultra laptop",
                "rtx 4060 laptop",
                "rtx 4050 laptop"
            ]

        all_records = []
        total_discovered = 0

        for q in queries:
            records = self.scrape_query(q, max_pages=max_pages_per_query)
            for r in records:
                all_records.append(r)
                # Append to parsed retailer file immediately
                with open(PARSED_RETAILER_FILE, "a", encoding="utf-8") as f:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            total_discovered += len(records)
            self.sleep_polite()

        print(f"\n========================================")
        print(f"RETAIL PRICE CRAWL COMPLETE")
        print(f"Total Configurations Scraped: {len(all_records)}")
        print(f"Saved to: {PARSED_RETAILER_FILE}")
        print(f"Raw Pages: {RAW_PRICES_DIR}")
        print(f"========================================\n")
        return len(all_records)


if __name__ == "__main__":
    crawler = RetailerCrawler()
    pages = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    crawler.run(max_pages_per_query=pages)
