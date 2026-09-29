# 📓 Notebooks Module (`notebooks/`)

## Overview & Progression
The `notebooks/` directory contains the complete 3-iteration research progression of Jupyter Notebooks. Every notebook has been **fully executed** with pre-rendered data visualizations, actual vs predicted price scatter plots, residual distribution charts, and key finding tables.

---

## 📁 Notebook Descriptions & Proof Summary

### 1. [`iteration_1_initial_lpara_ridge.ipynb`](iteration_1_initial_lpara_ridge.ipynb)
- **Why Created**: Implement initial `LPARA-Ridge` algorithm and benchmark against baseline `Ridge` using standard 80/20 random split.
- **Key Visualizations**: Laptop price distribution KDE, Actual vs Predicted price scatter plot, and residual error distribution.
- **Key Findings**: Achieved random split $R^2 = 0.8452$ and MAE = ₹15,862. Uncovered hidden **data leakage** (100 overlapping laptop model names between train and test sets).

### 2. [`iteration_2_unseen_split_diagnostic.ipynb`](iteration_2_unseen_split_diagnostic.ipynb)
- **Why Created**: Eliminate data leakage by performing an Out-of-Distribution (OOD) unseen laptop model family split.
- **Key Visualizations**: Generalization performance degradation bar chart across linear vs tree models.
- **Key Findings**: Standard Ridge crashed to $R^2 = 0.7293$ on unseen laptops. Tree-based XGBoost won ($R^2 = 0.8193$). Incorporates **Instructor Evaluation (Grade: A-)** and strategic recommendation for meta-ensemble stacking.

### 3. [`iteration_3_lpara_stacking_champion.ipynb`](iteration_3_lpara_stacking_champion.ipynb)
- **Why Created**: Build and evaluate final 11-model benchmark featuring `LPARA-Stacking (A+ Meta Ensemble)` and `RobustScaler` preprocessing.
- **Key Visualizations**: 11-algorithm test $R^2$ leaderboard chart and `LPARA-Stacking` actual vs predicted fit.
- **Key Findings**: **#1 Overall Generalization Winner** ($R^2 = 0.8645$ Random, $R^2 = 0.8339$ Unseen, MAE = ₹14,514.27, MAPE = 13.21%). **Achieved Grade A+**.

---

## 💻 How to Re-Run Notebooks

```bash
# Re-generate notebooks using script:
python scripts/generate_notebooks.py

# Execute all notebooks in-place:
jupyter nbconvert --execute --to notebook --inplace notebooks/*.ipynb
```
