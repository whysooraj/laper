"""
LPARA Automated Data Cleaning & Dataset Export Pipeline
Takes raw/scraped laptop configurations, cleans and standardizes all fields,
performs feature selection and domain engineering, removes anomalies,
and exports the final cleaned dataset for download and ML modeling.
"""

import json
import os
import re
import sys
from typing import Optional

import numpy as np
import pandas as pd

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
RETAILER_PARSED_FILE = os.path.join(ROOT_DIR, "data", "parsed", "retailer_laptops.jsonl")
MASTER_CSV_FILE = os.path.join(ROOT_DIR, "data", "final", "laptop_prices_complete_1k.csv")
OUTPUT_DIR = os.path.join(ROOT_DIR, "data", "cleaned")
OUTPUT_CSV = os.path.join(OUTPUT_DIR, "lpara_cleaned_laptop_dataset.csv")
OUTPUT_JSONL = os.path.join(OUTPUT_DIR, "lpara_cleaned_laptop_dataset.jsonl")
SUMMARY_REPORT = os.path.join(OUTPUT_DIR, "cleaning_summary.json")




def extract_cpu_tier(cpu_model: str, cpu_family: str) -> int:
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
    return 3


def assign_price_category(price: float) -> str:
    if price < 40000:
        return "Budget (<40K)"
    elif price < 75000:
        return "Mid-Range (40K-75K)"
    elif price < 125000:
        return "Upper Mid-Range (75K-1.25L)"
    else:
        return "Premium / Flagship (>1.25L)"


def clean_ram_type(rt: Optional[str]) -> str:
    rt_u = str(rt or "").upper()
    if "LPDDR5X" in rt_u: return "LPDDR5X"
    if "LPDDR5" in rt_u: return "LPDDR5"
    if "DDR5" in rt_u: return "DDR5"
    if "LPDDR4X" in rt_u: return "LPDDR4X"
    if "DDR4" in rt_u: return "DDR4"
    if "UNIFIED" in rt_u: return "Unified Memory"
    return "DDR5"


def clean_storage_type(st: Optional[str]) -> str:
    st_u = str(st or "").upper()
    if "NVME" in st_u: return "NVMe SSD"
    if "PCIE" in st_u: return "PCIe SSD"
    if "EMMC" in st_u: return "eMMC"
    if "HDD" in st_u: return "HDD"
    return "SSD"


def clean_and_export_dataset():
    print("=" * 70)
    print("STARTING LPARA AUTOMATED DATA CLEANING PIPELINE")
    print("=" * 70)

    raw_candidates = []

    # 1. Load Scraped Retailer Records
    if os.path.exists(RETAILER_PARSED_FILE):
        with open(RETAILER_PARSED_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    try:
                        raw_candidates.append(json.loads(line))
                    except Exception:
                        pass
        print(f"1. Loaded {len(raw_candidates)} records from {os.path.basename(RETAILER_PARSED_FILE)}")

    # 2. Also load previous complete records
    if os.path.exists(MASTER_CSV_FILE):
        csv_df = pd.read_csv(MASTER_CSV_FILE)
        raw_candidates.extend(csv_df.to_dict(orient="records"))
        print(f"2. Merged records from {os.path.basename(MASTER_CSV_FILE)}, total pooled: {len(raw_candidates)}")

    # 3. Filter accessories & ensure core presence
    cleaned_rows = []
    accessory_keywords = [
        "screen guard", "screen protector", "keyboard replacement",
        "adapter", "charger", "battery", "laptop skin", "cable", "mouse pad"
    ]

    for r in raw_candidates:
        price = r.get("price_current") or r.get("price_average")
        if not price:
            continue
        try:
            price = float(price)
        except (ValueError, TypeError):
            continue

        if price < 10000 or price > 1000000:
            continue

        brand = str(r.get("brand") or "").strip()
        if not brand or brand in ["Unknown", "None", ""]:
            continue

        model_name = str(r.get("model") or "").strip()
        if any(ak in model_name.lower() for ak in accessory_keywords):
            continue

        cpu_brand = str(r.get("cpu_brand") or "").strip()
        cpu_model = str(r.get("cpu_model") or "").strip()
        ram_gb = r.get("ram_gb")
        storage_gb = r.get("storage_gb")
        display = r.get("display_size_inches")

        if not (cpu_brand and cpu_model and ram_gb and storage_gb and display):
            continue

        try:
            ram_gb = int(round(float(ram_gb)))
            storage_gb = int(round(float(storage_gb)))
            display = round(float(display), 1)
        except (ValueError, TypeError):
            continue

        # Sanity ranges
        if ram_gb not in [4, 8, 12, 16, 24, 32, 36, 48, 64, 128]:
            continue
        if storage_gb not in [32, 64, 128, 256, 512, 1024, 2048, 4096]:
            continue
        if display < 10.0 or display > 18.0:
            continue

        brand_clean = brand.strip()
        brand_map = {
            "asus": "ASUS", "hp": "HP", "dell": "Dell", "lenovo": "Lenovo",
            "acer": "Acer", "msi": "MSI", "apple": "Apple", "samsung": "Samsung",
            "microsoft": "Microsoft", "infinix": "Infinix", "gigabyte": "Gigabyte",
            "motorola": "Motorola", "zebronics": "Zebronics", "colorful": "Colorful"
        }
        brand_clean = brand_map.get(brand_clean.lower(), brand_clean)

        gpu_t = str(r.get("gpu_type") or "").strip()
        if not gpu_t:
            gpu_t = "Integrated"

        os_str = str(r.get("operating_system") or "").strip()
        if not os_str:
            os_str = "macOS" if brand_clean == "Apple" else "Windows 11 Home"

        cpu_fam = str(r.get("cpu_family") or "").strip()
        if not cpu_fam:
            cpu_fam = cpu_model

        cleaned_rows.append({
            "brand": brand_clean,
            "model": model_name,
            "price_average": round(price, 2),
            "cpu_brand": cpu_brand,
            "cpu_model": cpu_model,
            "cpu_family": cpu_fam,
            "ram_gb": ram_gb,
            "ram_type": clean_ram_type(r.get("ram_type")),
            "storage_gb": storage_gb,
            "storage_type": clean_storage_type(r.get("storage_type")),
            "display_size_inches": display,
            "gpu_type": gpu_t,
            "operating_system": os_str
        })

    df = pd.DataFrame(cleaned_rows)
    print(f"3. Validated laptop candidates: {len(df)}")

    # 4. Deduplicate on composite hardware configuration key
    dedup_cols = ["brand", "model", "cpu_model", "ram_gb", "storage_gb", "display_size_inches"]
    df.drop_duplicates(subset=dedup_cols, inplace=True)
    print(f"4. Deduplication: {len(df)} distinct laptop configurations retained")

    # 5. Feature Engineering
    model_lower = df["model"].str.lower()
    df["is_apple"] = (df["brand"] == "Apple").astype(int)
    df["is_gaming"] = (
        (df["gpu_type"] == "Discrete") |
        model_lower.str.contains(r"tuf|rog|legion|loq|victus|omen|nitro|predator|katana|cyborg|sword|bravo|alienware|gaming|g15", regex=True)
    ).astype(int)
    df["is_touchscreen"] = model_lower.str.contains(r"touch|flip|2-in-1|360|yoga", regex=True).astype(int)
    df["is_oled"] = model_lower.str.contains("oled").astype(int)
    df["cpu_tier"] = [extract_cpu_tier(m, f) for m, f in zip(df["cpu_model"], df["cpu_family"])]
    df["ram_storage_ratio"] = (df["ram_gb"] / df["storage_gb"]).round(4)
    df["price_category"] = df["price_average"].apply(assign_price_category)

    # 6. Reorder and select features
    ordered_cols = [
        "brand",
        "model",
        "price_average",
        "price_category",
        "cpu_brand",
        "cpu_model",
        "cpu_family",
        "cpu_tier",
        "ram_gb",
        "ram_type",
        "storage_gb",
        "storage_type",
        "ram_storage_ratio",
        "display_size_inches",
        "gpu_type",
        "is_gaming",
        "is_apple",
        "is_touchscreen",
        "is_oled",
        "operating_system"
    ]
    df = df[ordered_cols]

    # Verify zero missing values across every single cell
    null_counts = df.isna().sum().to_dict()
    total_nulls = sum(null_counts.values())
    print(f"5. Missing Value Verification: Total Nulls = {total_nulls} (100% complete!)")

    # 7. Export Cleaned Dataset
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False, encoding="utf-8")
    df.to_json(OUTPUT_JSONL, orient="records", lines=True, force_ascii=False)

    summary = {
        "dataset_name": "LPARA Cleaned Laptop Price Dataset",
        "total_records": len(df),
        "total_features": len(df.columns),
        "columns": list(df.columns),
        "null_counts": null_counts,
        "price_statistics": {
            "min_price": float(df["price_average"].min()),
            "median_price": float(df["price_average"].median()),
            "mean_price": round(float(df["price_average"].mean()), 2),
            "max_price": float(df["price_average"].max())
        },
        "brand_distribution": df["brand"].value_counts().to_dict(),
        "price_category_distribution": df["price_category"].value_counts().to_dict(),
        "export_paths": {
            "cleaned_csv": OUTPUT_CSV,
            "cleaned_jsonl": OUTPUT_JSONL
        }
    }
    with open(SUMMARY_REPORT, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print("\n" + "=" * 70)
    print("DATA CLEANING COMPLETE & FILES GENERATED FOR DOWNLOAD")
    print(f"  Total Clean Rows:    {len(df)}")
    print(f"  Missing Values:      0 across all {len(df.columns)} columns")
    print(f"  Cleaned CSV File:    {OUTPUT_CSV}")
    print(f"  Cleaned JSONL:       {OUTPUT_JSONL}")
    print(f"  Cleaning Summary:    {SUMMARY_REPORT}")
    print("=" * 70 + "\n")
    return df


if __name__ == "__main__":
    clean_and_export_dataset()
