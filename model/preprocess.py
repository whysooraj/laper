import re
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.compose import ColumnTransformer
from sklearn.feature_selection import SelectPercentile, f_regression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, RobustScaler

# Core selected features (curated to eliminate target leakage and high-null noise)
SELECTED_NUMERIC_FEATURES = [
    "ram_gb",
    "storage_gb",
    "display_size_inches",
    "ram_storage_ratio",
    "cpu_tier",
    "is_gaming",
    "is_apple"
]

SELECTED_CATEGORICAL_FEATURES = [
    "brand",
    "cpu_brand",
    "cpu_family",
    "ram_type",
    "storage_type",
    "gpu_type",
    "operating_system"
]


def extract_cpu_tier(cpu_model: str, cpu_family: str) -> int:
    """
    Ranks CPU into performance tiers (1: Entry, 2: Budget, 3: Midrange, 4: Performance, 5: Flagship/Pro).
    """
    text = (str(cpu_family or "") + " " + str(cpu_model or "")).lower()
    if any(k in text for k in ["celeron", "pentium", "athlon", "kompanio", "n4020", "n4500"]):
        return 1
    if any(k in text for k in ["core i3", "i3-", "ryzen 3", "core 3"]):
        return 2
    if any(k in text for k in ["core i5", "i5-", "ryzen 5", "core 5", "apple m1", "m1 "]):
        return 3
    if any(k in text for k in ["core i7", "i7-", "ryzen 7", "core 7", "core ultra 5", "apple m2", "apple m3", "snapdragon x"]):
        return 4
    if any(k in text for k in ["core i9", "i9-", "ryzen 9", "core 9", "core ultra 7", "core ultra 9", "m2 max", "m3 max", "m4", "threadripper", "ai max"]):
        return 5
    return 3  # Default median tier


class FeatureEngineeringTransformer(BaseEstimator, TransformerMixin):
    """
    Custom Scikit-Learn transformer that performs feature engineering
    and feature selection on input laptop specifications.
    """

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        df = X.copy()
        if not isinstance(df, pd.DataFrame):
            df = pd.DataFrame(df)

        # 1. Feature Engineering
        model_str = df.get("model", pd.Series([""] * len(df))).astype(str).str.lower()
        brand_str = df.get("brand", pd.Series([""] * len(df))).astype(str)

        # Apple premium flag
        df["is_apple"] = (brand_str == "Apple").astype(int)

        # Gaming laptop flag
        gpu_type_str = df.get("gpu_type", pd.Series(["Integrated"] * len(df))).astype(str)
        is_discrete = (gpu_type_str == "Discrete")
        gaming_kw = model_str.str.contains(
            r"tuf|rog|legion|loq|victus|omen|nitro|predator|katana|cyborg|sword|bravo|alienware|gaming|g15",
            regex=True
        )
        df["is_gaming"] = (is_discrete | gaming_kw).astype(int)

        # CPU performance tier
        cpu_models = df.get("cpu_model", pd.Series([""] * len(df))).astype(str)
        cpu_families = df.get("cpu_family", pd.Series([""] * len(df))).astype(str)
        df["cpu_tier"] = [
            extract_cpu_tier(m, f) for m, f in zip(cpu_models, cpu_families)
        ]

        # RAM to Storage ratio
        ram = pd.to_numeric(df.get("ram_gb", 16), errors="coerce").fillna(16)
        storage = pd.to_numeric(df.get("storage_gb", 512), errors="coerce").fillna(512).replace(0, 512)
        df["ram_storage_ratio"] = ram / storage

        # Fill missing categoricals with 'Unknown' to ensure zero crash on new inputs
        for c in SELECTED_CATEGORICAL_FEATURES:
            if c not in df.columns:
                df[c] = "Unknown"
            else:
                df[c] = df[c].fillna("Unknown").astype(str)

        # Ensure all numeric columns are numeric
        for n in SELECTED_NUMERIC_FEATURES:
            if n not in df.columns:
                df[n] = 0.0
            else:
                df[n] = pd.to_numeric(df[n], errors="coerce").fillna(0.0)

        # Select strictly the curated feature set
        return df[SELECTED_NUMERIC_FEATURES + SELECTED_CATEGORICAL_FEATURES]


def build_preprocessor(percentile_feature_selection: int = 80) -> Pipeline:
    """
    Constructs an end-to-end preprocessing pipeline:
      1. Feature Engineering (engineered indicators, CPU tiering, domain ratios)
      2. ColumnTransformer (Scaling for numerics, OneHotEncoding with unseen handling for categoricals)
      3. Statistical Feature Selection (SelectPercentile with f_regression) to eliminate noisy/sparse one-hot columns
    """
    numeric_pipe = Pipeline([
        ("scaler", RobustScaler())
    ])

    categorical_pipe = Pipeline([
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    col_transformer = ColumnTransformer(
        transformers=[
            ("num", numeric_pipe, SELECTED_NUMERIC_FEATURES),
            ("cat", categorical_pipe, SELECTED_CATEGORICAL_FEATURES)
        ]
    )

    full_pipeline = Pipeline([
        ("feature_engineer", FeatureEngineeringTransformer()),
        ("encoder_scaler", col_transformer),
        ("feature_selector", SelectPercentile(score_func=f_regression, percentile=percentile_feature_selection))
    ])

    return full_pipeline
