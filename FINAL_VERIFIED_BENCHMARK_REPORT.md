# Final Verified Benchmark Report — Laptop Price Prediction Project

> **Artifact File**: `model/saved_model/final_verified_benchmark_report.json`  
> **Status**: Verified & Executed  
> **Primary Architecture**: `LPARA-Stacking (A+ Meta Ensemble)`

---

## 1. Master Benchmark Leaderboard (Sorted by Unseen Model $R^2$)

| Rank | Model Name | 5-Fold CV $R^2$ | Random Split $R^2$ | Random MAE (₹) | Random RMSE (₹) | Random MAPE (%) | **Unseen Model $R^2$** | **Unseen MAE (₹)** | **Unseen RMSE (₹)** | **Unseen MAPE (%)** |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 🥇 | **LPARA-Stacking (A+ Meta Ensemble)** | **0.8143 ±0.035** | **0.8645** | **₹14,514.27** | **₹23,874.54** | **13.21%** | **0.8339** | **₹17,799.85** | **₹29,573.02** | **15.32%** |
| 🥈 | **Stacking Ensemble (Standard)** | 0.8124 ±0.041 | 0.8639 | ₹14,496.22 | ₹23,926.03 | 13.15% | 0.8283 | ₹18,063.63 | ₹30,072.94 | 15.38% |
| 🥉 | **XGBoost Regressor** | 0.8072 ±0.027 | 0.8264 | ₹15,575.02 | ₹27,024.52 | 13.54% | 0.8193 | ₹17,649.63 | ₹30,845.39 | 14.85% |
| 4 | **LPARA-Hybrid (Two-Stage)** | 0.6529 ±0.318 | 0.8711 | ₹14,462.31 | ₹23,282.25 | 13.42% | 0.8176 | ₹18,799.42 | ₹30,990.96 | 15.98% |
| 5 | **Lasso Regression** | 0.5218 ±0.508 | 0.8312 | ₹16,752.98 | ₹26,646.45 | 15.08% | 0.8026 | ₹19,969.97 | ₹32,242.40 | 17.01% |
| 6 | **Standalone LPARA-Ridge** | 0.5768 ±0.414 | 0.8452 | ₹15,862.02 | ₹25,521.35 | 14.56% | 0.7868 | ₹20,597.09 | ₹33,506.23 | 17.27% |
| 7 | **Gradient Boosting** | 0.8208 ±0.039 | 0.8372 | ₹15,304.67 | ₹26,169.42 | 13.60% | 0.7849 | ₹18,145.75 | ₹33,655.58 | 14.76% |
| 8 | **Extra Trees** | 0.7897 ±0.036 | 0.7750 | ₹17,633.12 | ₹30,763.29 | 15.68% | 0.7592 | ₹21,254.75 | ₹35,609.58 | 18.38% |
| 9 | **Ridge Regression (Standard)** | 0.6109 ±0.360 | 0.8473 | ₹15,657.64 | ₹25,343.24 | 14.44% | 0.7490 | ₹21,481.82 | ₹36,358.92 | 17.74% |
| 10 | **Random Forest** | 0.7693 ±0.060 | 0.7926 | ₹16,856.50 | ₹29,540.00 | 14.99% | 0.7240 | ₹21,576.14 | ₹38,126.53 | 17.38% |
| 11 | **Decision Tree** | 0.6313 ±0.148 | 0.6894 | ₹19,773.91 | ₹36,144.79 | 17.76% | 0.6146 | ₹23,991.04 | ₹45,051.03 | 19.79% |

---

## 2. Key Accomplishments & Analytical Validation

1. **Unseen Generalization Champion ($R^2 = 0.8339$)**:
   `LPARA-Stacking (A+ Meta Ensemble)` achieves the highest $R^2$ on unseen laptop lines (**0.8339**), outperforming standard Stacking ($0.8283$) and XGBoost ($0.8193$).
2. **5-Fold Cross-Validation Stability ($0.8143 \pm 0.035$)**:
   By integrating `RobustScaler` and domain-group regularization in the meta blender, cross-validation variance was reduced from $\pm 0.318 \rightarrow \pm 0.035$, addressing the instructor's key concern.
3. **Random Split Accuracy ($R^2 = 0.8645$, MAE = ₹14,514.27)**:
   Maintains top-tier accuracy on random 80/20 test split while delivering maximum generalization.
