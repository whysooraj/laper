import csv
import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = "data/normalized/valid.jsonl"
OUT_CSV = "data/final/laptop_prices_complete_1k.csv"
OUT_JSONL = "data/final/laptop_prices_complete_1k.jsonl"
REPORT_JSON = "data/final/complete_1k_report.json"

CORE_REQUIRED_COLUMNS = [
    "brand",
    "model",
    "cpu_brand",
    "cpu_model",
    "ram_gb",
    "storage_gb",
    "display_size_inches",
    "operating_system",
    "price_average"
]

ALL_EXPORT_COLUMNS = [
    "brand",
    "model",
    "model_number",
    "series",
    "release_year",
    "cpu_brand",
    "cpu_model",
    "cpu_family",
    "cpu_generation",
    "cpu_cores",
    "cpu_threads",
    "gpu_brand",
    "gpu_model",
    "gpu_type",
    "gpu_vram_gb",
    "npu",
    "npu_tops",
    "ram_gb",
    "ram_type",
    "ram_speed_mhz",
    "storage_gb",
    "storage_type",
    "storage_upgradeable",
    "display_size_inches",
    "resolution",
    "panel_type",
    "refresh_rate_hz",
    "touchscreen",
    "weight_kg",
    "battery_wh",
    "operating_system",
    "windows_included",
    "price_current",
    "price_original",
    "price_discount",
    "price_lowest",
    "price_average",
    "price_highest",
    "price_source_count",
    "url"
]


def export_complete_dataset(min_count: int = 1000):
    if not os.path.exists(INPUT_FILE):
        print(f"File not found: {INPUT_FILE}")
        return 0

    complete_records = []
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)

            # Ensure price_average is set
            if r.get("price_average") is None and r.get("price_current") is not None:
                r["price_average"] = r["price_current"]

            # Filter accessories or prices < 10000
            price = r.get("price_average") or r.get("price_current")
            if not price or price < 10000:
                continue

            # Ensure brand is known
            brand = r.get("brand")
            if not brand or brand == "Unknown":
                continue

            # Check core required columns: ZERO MISSING VALUES ALLOWED
            is_complete = True
            for col in CORE_REQUIRED_COLUMNS:
                val = r.get(col)
                if val is None or val == "" or (isinstance(val, (int, float)) and val <= 0):
                    is_complete = False
                    break

            if is_complete:
                # Fill default secondary categoricals if missing
                if not r.get("ram_type"):
                    r["ram_type"] = "DDR4" if (r.get("release_year") and r.get("release_year") <= 2022) else "DDR5"
                if not r.get("storage_type"):
                    r["storage_type"] = "SSD"
                if not r.get("gpu_type"):
                    r["gpu_type"] = "Discrete" if (r.get("gpu_model") and any(g in str(r.get("gpu_model")) for g in ["RTX", "GTX", "GeForce", "Radeon RX"])) else "Integrated"

                complete_records.append(r)

    print(f"\n============================================================")
    print(f"ZERO-MISSING-VALUE COMPLETE DATASET EXPORT")
    print(f"============================================================")
    print(f"Total Complete Configurations: {len(complete_records)}")

    # Brand Distribution
    from collections import Counter
    brands = Counter(r["brand"] for r in complete_records)
    print("\nBrand Distribution:")
    for b, c in brands.most_common():
        print(f"  {b:15s}: {c}")

    prices = [r["price_average"] for r in complete_records]
    min_p = min(prices) if prices else 0
    avg_p = sum(prices) / len(prices) if prices else 0
    max_p = max(prices) if prices else 0

    print(f"\nPrice Summary (Zero Missing Values):")
    print(f"  Lowest Price:   ₹{min_p:,.2f}")
    print(f"  Average Price:  ₹{avg_p:,.2f}")
    print(f"  Highest Price:  ₹{max_p:,.2f}")

    # Export to CSV
    os.makedirs(os.path.dirname(OUT_CSV), exist_ok=True)
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f_csv:
        writer = csv.DictWriter(f_csv, fieldnames=ALL_EXPORT_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        for r in complete_records:
            writer.writerow(r)

    # Export to JSONL
    with open(OUT_JSONL, "w", encoding="utf-8") as f_json:
        for r in complete_records:
            f_json.write(json.dumps(r, ensure_ascii=False) + "\n")

    # Generate metadata report
    report_data = {
        "dataset_name": "LPARA Zero-Missing-Value Complete Dataset",
        "total_complete_configurations": len(complete_records),
        "target_variable": "price_average",
        "core_features_missing_count": 0,
        "price_summary": {
            "lowest": round(min_p, 2),
            "average": round(avg_p, 2),
            "highest": round(max_p, 2)
        },
        "brand_breakdown": dict(brands.most_common())
    }
    with open(REPORT_JSON, "w", encoding="utf-8") as f_rep:
        json.dump(report_data, f_rep, indent=2)

    print(f"\nFiles Generated:")
    print(f"  CSV:   {OUT_CSV}")
    print(f"  JSONL: {OUT_JSONL}")
    print(f"  Meta:  {REPORT_JSON}")
    print(f"============================================================\n")

    return len(complete_records)


if __name__ == "__main__":
    export_complete_dataset()
