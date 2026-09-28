import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Dict, List, Tuple


def calculate_price_aggregates(prices: List[float]) -> Dict:
    """
    Computes price_lowest, price_average, price_highest, price_source_count, and price_status.
    Detects outliers (e.g. values < 30% of median or > 300% of median).
    """
    if not prices:
        return {
            "price_lowest": None,
            "price_average": None,
            "price_highest": None,
            "price_source_count": 0,
            "price_status": "insufficient_sources"
        }

    valid_prices = [p for p in prices if isinstance(p, (int, float)) and p >= 10000]

    if not valid_prices:
        return {
            "price_lowest": None,
            "price_average": None,
            "price_highest": None,
            "price_source_count": 0,
            "price_status": "insufficient_sources"
        }

    sorted_prices = sorted(valid_prices)
    median = sorted_prices[len(sorted_prices) // 2]

    # Outlier filter: keep prices within [0.4 * median, 2.5 * median]
    filtered_prices = [p for p in sorted_prices if 0.4 * median <= p <= 2.5 * median]
    has_outlier = len(filtered_prices) < len(sorted_prices)

    calc_list = filtered_prices if filtered_prices else sorted_prices

    price_lowest = round(float(min(calc_list)), 2)
    price_highest = round(float(max(calc_list)), 2)
    price_average = round(float(sum(calc_list) / len(calc_list)), 2)
    price_source_count = len(calc_list)

    if has_outlier:
        price_status = "outlier"
    elif price_source_count >= 2:
        price_status = "valid"
    else:
        price_status = "insufficient_sources"

    return {
        "price_lowest": price_lowest,
        "price_average": price_average,
        "price_highest": price_highest,
        "price_source_count": price_source_count,
        "price_status": price_status
    }


def aggregate_prices_by_config(records: List[Dict]) -> List[Dict]:
    """
    Groups configurations and aggregates price data.
    """
    from processing.deduplicate import make_config_key

    groups: Dict[Tuple, List[Dict]] = {}
    for r in records:
        key = make_config_key(r)
        if key not in groups:
            groups[key] = []
        groups[key].append(r)

    aggregated_records = []
    for key, items in groups.items():
        # Collect all positive prices from the items
        prices = []
        for it in items:
            for p_key in ["price_current", "price_original"]:
                val = it.get(p_key)
                if val and isinstance(val, (int, float)) and val >= 10000:
                    prices.append(val)

        # Base record is the most complete item in group
        base = max(items, key=lambda x: sum(1 for v in x.values() if v is not None))
        stats = calculate_price_aggregates(prices)

        base["price_lowest"] = stats["price_lowest"]
        base["price_average"] = stats["price_average"]
        base["price_highest"] = stats["price_highest"]
        base["price_source_count"] = stats["price_source_count"]
        base["price_status"] = stats["price_status"]

        # Ensure price_current is consistent
        if base.get("price_current") is None and stats["price_average"] is not None:
            base["price_current"] = stats["price_average"]

        aggregated_records.append(base)

    return aggregated_records


def process_prices_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return 0

    records = []
    with open(input_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except Exception:
                    pass

    processed = aggregate_prices_by_config(records)
    os.makedirs(os.path.dirname(output_file) or ".", exist_ok=True)
    with open(output_file, "w", encoding="utf-8") as f:
        for r in processed:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

    print(f"Processed prices for {len(processed)} unique configurations -> {output_file}")
    return len(processed)


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/asus_laptops.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/normalized/asus_priced.jsonl"
    process_prices_file(src, dst)
