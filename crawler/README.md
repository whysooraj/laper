# 🕷️ Crawler Module (`crawler/`)

## Overview & Purpose
The `crawler/` directory contains modular web scraping components designed to extract structured laptop specifications and pricing data from OEM manufacturer sites (ASUS, Dell, HP, Lenovo) and e-commerce retailers.

---

## 📁 File Structure & Component Roles

| File | Purpose | How Created | How Used |
| :--- | :--- | :--- | :--- |
| `base_crawler.py` | Abstract Base Class defining HTTP session handling, rate-limiting, proxy rotation, and retry logic. | Hand-crafted OOP base module. | Inherited by OEM-specific crawlers (`asus.py`, `dell.py`, `hp.py`, `lenovo.py`). |
| `asus.py` | Scrapes ASUS store pages for ROG, TUF, Zenbook, and Vivobook specifications. | Custom parser targeting ASUS DOM structures. | Invoked via `python scripts/crawl_asus.py`. |
| `dell.py` | Scrapes Dell laptop product listings (XPS, Inspiron, Alienware). | Custom BeautifulSoup/Playwright parser. | Executed during data collection phase. |
| `hp.py` | Scrapes HP laptop listings (Spectre, Envy, Omen, Victus, Pavilion). | Target DOM parser for HP Store APIs. | Executed during data collection phase. |
| `lenovo.py` | Scrapes Lenovo store listings (ThinkPad, Legion, LOQ, Yoga, IdeaPad). | Custom JSON-LD & DOM extractor. | Executed during data collection phase. |
| `retailer.py` | Scrapes multi-brand e-commerce retailers for cross-validation pricing. | Generic multi-store DOM scraper. | Gathers independent market prices for normalization. |
| `boost_crawl.py` | Multi-threaded async scheduler for parallel URL processing. | Asyncio worker pool wrapper. | Accelerates bulk crawling runs. |
| `cross_1k_sprint.py` | Sprint runner targeting 1,000+ raw laptop listings. | Batch execution script. | Populates `data/parsed/` JSONL records. |
| `scale_1k_crawl.py` | Scaled crawling utility with proxy failover and checkpointing. | Fault-tolerant crawler wrapper. | Ensures zero data loss during long crawl sessions. |

---

## 💻 Usage Example

```bash
# Run ASUS crawler sprint:
python scripts/crawl_asus.py

# Run bulk scaled crawler:
python crawler/scale_1k_crawl.py
```
Outputs raw extracted records into `data/parsed/`.
