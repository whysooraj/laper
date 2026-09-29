# 🤖 Machine Learning Package (`model/`)

## Overview & Purpose
The `model/` directory houses the core machine learning algorithms, preprocessing pipelines, training suites, and inference engines for predicting laptop prices.

---

## 📁 File Structure & Core Responsibilities

| File | Role | Why Created | How Used |
| :--- | :--- | :--- | :--- |
| `lpara_ridge.py` | Custom machine learning algorithms (`DomainAdaptiveRidgeRegressor`, `LPARAHybridRegressor`, `LPARAStackingRegressor`). | Hand-crafted to address hardware domain interaction and multi-model meta-stacking. | Imported by `train.py` and `predict.py`. |
| `preprocess.py` | Feature engineering & `build_preprocessor()` pipeline builder utilizing `RobustScaler` and `OneHotEncoder`. | Created to standardize input features and eliminate outlier leverage in CV splits. | Called during model training and inference. |
| `train.py` | 11-algorithm benchmark runner with 5-fold cross-validation and hyperparameter selection. | Created to evaluate models across random and unseen splits, selecting the #1 performer. | Run directly: `python model/train.py`. |
| `predict.py` | Command-Line Interface (CLI) & Python API for real-time price inference. | Created to provide instant valuation estimates for new/custom laptop specs. | Run directly: `python model/predict.py --demo`. |
| `saved_model/` | Serialized model artifacts (`best_laptop_price_model.joblib`), benchmark JSON report, and feature metadata. | Created to store trained pipeline state for instant zero-latency inference. | Loaded automatically by `predict.py`. |

---

## 🧠 Custom Algorithm Architectures

1. **`DomainAdaptiveRidgeRegressor`**: Regularized linear model with domain-specific penalty weights for RAM/Storage hardware ratios, brand equity multiplier, and market tiering.
2. **`LPARAHybridRegressor`**: Two-stage residual learning model where Ridge fits baseline linear price growth, and XGBoost models residual non-linear gaming/luxury spikes.
3. **`LPARAStackingRegressor` (🏆 #1 Champion)**: Meta-ensemble architecture stacking Ridge, XGBoost, ExtraTrees, and GradientBoosting base learners into a domain-adaptive meta-blender.

---

## 💻 Commands & Usage

```bash
# Train & Benchmark 11 ML Models:
python model/train.py

# Predict Price for Custom Laptop Specs:
python model/predict.py --brand "ASUS" --model "ROG Strix" --cpu_brand "Intel" --cpu_model "Core i9-14900HX" --ram 32 --storage 2048
```
