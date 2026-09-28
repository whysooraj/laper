import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Dict, List, Tuple


DUPLICATES_FILE = "data/normalized/duplicates.jsonl"


def make_config_key(record: Dict) -> Tuple:
    """
    Creates a configuration identity tuple.
    Two products with different RAM or storage or GPU or display size remain separate configurations.
    """
    brand = str(record.get("brand") or "").strip().upper()
    model_num = str(record.get("model_number") or record.get("model") or "").strip().lower()
    cpu = str(record.get("cpu_model") or "").strip().lower()
    ram = record.get("ram_gb")
    storage = record.get("storage_gb")
    gpu = str(record.get("gpu_model") or "").strip().lower()
    display = record.get("display_size_inches")

    return (brand, model_num, cpu, ram, storage, gpu, display)


def deduplicate_records(records: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
    """
    Deduplicates a list of laptop records based on exact configuration key.
    Merges pricing or keeps best-populated record when duplicate configs are encountered.
    """
    seen = {}
    duplicates = []
    unique_list = []

    for rec in records:
        key = make_config_key(rec)
        if key in seen:
            duplicates.append({
                "duplicate_record": rec,
                "existing_record_url": seen[key].get("url"),
                "config_key": [str(x) for x in key]
            })
            # Merge price info if existing record lacked price but duplicate has it
            existing = seen[key]
            if existing.get("price_current") is None and rec.get("price_current") is not None:
                existing["price_current"] = rec.get("price_current")
                existing["price_original"] = rec.get("price_original")
                existing["price_discount"] = rec.get("price_discount")
        else:
            seen[key] = rec
            unique_list.append(rec)

    return unique_list, duplicates


def deduplicate_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return 0, 0

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    unique_records, duplicate_records = deduplicate_records(records)

    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    os.makedirs("data/normalized", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f_out:
        for r in unique_records:
            f_out.write(json.dumps(r, ensure_ascii=False) + "\n")

    with open(DUPLICATES_FILE, "a", encoding="utf-8") as f_dup:
        for d in duplicate_records:
            f_dup.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"Deduplication complete: {len(unique_records)} unique configurations, {len(duplicate_records)} duplicates logged to {DUPLICATES_FILE}")
    return len(unique_records), len(duplicate_records)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/asus_laptops.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/normalized/asus_deduped.jsonl"
    deduplicate_file(src, dst)
