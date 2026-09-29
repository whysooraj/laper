# 📜 Scripts Directory (`scripts/`)

## Overview & Purpose
The `scripts/` directory contains standalone utility scripts, scraper exploration tools, dataset building routines, and automated notebook generation utilities.

---

## 📁 File Structure & Script Roles

| File | Description | Why Created | How Used |
| :--- | :--- | :--- | :--- |
| `crawl_asus.py` | Standalone ASUS store scraper wrapper. | Created to test and run dedicated ASUS laptop specification extraction. | Run via: `python scripts/crawl_asus.py`. |
| `inspect_asus.py` | DOM inspection utility for analyzing ASUS product HTML tags. | Created for debugging scraper extraction errors on new ASUS store layouts. | Run via: `python scripts/inspect_asus.py`. |
| `find_products.py` | Product URL discovery tool. Extracts listing page links across OEM websites. | Created to discover all laptop product URLs before deep scraping. | Run via: `python scripts/find_products.py`. |
| `scraper.py` | Generic web scraper utility script. | Created for quick exploratory HTML fetches. | Run via: `python scripts/scraper.py`. |
| `build_dataset.py` | Compiles extracted JSON records into pooled raw dataset. | Created to aggregate multi-source crawl outputs. | Run via: `python scripts/build_dataset.py`. |
| `train_baseline.py` | Quick baseline training runner. | Created for rapid initial validation of baseline linear regression models. | Run via: `python scripts/train_baseline.py`. |
| `generate_notebooks.py` | Automated Jupyter Notebook generator script. | Created to construct and format the 3 standalone iteration notebooks programmatically. | Run via: `python scripts/generate_notebooks.py`. |

---

## 💻 Commands

```bash
# Discover product URLs:
python scripts/find_products.py

# Crawl ASUS listings:
python scripts/crawl_asus.py

# Generate all 3 research notebooks:
python scripts/generate_notebooks.py
```
