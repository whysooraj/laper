import hashlib
import json
import os
import random
import re
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

import requests
from parser import parse_html


BASE_URL = "https://www.asus.com"

START_URLS = [
    "https://www.asus.com/in/laptops/for-gaming/all-series/",
    "https://www.asus.com/in/laptops/for-home/all-series/",
    "https://www.asus.com/in/laptops/for-work/all-series/",
    "https://www.asus.com/in/laptops/for-creators/all-series/",
    "https://www.asus.com/in/laptops/for-students/all-series/"
]

OUTPUT_FILE = "data/asus_laptops.jsonl"
PARSED_FILE = "data/parsed/asus.jsonl"
URLS_FILE = "data/raw/asus_urls.json"
RAW_HTML_DIR = "data/raw/asus"

MAX_PRODUCTS = 100

DELAY_MIN = 1.5
DELAY_MAX = 3.0

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-IN,en;q=0.9",
}

session = requests.Session()
session.headers.update(HEADERS)


import sys

# Configure UTF-8 for console output on Windows
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")


def is_asus_laptop_url(url):
    parsed = urlparse(url)
    if parsed.netloc not in ["www.asus.com", "asus.com"]:
        return False

    path = parsed.path.lower()
    if "/in/laptops/" not in path:
        return False

    # Ignore non-product pages and hubs
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
    for item in blocked:
        if item in path:
            return False

    parts = [x for x in path.split("/") if x]
    # Product pages have at least 5 segments: in / laptops / category / series / product-name
    return len(parts) >= 5


def get_links(url):
    print(f"\nScanning category: {url}")
    try:
        response = session.get(url, timeout=25)
        print(f"HTTP {response.status_code}")
        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        links = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            full_url = urljoin(BASE_URL, href).split("#")[0].split("?")[0]
            if is_asus_laptop_url(full_url):
                links.add(full_url)
        return list(links)
    except Exception as e:
        print(f"ERROR: {e}")
        return []


def discover_sitemap_urls():
    print("\nScanning ASUS India sitemaps for complete catalog...")
    sitemap_links = []
    for i in range(1, 9):
        sm_url = f"https://www.asus.com/in/sitemap/in{i}.xml"
        try:
            r = session.get(sm_url, timeout=20)
            if r.status_code == 200:
                urls = re.findall(r"<loc>(https://www.asus.com/in/laptops/[^<]+)</loc>", r.text)
                for u in urls:
                    u = u.strip().split("#")[0].split("?")[0]
                    if is_asus_laptop_url(u) and u not in sitemap_links:
                        sitemap_links.append(u)
        except Exception as e:
            print(f"Warning fetching {sm_url}: {e}")
    print(f"Discovered {len(sitemap_links)} total candidate URLs from sitemaps.")
    return sitemap_links


def discover_products():
    discovered = []
    visited = set()

    # 1. Scan category pages
    for cat_url in START_URLS:
        if len(discovered) >= MAX_PRODUCTS:
            break
        links = get_links(cat_url)
        for link in links:
            if link not in visited and is_asus_laptop_url(link):
                visited.add(link)
                discovered.append(link)
                print(f"[FOUND {len(discovered)}] {link}")
                if len(discovered) >= MAX_PRODUCTS:
                    break
        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    # 2. If dynamic listing didn't yield enough, draw from sitemaps
    if len(discovered) < MAX_PRODUCTS:
        sitemap_urls = discover_sitemap_urls()
        # Prefer overview and techspec pages
        random.seed(42)
        random.shuffle(sitemap_urls)
        for link in sitemap_urls:
            if link not in visited:
                visited.add(link)
                discovered.append(link)
                print(f"[FOUND {len(discovered)}] {link}")
                if len(discovered) >= MAX_PRODUCTS:
                    break

    # Save discovered URLs
    os.makedirs("data/raw", exist_ok=True)
    with open(URLS_FILE, "w", encoding="utf-8") as f:
        json.dump(discovered, f, indent=2)

    return discovered


def scrape_product(url, index, total):
    print(f"\n[{index}/{total}] Downloading: {url}")
    try:
        response = session.get(url, timeout=30)
        if response.status_code != 200:
            print(f"FAILED HTTP {response.status_code}")
            return None

        html = response.text
        if len(html) < 3000:
            print("FAILED: HTML too small")
            return None

        print(f"HTML: {len(html):,} bytes")

        # Save raw HTML
        os.makedirs(RAW_HTML_DIR, exist_ok=True)
        url_hash = hashlib.md5(url.encode("utf-8")).hexdigest()[:12]
        url_slug = re.sub(r"[^a-zA-Z0-9_-]", "_", urlparse(url).path.strip("/"))[-40:]
        raw_filename = os.path.join(RAW_HTML_DIR, f"{url_slug}_{url_hash}.html")
        with open(raw_filename, "w", encoding="utf-8") as f:
            f.write(html)

        result = parse_html(html, url, "asus")

        if not result.get("brand"):
            result["brand"] = "ASUS"

        print(f"Model: {result.get('model')}")
        print(f"CPU  : {result.get('cpu_brand')} {result.get('cpu_model')}")
        print(f"RAM  : {result.get('ram_gb')} GB {result.get('ram_type')}")
        print(f"SSD  : {result.get('storage_gb')} GB")
        print(f"Price: {result.get('price_current')}")

        return result

    except Exception as e:
        print(f"FAILED: {e}")
        return None


def save_result(result):
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/parsed", exist_ok=True)

    # Save to data/asus_laptops.jsonl
    with open(OUTPUT_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")

    # Save to data/parsed/asus.jsonl
    with open(PARSED_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(result, ensure_ascii=False) + "\n")


def main():
    print("=" * 60)
    print("LPARA ASUS LAPTOP CRAWLER")
    print("=" * 60)
    print(f"Maximum products: {MAX_PRODUCTS}")

    print("\nStep 1: Discovering product URLs...")
    urls = discover_products()
    print(f"\nFound {len(urls)} product URLs.")

    if not urls:
        print("No product URLs found.")
        return

    print("\nStep 2: Scraping products...")

    # Start fresh for validation run
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)
    if os.path.exists(PARSED_FILE):
        os.remove(PARSED_FILE)

    successful = 0
    failed = 0

    for index, url in enumerate(urls, start=1):
        result = scrape_product(url, index, len(urls))
        if result:
            save_result(result)
            successful += 1
            print("STATUS: SAVED")
        else:
            failed += 1
            print("STATUS: SKIPPED")

        time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))

    print("\n" + "=" * 60)
    print("CRAWL COMPLETE")
    print("=" * 60)
    print(f"URLs discovered : {len(urls)}")
    print(f"Successful      : {successful}")
    print(f"Failed          : {failed}")
    print(f"Output          : {OUTPUT_FILE}")
    print(f"Parsed Output   : {PARSED_FILE}")
    print("=" * 60)


if __name__ == "__main__":
    main()