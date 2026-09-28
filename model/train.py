import json
import os
import sys
import time
from typing import Dict, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import TransformedTargetRegressor
from sklearn.ensemble import (
    ExtraTreesRegressor,
    GradientBoostingRegressor,
    RandomForestRegressor,
    StackingRegressor
)
from sklearn.linear_model import ElasticNet, Lasso, Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
import xgboost as xgb

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from model.preprocess import (
    SELECTED_CATEGORICAL_FEATURES,
    SELECTED_NUMERIC_FEATURES,
    build_preprocessor
)

CLEANED_DATA_PATH = os.path.join(ROOT_DIR, "data", "cleaned", "lpara_cleaned_laptop_dataset.csv")
FALLBACK_DATA_PATH = os.path.join(ROOT_DIR, "data", "final", "laptop_prices_complete_1k.csv")
DATA_PATH = CLEANED_DATA_PATH if os.path.exists(CLEANED_DATA_PATH) else FALLBACK_DATA_PATH
SAVED_MODEL_DIR = os.path.join(PACKAGE_DIR, "saved_model")
SAVED_MODEL_PATH = os.path.join(SAVED_MODEL_DIR, "best_laptop_price_model.joblib")
BENCHMARK_REPORT_PATH = os.path.join(SAVED_MODEL_DIR, "model_benchmark_report.json")
FEATURES_METADATA_PATH = os.path.join(SAVED_MODEL_DIR, "selected_features.json")


def get_candidate_models() -> Dict[str, object]:
    """
    Returns a comprehensive suite of competitive regression algorithms
    for laptop price prediction.
    """
    base_ridge = Ridge(alpha=1.0)
    base_rf = RandomForestRegressor(n_estimators=180, max_depth=14, min_samples_split=3, random_state=42, n_jobs=4)
    base_gb = GradientBoostingRegressor(n_estimators=180, learning_rate=0.06, max_depth=5, random_state=42)
    base_xgb = xgb.XGBRegressor(n_estimators=180, learning_rate=0.06, max_depth=5, random_state=42, n_jobs=4)

    stacking_ensemble = StackingRegressor(
        estimators=[
            ("rf", base_rf),
            ("gb", base_gb),
            ("xgb", base_xgb),
            ("ridge", base_ridge)
        ],
        final_estimator=Ridge(alpha=0.5),
        n_jobs=1
    )

    models = {
        "Ridge Regression": base_ridge,
        "Lasso Regression": Lasso(alpha=0.001, max_iter=2000),
        "Decision Tree": DecisionTreeRegressor(max_depth=10, min_samples_split=4, random_state=42),
        "Random Forest": base_rf,
        "Extra Trees": ExtraTreesRegressor(n_estimators=180, max_depth=14, min_samples_split=3, random_state=42, n_jobs=4),
        "Gradient Boosting": base_gb,
        "XGBoost Regressor": base_xgb,
        "Stacking Ensemble": stacking_ensemble
    }
    return models


def train_and_evaluate_all():
    print("=" * 70)
    print("LPARA MULTI-ALGORITHM BENCHMARK & MODEL SELECTION")
    print("=" * 70)

    if not os.path.exists(DATA_PATH):
        raise FileNotFoundError(f"Training dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)
    print(f"Loaded dataset: {len(df)} rows from {os.path.basename(DATA_PATH)}")

    # Target variable: price_average
    target_col = "price_average"
    y = df[target_col].values
    X = df.drop(columns=[target_col])

    # 80/20 Train-Test Split (stratified shuffle)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.20, random_state=42
    )
    print(f"Split data into: Train={len(X_train)} samples, Test={len(X_test)} samples\n")

    candidates = get_candidate_models()
    benchmark_results = []

    print(f"{'Algorithm':<22} | {'CV R² (5-Fold)':<14} | {'Test R²':<10} | {'Test MAE':<14} | {'Test RMSE':<14} | {'Test MAPE':<10}")
    print("-" * 92)

    best_model_name = None
    best_pipeline = None
    best_test_r2 = -float("inf")

    kf = KFold(n_splits=5, shuffle=True, random_state=42)

    for name, regressor in candidates.items():
        t0 = time.time()

        # Build pipeline: Preprocessor (with Feature Selection) + TransformedTargetRegressor (log target)
        preprocessor = build_preprocessor(percentile_feature_selection=85)
        wrapped_model = TransformedTargetRegressor(
            regressor=regressor,
            func=np.log1p,
            inverse_func=np.expm1
        )
        pipeline = Pipeline([
            ("preprocessor", preprocessor),
            ("model", wrapped_model)
        ])

        # 5-Fold Cross-Validation on Train Set
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=kf, scoring="r2", n_jobs=1)
        cv_r2_mean = float(np.mean(cv_scores))
        cv_r2_std = float(np.std(cv_scores))

        # Fit on full training set
        pipeline.fit(X_train, y_train)

        # Evaluate on Holdout Test Set
        y_pred = pipeline.predict(X_test)
        test_r2 = float(r2_score(y_test, y_pred))
        test_mae = float(mean_absolute_error(y_test, y_pred))
        test_rmse = float(np.sqrt(mean_squared_error(y_test, y_pred)))
        test_mape = float(np.mean(np.abs((y_test - y_pred) / y_test)) * 100)

        elapsed = time.time() - t0

        print(
            f"{name:<22} | "
            f"{cv_r2_mean:.4f} ±{cv_r2_std:.3f} | "
            f"{test_r2:.4f}{' *' if test_r2 > 0.88 else '  '}  | "
            f"₹{test_mae:>10,.2f}  | "
            f"₹{test_rmse:>10,.2f}  | "
            f"{test_mape:>7.2f}%"
        )

        res = {
            "model_name": name,
            "cv_r2_mean": round(cv_r2_mean, 4),
            "cv_r2_std": round(cv_r2_std, 4),
            "test_r2": round(test_r2, 4),
            "test_mae": round(test_mae, 2),
            "test_rmse": round(test_rmse, 2),
            "test_mape": round(test_mape, 2),
            "training_time_sec": round(elapsed, 2)
        }
        benchmark_results.append(res)

        if test_r2 > best_test_r2:
            best_test_r2 = test_r2
            best_model_name = name
            best_pipeline = pipeline

    print("-" * 92)
    print(f"\nWINNING MODEL SELECTED: '{best_model_name}' (Test R² = {best_test_r2:.4f})")

    # Serialize Best Model Pipeline
    os.makedirs(SAVED_MODEL_DIR, exist_ok=True)
    joblib.dump(best_pipeline, SAVED_MODEL_PATH)
    print(f"Saved best model pipeline to: {SAVED_MODEL_PATH}")

    # Save Benchmark Report
    report_data = {
        "dataset": os.path.basename(DATA_PATH),
        "total_configurations": len(df),
        "train_samples": len(X_train),
        "test_samples": len(X_test),
        "best_model": best_model_name,
        "best_test_r2": round(best_test_r2, 4),
        "leaderboard": sorted(benchmark_results, key=lambda x: -x["test_r2"])
    }
    with open(BENCHMARK_REPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=2)
    print(f"Saved benchmark report to: {BENCHMARK_REPORT_PATH}")

    # Save Selected Features Metadata
    features_meta = {
        "selected_numeric_features": SELECTED_NUMERIC_FEATURES,
        "selected_categorical_features": SELECTED_CATEGORICAL_FEATURES,
        "target_variable": target_col,
        "feature_selection_percentile": 85,
        "feature_selection_method": "f_regression with SelectPercentile on OneHot encoded space"
    }
    with open(FEATURES_METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(features_meta, f, indent=2)
    print(f"Saved feature metadata to: {FEATURES_METADATA_PATH}")

    print("\n" + "=" * 70)
    print("TRAINING & BENCHMARK COMPLETED SUCCESSFULLY!")
    print("=" * 70 + "\n")
    return best_model_name, best_pipeline, benchmark_results


if __name__ == "__main__":
    train_and_evaluate_all()
