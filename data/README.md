# 📊 Data Module (`data/`)

## Overview & Data Lineage
The `data/` directory stores raw scraped records, intermediate validation files, and final clean zero-null datasets used for model training and benchmark evaluation.

---

## 📁 Directory Structure & Data Stages

```
data/
├── cleaned/
│   ├── lpara_cleaned_laptop_dataset.csv   # Primary training dataset (1,292 rows x 20 features)
│   ├── lpara_cleaned_laptop_dataset.jsonl # JSON Lines format of cleaned dataset
│   └── cleaning_summary.json              # Statistical audit summary of cleaning step
├── final/
│   ├── laptop_prices_complete_1k.csv      # Pooled dataset with 1,000+ scraped listings
│   └── dataset_report.json                # Hardware specification distribution report
├── parsed/                                # Raw JSONL outputs directly from web crawlers
└── unseen dataset/
    └── laptop_data.csv                    # Independent unseen holdout dataset for OOD benchmarking
```

---

## 🔬 Dataset Schema & Feature Definition

| Feature Column | Type | Description | Derived / Raw |
| :--- | :---: | :--- | :---: |
| `brand` | Categorical | OEM Manufacturer (ASUS, Dell, HP, Lenovo, Apple, Acer, MSI, etc.) | Raw Scraped |
| `model` | String | Laptop series and model designation | Raw Scraped |
| `price_average` | Numeric (INR ₹) | Target variable: Fair market price average | Raw / Cleaned |
| `price_category` | Categorical | Budget Tier (Entry, Mid-Range, Premium, Ultra-Luxury) | Engineered |
| `cpu_brand` | Categorical | Processor vendor (Intel, AMD, Apple, Qualcomm) | Raw Scraped |
| `cpu_model` | String | Full CPU model string (e.g., Core Ultra 7 155H, Ryzen 7 7840HS) | Raw Scraped |
| `cpu_family` | Categorical | Family grouping (Core i5, Core i7, Core Ultra 7, Ryzen 7, M3) | Engineered |
| `cpu_tier` | Numeric (1-5) | Performance rank (1: Entry, 3: Mid, 5: Flagship) | Engineered |
| `ram_gb` | Numeric | Installed RAM capacity in Gigabytes | Standardized |
| `ram_type` | Categorical | Memory technology (DDR4, DDR5, LPDDR5, LPDDR5X) | Standardized |
| `storage_gb` | Numeric | Solid-State Drive (SSD) capacity in Gigabytes | Standardized |
| `storage_type` | Categorical | Storage interface (SSD, NVMe PCIe 4.0, eMMC) | Standardized |
| `ram_storage_ratio` | Numeric | Feature Interaction: $\text{RAM (GB)} / \text{Storage (GB)}$ | Engineered |
| `display_size_inches` | Numeric | Screen diagonal size in inches | Standardized |
| `gpu_type` | Categorical | Graphics category (Integrated vs Discrete) | Standardized |
| `is_gaming` | Binary (0/1) | Flag indicating gaming laptop model | Engineered |
| `is_apple` | Binary (0/1) | Flag indicating Apple Silicon ecosystem | Engineered |
| `is_touchscreen` | Binary (0/1) | Flag indicating touchscreen support | Standardized |
| `is_oled` | Binary (0/1) | Flag indicating OLED display panel | Standardized |
| `operating_system` | Categorical | OS (Windows 11 Home, macOS, ChromeOS) | Standardized |

---

## 💻 How Data is Generated & Used

1. **Scraping**: Crawlers dump raw JSON records into `data/parsed/`.
2. **Cleaning & Normalization**: Running `python clean_dataset.py` processes raw data through `processing/` modules, outputting `data/cleaned/lpara_cleaned_laptop_dataset.csv`.
3. **Training & Inference**: `model/train.py` reads `data/cleaned/lpara_cleaned_laptop_dataset.csv` for algorithm benchmarking and model training.
