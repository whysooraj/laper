# ⚙️ Processing Module (`processing/`)

## Overview & Purpose
The `processing/` directory contains modular data cleaning, normalization, deduplication, and quality validation components that transform raw scraped HTML/JSON records into zero-null analytical datasets.

---

## 📁 File Structure & Functionalities

| File | Primary Responsibility | How Created | How Used |
| :--- | :--- | :--- | :--- |
| `deduplicate.py` | Composite hardware deduplication engine. Identifies and merges duplicate laptop listings based on brand, CPU, RAM, storage, and display configuration. | Created to eliminate redundant crawler scrapes. | Invoked during `clean_dataset.py` execution pipeline. |
| `normalize.py` | Hardware spec parsing & standardization. Normalizes raw text strings (e.g. "16GB DDR5 4800MHz" $\rightarrow$ `16`, `DDR5`). | Created to extract clean numeric and categorical variables from unstructured text. | Invoked during `clean_dataset.py` execution pipeline. |
| `validate.py` | Data quality sanity checker. Enforces range validation (e.g., price > ₹10,000, RAM $\in [4, 128]$ GB, display $\in [10, 18]$ inches). | Created to catch scraper extraction anomalies and malformed values. | Filters out invalid records into log files. |
| `report.py` | Statistical summary generator. Generates null audits, feature distributions, and cleaning efficiency metrics. | Created to provide automated audit trails of data cleaning steps. | Generates `data/cleaned/cleaning_summary.json`. |

---

## 💻 Usage Example

```bash
# Run full processing pipeline end-to-end:
python clean_dataset.py
```
Outputs clean zero-missing dataset to `data/cleaned/lpara_cleaned_laptop_dataset.csv`.
