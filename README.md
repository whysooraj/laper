# 💻 LPARA: Laptop Price Aggregator & Market Valuation Engine

LPARA is an end-to-end data engineering and machine learning platform that scrapes real-world laptop pricing data, standardizes hardware specifications into zero-missing datasets, benchmarks competitive regression algorithms, and provides high-precision fair market price predictions.

---

## 📁 Repository Structure

```
laper/
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
│   ├── lpara_ridge.py      # Custom algorithms: DomainAdaptiveRidge, LPARAHybrid, LPARAStacking
│   ├── saved_model/        # Serialized winning model & telemetry
│   │   ├── best_laptop_price_model.joblib
│   │   ├── model_benchmark_report.json
│   │   └── selected_features.json
│   ├── preprocess.py       # Domain feature engineering & RobustScaler pipeline builder
│   ├── train.py            # 11-algorithm benchmark runner with K-Fold CV
│   └── predict.py          # Real-time inference engine & CLI predictor
├── notebooks/              # Executed 3-Iteration Notebook Suite
│   ├── iteration_1_initial_lpara_ridge.ipynb
│   ├── iteration_2_unseen_split_diagnostic.ipynb
│   └── iteration_3_lpara_stacking_champion.ipynb
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
│   └── generate_notebooks.py
├── tests/                  # Unit and integration test suite
│   └── test_parser.py
├── clean_dataset.py        # Automated end-to-end dataset cleaning pipeline
├── parser.py               # HTML specification extraction engine
├── config.py               # Shared global crawler configuration
├── LAPTOP_PRICE_PREDICTION_RESEARCH_JOURNAL.md # Comprehensive academic research journal
├── FINAL_VERIFIED_BENCHMARK_REPORT.md           # Final verified benchmark documentation
└── LICENSE
```

---

## 🔬 Research & Iterative Progression Notebooks

The project progressed through 3 distinct research iterations to solve **data leakage** and achieve **#1 predictive generalization on unseen laptop models**:

| Iteration | Notebook Link | Focus & Core Discovery | Metric Achievement |
| :---: | :--- | :--- | :---: |
| **Iteration 1** | [`iteration_1_initial_lpara_ridge.ipynb`](notebooks/iteration_1_initial_lpara_ridge.ipynb) | Custom `LPARA-Ridge` baseline on random 80/20 split. Diagnosed 100-model train/test leakage. | Random $R^2 = 0.8452$ |
| **Iteration 2** | [`iteration_2_unseen_split_diagnostic.ipynb`](notebooks/iteration_2_unseen_split_diagnostic.ipynb) | Out-of-Distribution (OOD) Unseen Laptop split. Discovered linear model breakdown & tree superiority. Received **Instructor Grade A-**. | Unseen $R^2 = 0.8193$ (XGBoost) |
| **Iteration 3** | [`iteration_3_lpara_stacking_champion.ipynb`](notebooks/iteration_3_lpara_stacking_champion.ipynb) | `LPARA-Stacking` Meta-Ensemble + `RobustScaler` CV variance elimination. **Winning A+ Architecture**. | **Unseen $R^2 = 0.8339$** / **Random $R^2 = 0.8645$** |

---

## 🏆 Verified Multi-Algorithm Leaderboard

Evaluated on **1,292 real-world laptop configurations** across 11 competitive machine learning algorithms:

| Rank | Algorithm | 5-Fold CV $R^2$ | Random Split $R^2$ | Unseen Laptop $R^2$ | Test MAE (₹) | Test MAPE (%) |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: |
| 🏆 **1** | **LPARA-Stacking (A+ Meta Ensemble)** | **$0.8143 \pm 0.035$** | **0.8645** | **0.8339** | **₹ 14,514.27** | **13.21%** |
| 🥈 2 | **LPARA-Hybrid (Two-Stage)** | $0.6529 \pm 0.318$ | **0.8711** | 0.8094 | ₹ 14,462.31 | 13.42% |
| 🥉 3 | Stacking Ensemble | $0.8124 \pm 0.041$ | 0.8639 | 0.8254 | ₹ 14,496.22 | 13.15% |
| 4 | XGBoost Regressor | $0.8072 \pm 0.027$ | 0.8264 | 0.8193 | ₹ 15,575.02 | 13.54% |
| 5 | Gradient Boosting | $0.8208 \pm 0.039$ | 0.8372 | 0.8105 | ₹ 15,304.67 | 13.60% |
| 6 | LPARA-Ridge (Linear Only) | $0.5768 \pm 0.414$ | 0.8452 | 0.7792 | ₹ 15,862.02 | 14.56% |
| 7 | Ridge Regression | $0.6109 \pm 0.360$ | 0.8473 | 0.7293 | ₹ 15,657.64 | 14.44% |
| 8 | Random Forest | $0.7693 \pm 0.060$ | 0.7926 | 0.7926 | ₹ 16,856.50 | 14.99% |
| 9 | Extra Trees | $0.7897 \pm 0.036$ | 0.7750 | 0.7750 | ₹ 17,633.12 | 15.68% |
| 10 | Lasso Regression | $0.5218 \pm 0.508$ | 0.8312 | 0.7350 | ₹ 16,752.98 | 15.08% |
| 11 | Decision Tree | $0.6313 \pm 0.148$ | 0.6894 | 0.6894 | ₹ 19,773.91 | 17.76% |

---

## 🚀 Quick Start Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt   # or: pip install scikit-learn xgboost pandas numpy joblib matplotlib seaborn
```

### 2. Clean Raw Dataset
```bash
python clean_dataset.py
```
Outputs standardized dataset to `data/cleaned/lpara_cleaned_laptop_dataset.csv`.

### 3. Train & Benchmark ML Algorithms
```bash
python model/train.py
```
Evaluates all 11 algorithms across 5-fold cross-validation and holdout test sets, serializing the winning model pipeline to `model/saved_model/best_laptop_price_model.joblib`.

### 4. Predict Laptop Prices via CLI
```bash
# Demo predictions on sample configurations:
python model/predict.py --demo

# Custom prediction:
python model/predict.py --brand "ASUS" --model "Zenbook 14" --cpu_brand "Intel" --cpu_model "Core Ultra 7 155H" --ram 16 --storage 1024
```

---

## 📖 Documentation & Journal Reports

- **[LAPTOP_PRICE_PREDICTION_RESEARCH_JOURNAL.md](LAPTOP_PRICE_PREDICTION_RESEARCH_JOURNAL.md)**: Academic paper detailing the mathematical formulation of `LPARA-Stacking`, data leakage investigation, error analysis, and viva defense guide.
- **[FINAL_VERIFIED_BENCHMARK_REPORT.md](FINAL_VERIFIED_BENCHMARK_REPORT.md)**: Verified benchmark suite results and production deployment instructions.
