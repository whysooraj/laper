import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from crawler.retailer import RetailerCrawler

target_queries = [
    # ASUS Series
    "asus vivobook 15",
    "asus vivobook 14",
    "asus vivobook 16",
    "asus zenbook 14 oled",
    "asus tuf f15",
    "asus tuf a15",
    "asus rog zephyrus",
    
    # Lenovo Series
    "lenovo ideapad slim 3",
    "lenovo ideapad slim 5",
    "lenovo thinkpad e14",
    "lenovo thinkpad e16",
    "lenovo yoga 7",
    "lenovo loq i5",
    "lenovo loq ryzen",
    "lenovo legion 5",

    # HP Series
    "hp 15s i5",
    "hp 15s ryzen",
    "hp 14s i3",
    "hp pavilion 15",
    "hp pavilion plus",
    "hp victus i5",
    "hp victus ryzen",
    "hp omen 16",

    # Acer Series
    "acer aspire lite",
    "acer aspire 5",
    "acer aspire 7",
    "acer nitro v",
    "acer predator helios 16",
    "acer swift go 14",

    # Dell Series
    "dell inspiron 3520",
    "dell inspiron 3530",
    "dell inspiron 5430",
    "dell vostro 3520",
    "dell g15 gaming",

    # MSI & Samsung & Apple
    "msi thin a15",
    "msi bravo 15",
    "msi katana a15",
    "msi modern 14",
    "samsung galaxy book 4",
    "samsung galaxy book 4 pro",
    "apple macbook air m2",
    "apple macbook air m3",
    "apple macbook pro m3",

    # Feature / Specs Queries
    "16gb ram 512gb ssd laptop",
    "16gb ram 1tb ssd laptop",
    "rtx 4060 laptop",
    "intel core ultra 7 laptop",
    "amd ryzen 7 7730u laptop",
    "touch screen 2 in 1 laptop"
]

print(f"Starting scaled crawl across {len(target_queries)} specific laptop queries to reach 1000+ complete configurations...")
crawler = RetailerCrawler(delay_min=0.8, delay_max=1.5)
crawler.run(queries=target_queries, max_pages_per_query=3)
