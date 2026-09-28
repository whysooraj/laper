import json
import os
import sys

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from processing.merge_sources import merge_parsed_sources
from processing.normalize import normalize_file
from processing.price import process_prices_file
from processing.deduplicate import deduplicate_file
from processing.validate import validate_file
from processing.report import generate_report


def run_pipeline():
    print("\n" + "=" * 60)
    print("STARTING LPARA FULL DATASET PROCESSING PIPELINE")
    print("=" * 60)

    # 1. Merge All Scraped Data
    all_scraped_file = "data/parsed/all_scraped.jsonl"
    total_scraped = merge_parsed_sources()

    # 2. Normalize
    normalized_file = "data/normalized/normalized_laptops.jsonl"
    print(f"\n--- STEP 1: NORMALIZING DATA ({all_scraped_file} -> {normalized_file}) ---")
    total_norm = normalize_file(all_scraped_file, normalized_file)

    # 3. Price Aggregation & Target Calculation
    priced_file = "data/normalized/priced_laptops.jsonl"
    print(f"\n--- STEP 2: PRICE AGGREGATION ({normalized_file} -> {priced_file}) ---")
    total_priced = process_prices_file(normalized_file, priced_file)

    # 4. Deduplication
    deduped_file = "data/normalized/deduped_laptops.jsonl"
    print(f"\n--- STEP 3: DEDUPLICATION ({priced_file} -> {deduped_file}) ---")
    unique_count, dup_count = deduplicate_file(priced_file, deduped_file)

    # 5. Validation
    print(f"\n--- STEP 4: VALIDATION ({deduped_file}) ---")
    valid_count, invalid_count = validate_file(deduped_file, append_valid=False)

    # 6. Final Report & Export
    valid_file = "data/normalized/valid.jsonl"
    print(f"\n--- STEP 5: FINAL REPORT & EXPORT ({valid_file}) ---")
    records = []
    if os.path.exists(valid_file):
        with open(valid_file, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    records.append(json.loads(line))

    # Also save to final JSONL
    final_jsonl = "data/final/laptop_prices.jsonl"
    os.makedirs("data/final", exist_ok=True)
    with open(final_jsonl, "w", encoding="utf-8") as f_out:
        for r in records:
            f_out.write(json.dumps(r, ensure_ascii=False) + "\n")

    report = generate_report(records, export_final=True)

    # 7. Zero-Missing-Value Complete Dataset Export
    from processing.export_clean_complete import export_complete_dataset
    complete_count = export_complete_dataset()

    print("============================================================")
    print("LPARA PIPELINE EXECUTION COMPLETED SUCCESSFULLY!")
    print(f"Total Clean Configurations:        {len(records)}")
    print(f"Zero-Missing Complete Laptops:     {complete_count}")
    print(f"Exported Master CSV:               data/final/laptop_prices.csv")
    print(f"Exported Zero-Missing 1K+ CSV:     data/final/laptop_prices_complete_1k.csv")
    print(f"Exported Zero-Missing 1K+ JSONL:   data/final/laptop_prices_complete_1k.jsonl")
    print(f"Dataset Report:                    data/final/dataset_report.json")
    print("============================================================\n")


if __name__ == "__main__":
    run_pipeline()
