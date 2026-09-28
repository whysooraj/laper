import glob
import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

PARSED_DIR = os.path.join("data", "parsed")
OUTPUT_FILE = os.path.join(PARSED_DIR, "all_scraped.jsonl")


def merge_parsed_sources() -> int:
    source_files = [
        os.path.join(PARSED_DIR, "asus.jsonl"),
        os.path.join(PARSED_DIR, "lenovo.jsonl"),
        os.path.join(PARSED_DIR, "retailer_laptops.jsonl"),
    ]

    all_records = []
    file_counts = {}

    for sf in source_files:
        if not os.path.exists(sf):
            print(f"Skipping non-existent source: {sf}")
            continue

        count = 0
        with open(sf, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        record = json.loads(line)
                        all_records.append(record)
                        count += 1
                    except Exception as e:
                        pass
        file_counts[sf] = count

    print("\n========================================")
    print("MERGING CRAWLED SOURCES")
    print("========================================")
    for sf, cnt in file_counts.items():
        print(f"  {os.path.basename(sf)}: {cnt} records")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f_out:
        for r in all_records:
            f_out.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"\nTotal merged records written to {OUTPUT_FILE}: {len(all_records)}")
    print("========================================\n")
    return len(all_records)


if __name__ == "__main__":
    merge_parsed_sources()
