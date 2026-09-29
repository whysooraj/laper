# 💻 LPARA: Laptop Price Aggregator & Market Valuation Engine

LPARA is an end-to-end data engineering and machine learning platform that scrapes real-world laptop pricing data, standardizes and cleans hardware specifications into zero-missing datasets, benchmarks competitive regression algorithms, and provides high-precision fair market price predictions.

---

## 📁 Repository Structure

```
lapra/
├── crawler/                # OEM & Retailer Web Crawlers (ASUS, Dell, HP, Lenovo, Retailers)
├── data/                   # Data Storage
│   ├── cleaned/            # Cleaned, zero-null datasets & summaries
│   │   ├── lpara_cleaned_laptop_dataset.csv
│   │   ├── lpara_cleaned_laptop_dataset.jsonl
│   │   └── cleaning_summary.json
│   ├── final/              # Pooled datasets & data quality reports
│   │   ├── laptop_prices_complete_1k.csv
│   │   └── dataset_report.json
│   └── parsed/             # Extracted JSONL records from crawlers
├── model/                  # Production Machine Learning Package
│   ├── saved_model/        # Serialized winning model & telemetry
│   │   ├── best_laptop_price_model.joblib
│   │   ├── model_benchmark_report.json
│   │   └── selected_features.json
│   ├── preprocess.py       # Domain feature engineering & pipeline builder
│   ├── train.py            # 8-algorithm cross-validation & benchmark runner
│   └── predict.py          # Real-time inference engine & CLI predictor
├── notebooks/              # Jupyter & Google Colab Notebooks
│   └── laptop_price_prediction_colab.ipynb
├── processing/             # Modular Data Processing Pipeline
│   ├── deduplicate.py      # Composite hardware configuration deduplication
│   ├── normalize.py        # CPU, GPU, RAM, and Storage standardization
│   ├── validate.py         # Hardware sanity & range checks
│   └── report.py           # Statistical dataset quality auditing
├── scripts/                # Scraper explorations & standalone utilities
│   ├── crawl_asus.py
│   ├── inspect_asus.py
│   ├── find_products.py
│   ├── scraper.py
│   ├── build_dataset.py
│   ├── train_baseline.py
│   └── normalizer.py
├── tests/                  # Unit and integration test suite
│   └── test_parser.py
├── clean_dataset.py        # Automated end-to-end dataset cleaning pipeline
├── parser.py               # HTML specification extraction engine
├── config.py               # Shared global crawler configuration
└── LICENSE
```

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt   # or: pip install scikit-learn xgboost pandas numpy joblib
```

### 2. Clean Raw Dataset (From Scraped Data to Zero-Null Dataset)
```bash
python clean_dataset.py
```
Outputs the standardized dataset to `data/cleaned/lpara_cleaned_laptop_dataset.csv`.

### 3. Train & Benchmark ML Algorithms
```bash
python model/train.py
```
Evaluates 8 regression algorithms across 5-fold cross-validation and holdout test set, saving the winning model to `model/saved_model/best_laptop_price_model.joblib`.

### 4. Predict Laptop Prices via CLI
```bash
# Demo predictions on unseen configurations:
python model/predict.py --demo

# Predict a custom laptop:
python model/predict.py --brand "ASUS" --model "Zenbook 14" --cpu_brand "Intel" --cpu_model "Core Ultra 7 155H" --ram 16 --storage 1024
```

### 5. Run in Google Colab
Open [`notebooks/laptop_price_prediction_colab.ipynb`](notebooks/laptop_price_prediction_colab.ipynb) directly in [Google Colab](https://colab.research.google.com).

---

## 🏆 Machine Learning Leaderboard

Evaluated on 1,292 real-world laptop configurations:

| Rank | Model | CV R² (5-Fold) | Test R² | Test MAE | Test MAPE |
| :---: | :--- | :---: | :---: | :---: | :---: |
| 🥇 **1** | **Stacking Ensemble** | **0.8128 ±0.039** | **0.8643** | **₹14,482** | **13.14%** |
| 🥈 2 | Ridge Regression | 0.6153 ±0.352 | 0.8476 | ₹15,646 | 14.43% |
| 🥉 3 | Gradient Boosting | 0.8206 ±0.039 | 0.8382 | ₹15,270 | 13.60% |
| 4 | Lasso Regression | 0.5567 ±0.441 | 0.8351 | ₹16,634 | 15.03% |
| 5 | XGBoost Regressor | 0.8072 ±0.027 | 0.8264 | ₹15,575 | 13.54% |
| 6 | Random Forest | 0.7712 ±0.059 | 0.7957 | ₹16,820 | 15.01% |
| 7 | Extra Trees | 0.7892 ±0.037 | 0.7747 | ₹17,647 | 15.69% |
| 8 | Decision Tree | 0.6200 ±0.154 | 0.7095 | ₹19,634 | 17.31% |
