import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import GradientBoostingRegressor, RandomForestRegressor
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

DEFAULT_CSV = "data/final/laptop_prices_complete_1k.csv"
FALLBACK_CSV = "data/final/laptop_prices.csv"


def train_lpara_baseline(csv_path: str = None):
    print("=" * 60)
    print("LPARA MACHINE LEARNING REGRESSION BASELINE")
    print("=" * 60)

    if csv_path is None:
        if len(sys.argv) > 1:
            csv_path = sys.argv[1]
        elif os.path.exists(DEFAULT_CSV):
            csv_path = DEFAULT_CSV
        else:
            csv_path = FALLBACK_CSV

    if not os.path.exists(csv_path):
        print(f"Error: {csv_path} not found.")
        return

    print(f"Loading dataset from: {csv_path}")
    df = pd.read_csv(csv_path)
    print(f"Total dataset configurations: {len(df)}")

    # 1. Split Labeled (Priced) vs Unlabeled (Unpriced)
    # Regression target is 'price_average' (with fallback to 'price_current')
    target_col = "price_average"
    df[target_col] = df[target_col].fillna(df["price_current"])

    labeled_df = df[df[target_col].notna() & (df[target_col] >= 10000)].copy()
    unlabeled_df = df[df[target_col].isna() | (df[target_col] < 10000)].copy()

    print(f"Labeled training rows (with verified retail price): {len(labeled_df)}")
    print(f"Unlabeled rows (for market valuation inference):   {len(unlabeled_df)}")

    # 2. Select Features for Regression (No target leakage: strictly hardware & physical specs)
    numeric_features = [
        "ram_gb",
        "storage_gb",
        "display_size_inches",
        "refresh_rate_hz",
        "weight_kg",
        "battery_wh"
    ]
    categorical_features = [
        "brand",
        "series",
        "cpu_brand",
        "cpu_model",
        "ram_type",
        "storage_type",
        "operating_system"
    ]

    # Keep only features present in df
    num_cols = [c for c in numeric_features if c in df.columns]
    cat_cols = [c for c in categorical_features if c in df.columns]

    X = labeled_df[num_cols + cat_cols]
    y = labeled_df[target_col]

    # 3. Train-Test Split (80% Train, 20% Out-of-Sample Test)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"\nTraining set size:   {len(X_train)} samples")
    print(f"Test set size:       {len(X_test)} samples")

    # 4. Preprocessing Pipeline
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="Unknown")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, num_cols),
            ("cat", categorical_transformer, cat_cols)
        ]
    )

    # 5. Model Benchmarking: Random Forest & Gradient Boosting
    models = {
        "Random Forest Regressor": RandomForestRegressor(n_estimators=150, random_state=42, max_depth=12),
        "Gradient Boosting Regressor": GradientBoostingRegressor(n_estimators=150, random_state=42, learning_rate=0.08)
    }

    best_model_name = None
    best_pipe = None
    best_r2 = -float("inf")

    print("\n--- MODEL EVALUATION (Test Set: 20%) ---")
    for name, model in models.items():
        pipe = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("regressor", model)
        ])
        pipe.fit(X_train, y_train)
        y_pred = pipe.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        r2 = r2_score(y_test, y_pred)

        print(f"\nModel: {name}")
        print(f"  R² Score:  {r2:.4f}")
        print(f"  MAE:       ₹{mae:,.2f}")
        print(f"  RMSE:      ₹{rmse:,.2f}")

        if r2 > best_r2:
            best_r2 = r2
            best_model_name = name
            best_pipe = pipe

    print(f"\n>>> Best Model: {best_model_name} (R² = {best_r2:.4f})")

    # 6. Sample Actual vs Predicted on Test Set
    y_test_pred = best_pipe.predict(X_test)
    sample_eval = X_test.copy()
    sample_eval["Actual_Price"] = y_test
    sample_eval["Predicted_Price"] = np.round(y_test_pred, 2)
    sample_eval["Difference"] = sample_eval["Predicted_Price"] - sample_eval["Actual_Price"]
    sample_eval["Error_%"] = np.round(np.abs(sample_eval["Difference"]) / sample_eval["Actual_Price"] * 100, 1)

    print("\n--- SAMPLE TEST SET PREDICTIONS (First 5 laptops) ---")
    cols_to_show = ["brand", "cpu_model", "ram_gb", "storage_gb", "Actual_Price", "Predicted_Price", "Error_%"]
    available_cols = [c for c in cols_to_show if c in sample_eval.columns]
    print(sample_eval[available_cols].head(5).to_string(index=False))

    # 7. Unlabeled Inference: Predict Fair Market Prices for OEM/Unpriced Models
    if len(unlabeled_df) > 0:
        X_unlabeled = unlabeled_df[num_cols + cat_cols]
        unlabeled_preds = best_pipe.predict(X_unlabeled)
        unlabeled_df["predicted_fair_price"] = np.round(unlabeled_preds, 2)

        print(f"\n--- SAMPLE FAIR MARKET VALUATION PREDICTIONS (Unpriced OEM Models) ---")
        pred_cols = ["brand", "model", "cpu_model", "ram_gb", "storage_gb", "predicted_fair_price"]
        avail_pred_cols = [c for c in pred_cols if c in unlabeled_df.columns]
        print(unlabeled_df[avail_pred_cols].head(5).to_string(index=False))

    print("\n" + "=" * 60)
    print("BASELINE ML TRAINING COMPLETED SUCCESSFULLY!")
    print("=" * 60)


if __name__ == "__main__":
    train_lpara_baseline()
