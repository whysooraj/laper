# 🌐 URLs Directory (`urls/`)

## Overview & Purpose
The `urls/` directory contains target web link lists and seed seed-files used by web crawlers to discover and extract laptop product specifications across OEM store domains.

---

## 📁 File Breakdown & Role

| File | Content & Purpose | How Created | How Used |
| :--- | :--- | :--- | :--- |
| `laptops.txt` | Target seed URLs for laptop product store pages (e.g. ASUS TUF, ROG, Zenbook listings). | Generated during URL discovery stage (`scripts/find_products.py`). | Read line-by-line by crawlers (`crawler/crawl_asus.py`, `crawler/base_crawler.py`) for HTTP scraping. |

---

## 💻 How Used by Crawlers

Crawlers parse `urls/laptops.txt` to populate the async crawling queue, ensuring targeted fetching of product specification pages.
