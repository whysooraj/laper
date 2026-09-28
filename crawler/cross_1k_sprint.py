import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from crawler.retailer import RetailerCrawler

cross_1k_queries = [
    "dell latitude laptop",
    "hp probook laptop",
    "lenovo thinkbook laptop",
    "asus expertbook laptop",
    "lg gram laptop",
    "infinix zerobook laptop",
    "honor magicbook laptop",
    "intel core i9 laptop",
    "amd ryzen 9 laptop",
    "rtx 4070 laptop",
    "snapdragon laptop",
    "fujitsu laptop",
    "acer swift go laptop",
    "microsoft surface pro laptop"
]

print(f"Executing sprint crawl on {len(cross_1k_queries)} fresh queries to firmly cross 1,000+ zero-missing laptops...")
crawler = RetailerCrawler(delay_min=0.5, delay_max=0.9)
crawler.run(queries=cross_1k_queries, max_pages_per_query=2)
print("Sprint crawl finished!")
