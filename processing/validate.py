import json
import os
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Dict, List, Tuple


INVALID_FILE = "data/normalized/invalid.jsonl"
VALID_FILE = "data/normalized/valid.jsonl"


def validate_record(record: Dict) -> Tuple[bool, List[str]]:
    """
    Validates a laptop record against sanity rules.
    Returns (is_valid, list_of_reasons).
    """
    reasons = []

    # Mandatory identity fields
    brand = record.get("brand")
    if not brand or not str(brand).strip():
        reasons.append("Missing brand")

    model = record.get("model")
    if not model or not str(model).strip():
        reasons.append("Missing model")

    url = record.get("url")
    if not url or not str(url).strip():
        reasons.append("Missing url")

    website = record.get("website")
    if not website or not str(website).strip():
        reasons.append("Missing website")

    # Check for accessories that leaked into search results
    combined_desc = (str(record.get("model") or "") + " " + str(record.get("url") or "")).lower()
    accessory_words = ["screen guard", "screen protector", "keyboard", "adapter", "battery", "charger", "mousepad", "sleeve", "skin"]
    for w in accessory_words:
        if w in combined_desc and not any(kw in combined_desc for kw in ["backlit keyboard", "keyboard with", "keyboard,"]):
            reasons.append(f"Suspected accessory: contains '{w}'")
            break

    # Price validations (must be at least 10000 for a laptop)
    price_curr = record.get("price_current")
    if price_curr is not None:
        if not isinstance(price_curr, (int, float)) or price_curr < 10000:
            reasons.append(f"Invalid price_current (must be >= 10000 for laptop): {price_curr}")

    price_orig = record.get("price_original")
    if price_orig is not None:
        if not isinstance(price_orig, (int, float)) or price_orig < 10000:
            reasons.append(f"Invalid price_original: {price_orig}")

    price_avg = record.get("price_average")
    if price_avg is not None:
        if not isinstance(price_avg, (int, float)) or price_avg < 10000:
            reasons.append(f"Invalid price_average: {price_avg}")

    # RAM validations
    ram = record.get("ram_gb")
    if ram is not None:
        if not isinstance(ram, (int, float)) or ram <= 0 or ram > 256:
            reasons.append(f"Invalid ram_gb: {ram}")

    # Storage validations
    storage = record.get("storage_gb")
    if storage is not None:
        if not isinstance(storage, (int, float)) or storage <= 0 or storage > 16384:
            reasons.append(f"Invalid storage_gb: {storage}")

    # Display validations
    display = record.get("display_size_inches")
    if display is not None:
        if not isinstance(display, (int, float)) or display < 10.0 or display > 21.0:
            reasons.append(f"Unreasonable display_size_inches: {display}")

    refresh = record.get("refresh_rate_hz")
    if refresh is not None:
        if not isinstance(refresh, (int, float)) or refresh < 30 or refresh > 600:
            reasons.append(f"Unreasonable refresh_rate_hz: {refresh}")

    # Physical validations
    weight = record.get("weight_kg")
    if weight is not None:
        if not isinstance(weight, (int, float)) or weight < 0.5 or weight > 6.0:
            reasons.append(f"Unreasonable weight_kg: {weight}")

    battery = record.get("battery_wh")
    if battery is not None:
        if not isinstance(battery, (int, float)) or battery <= 0 or battery > 150:
            reasons.append(f"Unreasonable battery_wh: {battery}")

    # CPU validations
    cores = record.get("cpu_cores")
    if cores is not None:
        if not isinstance(cores, int) or cores <= 0 or cores > 128:
            reasons.append(f"Invalid cpu_cores: {cores}")

    is_valid = len(reasons) == 0
    return is_valid, reasons


def validate_file(input_file: str, append_valid: bool = True):
    """
    Validates a JSONL file, splitting into valid and invalid.
    """
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return 0, 0

    os.makedirs("data/normalized", exist_ok=True)

    valid_count = 0
    invalid_count = 0

    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(INVALID_FILE, "a", encoding="utf-8") as f_inv, \
         open(VALID_FILE, "a" if append_valid else "w", encoding="utf-8") as f_val:

        for line_no, line in enumerate(f_in, start=1):
            line = line.strip()
            if not line:
                continue

            try:
                record = json.loads(line)
            except Exception as e:
                f_inv.write(json.dumps({
                    "raw_line": line,
                    "reasons": [f"JSON parse error at line {line_no}: {e}"]
                }) + "\n")
                invalid_count += 1
                continue

            is_valid, reasons = validate_record(record)
            if is_valid:
                f_val.write(json.dumps(record, ensure_ascii=False) + "\n")
                valid_count += 1
            else:
                record["validation_reasons"] = reasons
                f_inv.write(json.dumps(record, ensure_ascii=False) + "\n")
                invalid_count += 1

    print(f"Validation for {input_file}: {valid_count} valid, {invalid_count} invalid.")
    return valid_count, invalid_count


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "data/asus_laptops.jsonl"
    validate_file(target)
