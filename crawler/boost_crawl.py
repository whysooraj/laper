import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from crawler.retailer import RetailerCrawler

over_1k_queries = [
    "asus vivobook go 14 laptop",
    "lenovo ideapad slim 1 laptop",
    "hp 14s amd ryzen 5 laptop",
    "dell inspiron 15 3511 laptop",
    "acer aspire 3 ryzen 5 laptop",
    "msi thin 15 i7 laptop",
    "apple macbook air m3 16gb",
    "samsung galaxy book 4 16gb",
    "gaming laptop 16gb ram rtx",
    "thin and light laptop 16gb ssd"
]

print(f"Starting final sprint crawl for {len(over_1k_queries)} queries to guarantee >1000 zero-missing records...")
crawler = RetailerCrawler(delay_min=0.6, delay_max=1.0)
crawler.run(queries=over_1k_queries, max_pages_per_query=3)
