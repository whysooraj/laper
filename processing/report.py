import csv
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Dict, List


REPORT_JSON = "data/final/dataset_report.json"
FINAL_CSV = "data/final/laptop_prices.csv"
FINAL_JSONL = "data/final/laptop_prices.jsonl"


def generate_report(records: List[Dict], export_final: bool = False) -> Dict:
    total_records = len(records)
    if total_records == 0:
        print("No records found to report.")
        return {}

    brands = set()
    models = set()
    configs = set()

    missing_cpu = 0
    missing_gpu = 0
    missing_ram = 0
    missing_storage = 0
    missing_display = 0
    missing_price = 0

    has_npu = 0
    has_fingerprint = 0
    has_face_unlock = 0
    has_windows = 0

    prices = []
    price_source_counts = []

    # Track missing count for every column
    sample_record = records[0]
    all_keys = list(sample_record.keys())
    missing_by_col = {k: 0 for k in all_keys}

    for r in records:
        b = r.get("brand")
        if b:
            brands.add(b)
        m = r.get("model")
        if m:
            models.add(m)

        # Unique config tuple
        cfg_key = (
            b,
            r.get("model_number") or m,
            r.get("cpu_model"),
            r.get("ram_gb"),
            r.get("storage_gb"),
            r.get("gpu_model"),
            r.get("display_size_inches")
        )
        configs.add(cfg_key)

        # Missing checks
        if not r.get("cpu_model"):
            missing_cpu += 1
        if not r.get("gpu_model"):
            missing_gpu += 1
        if r.get("ram_gb") is None:
            missing_ram += 1
        if r.get("storage_gb") is None:
            missing_storage += 1
        if r.get("display_size_inches") is None:
            missing_display += 1

        p = r.get("price_average") or r.get("price_current")
        if p is None or p <= 0:
            missing_price += 1
        else:
            prices.append(float(p))

        psc = r.get("price_source_count")
        if psc:
            price_source_counts.append(psc)

        if r.get("npu") or r.get("npu_tops"):
            has_npu += 1
        if r.get("fingerprint") is True:
            has_fingerprint += 1
        if r.get("face_unlock") is True:
            has_face_unlock += 1
        if r.get("windows_included") is True:
            has_windows += 1

        for k in all_keys:
            val = r.get(k)
            if val is None or val == "" or val == []:
                missing_by_col[k] = missing_by_col.get(k, 0) + 1

    min_p = round(min(prices), 2) if prices else 0.0
    avg_p = round(sum(prices) / len(prices), 2) if prices else 0.0
    max_p = round(max(prices), 2) if prices else 0.0

    missing_percentages = {
        k: round((cnt / total_records) * 100, 2)
        for k, cnt in missing_by_col.items()
    }

    report = {
        "total_records": total_records,
        "total_brands": len(brands),
        "brands_list": sorted(list(brands)),
        "total_unique_models": len(models),
        "total_unique_configurations": len(configs),
        "price_range": {
            "lowest": min_p,
            "average": avg_p,
            "highest": max_p,
            "prices_recorded": len(prices)
        },
        "missing_summary": {
            "missing_cpu": missing_cpu,
            "missing_gpu": missing_gpu,
            "missing_ram": missing_ram,
            "missing_storage": missing_storage,
            "missing_display": missing_display,
            "missing_price": missing_price
        },
        "features_present": {
            "records_with_npu": has_npu,
            "records_with_fingerprint": has_fingerprint,
            "records_with_face_unlock": has_face_unlock,
            "records_with_windows": has_windows
        },
        "column_missing_percentage": missing_percentages
    }

    # Print terminal report
    print("\n" + "=" * 40)
    print("LPARA DATASET REPORT")
    print("=" * 40)
    print(f"Records:        {total_records}")
    print(f"Brands:         {len(brands)} ({', '.join(sorted(brands))})")
    print(f"Models:         {len(models)}")
    print(f"Configurations: {len(configs)}")
    print()
    print("Price range:")
    print(f"Lowest:         ₹{min_p:,.2f}")
    print(f"Average:        ₹{avg_p:,.2f}")
    print(f"Highest:        ₹{max_p:,.2f}")
    print()
    print("Missing data:")
    print(f"CPU:            {missing_cpu} ({missing_cpu/total_records*100:.1f}%)")
    print(f"GPU:            {missing_gpu} ({missing_gpu/total_records*100:.1f}%)")
    print(f"RAM:            {missing_ram} ({missing_ram/total_records*100:.1f}%)")
    print(f"Storage:        {missing_storage} ({missing_storage/total_records*100:.1f}%)")
    print(f"Display:        {missing_display} ({missing_display/total_records*100:.1f}%)")
    print(f"Price:          {missing_price} ({missing_price/total_records*100:.1f}%)")
    print()
    print(f"Price sources recorded: {len(prices)}")
    print("=" * 40 + "\n")

    os.makedirs("data/final", exist_ok=True)
    with open(REPORT_JSON, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    if export_final:
        # Export CSV
        with open(FINAL_CSV, "w", newline="", encoding="utf-8") as f_csv:
            writer = csv.DictWriter(f_csv, fieldnames=all_keys)
            writer.writeheader()
            for r in records:
                # Format lists as JSON string for CSV compatibility
                row = {k: json.dumps(v) if isinstance(v, list) else v for k, v in r.items()}
                writer.writerow(row)

        # Export JSONL
        with open(FINAL_JSONL, "w", encoding="utf-8") as f_jsonl:
            for r in records:
                f_jsonl.write(json.dumps(r, ensure_ascii=False) + "\n")

        print(f"Exported final dataset to:\n  - {FINAL_CSV}\n  - {FINAL_JSONL}")

    return report


def main():
    target_file = sys.argv[1] if len(sys.argv) > 1 else "data/asus_laptops.jsonl"
    export = "--export" in sys.argv or "-e" in sys.argv

    if not os.path.exists(target_file):
        print(f"File not found: {target_file}")
        return

    records = []
    with open(target_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    generate_report(records, export_final=export)


if __name__ == "__main__":
    main()
