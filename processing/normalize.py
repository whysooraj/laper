import json
import os
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from typing import Dict, Optional


def normalize_brand(brand: Optional[str], model: Optional[str] = None, url: Optional[str] = None) -> str:
    combined = (str(brand or "") + " " + str(model or "") + " " + str(url or "")).upper()
    if any(k in combined for k in ["ASUS", "ROG", "TUF", "ZENBOOK", "VIVOBOOK"]):
        return "ASUS"
    if any(k in combined for k in ["LENOVO", "THINKPAD", "IDEAPAD", "LEGION", "LOQ"]):
        return "Lenovo"
    if any(k in combined for k in ["HP", "HEWLETT", "VICTUS", "OMEN", "PAVILION"]):
        return "HP"
    if any(k in combined for k in ["DELL", "ALIENWARE", "INSPIRON", "LATITUDE", "VOSTRO", "XPS"]):
        return "Dell"
    if any(k in combined for k in ["ACER", "PREDATOR", "NITRO", "SWIFT", "ASPIRE"]):
        return "Acer"
    if "MSI" in combined:
        return "MSI"
    if any(k in combined for k in ["APPLE", "MACBOOK"]):
        return "Apple"
    if any(k in combined for k in ["SAMSUNG", "GALAXY BOOK"]):
        return "Samsung"
    if any(k in combined for k in ["LG", "GRAM"]):
        return "LG"
    if any(k in combined for k in ["MICROSOFT", "SURFACE"]):
        return "Microsoft"
    if "INFINIX" in combined:
        return "Infinix"
    if any(k in combined for k in ["GIGABYTE", "AORUS"]):
        return "Gigabyte"
    if any(k in combined for k in ["MOTOROLA", "MOTOBOOK"]):
        return "Motorola"
    if "PRIMEBOOK" in combined:
        return "Primebook"
    if "ZEBRONICS" in combined:
        return "Zebronics"
    if "COLORFUL" in combined:
        return "Colorful"
    if "THOMSON" in combined:
        return "Thomson"
    return str(brand).strip() if brand else "Unknown"


def normalize_cpu(record: Dict) -> Dict:
    cpu_model = record.get("cpu_model")
    if not cpu_model:
        return record

    cleaned = re.sub(r"[™®]", "", str(cpu_model))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    # Clean redundant brand prefixes if present
    for prefix in ["AMD ", "Intel ", "Apple "]:
        if cleaned.startswith(prefix):
            cleaned = cleaned[len(prefix):].strip()

    record["cpu_model"] = cleaned

    # Ensure brand is set
    if not record.get("cpu_brand"):
        if any(k in cleaned for k in ["Ryzen", "Athlon", "Threadripper"]):
            record["cpu_brand"] = "AMD"
        elif any(k in cleaned for k in ["Core", "Celeron", "Pentium", "Xeon"]):
            record["cpu_brand"] = "Intel"
        elif "Snapdragon" in cleaned:
            record["cpu_brand"] = "Qualcomm"
        elif cleaned.startswith("M1") or cleaned.startswith("M2") or cleaned.startswith("M3") or cleaned.startswith("M4"):
            record["cpu_brand"] = "Apple"

    return record


def normalize_gpu(record: Dict) -> Dict:
    gpu_model = record.get("gpu_model")
    if not gpu_model:
        return record

    cleaned = re.sub(r"[™®]", "", str(gpu_model))
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    record["gpu_model"] = cleaned

    # Brand and type
    if not record.get("gpu_brand"):
        if any(k in cleaned for k in ["GeForce", "RTX", "GTX", "NVIDIA"]):
            record["gpu_brand"] = "NVIDIA"
            record["gpu_type"] = "Discrete"
        elif "Radeon" in cleaned or "AMD" in cleaned:
            record["gpu_brand"] = "AMD"
            if re.search(r"RX\s+\d{4}", cleaned):
                record["gpu_type"] = "Discrete"
            else:
                record["gpu_type"] = "Integrated"
        elif any(k in cleaned for k in ["Arc", "Iris", "Intel"]):
            record["gpu_brand"] = "Intel"
            if "Arc A" in cleaned:
                record["gpu_type"] = "Discrete"
            else:
                record["gpu_type"] = "Integrated"
        elif "Adreno" in cleaned or "Qualcomm" in cleaned:
            record["gpu_brand"] = "Qualcomm"
            record["gpu_type"] = "Integrated"
        elif "Apple" in cleaned:
            record["gpu_brand"] = "Apple"
            record["gpu_type"] = "Integrated"

    return record


def normalize_ram(record: Dict) -> Dict:
    ram_gb = record.get("ram_gb")
    if ram_gb is not None:
        try:
            ram_gb = int(round(float(ram_gb)))
            # Standard laptop RAM sizes
            if ram_gb > 512:
                ram_gb = int(round(ram_gb / 1024))
            record["ram_gb"] = ram_gb
        except (ValueError, TypeError):
            pass

    ram_type = record.get("ram_type")
    if ram_type:
        rt = str(ram_type).upper().strip()
        if "LPDDR5X" in rt:
            record["ram_type"] = "LPDDR5X"
        elif "LPDDR5" in rt:
            record["ram_type"] = "LPDDR5"
        elif "LPDDR4X" in rt:
            record["ram_type"] = "LPDDR4X"
        elif "LPDDR4" in rt:
            record["ram_type"] = "LPDDR4"
        elif "DDR5" in rt:
            record["ram_type"] = "DDR5"
        elif "DDR4" in rt:
            record["ram_type"] = "DDR4"
        elif "UNIFIED" in rt:
            record["ram_type"] = "Unified Memory"

    return record


def normalize_storage(record: Dict) -> Dict:
    storage_gb = record.get("storage_gb")
    if storage_gb is not None:
        try:
            val = float(storage_gb)
            if val <= 16:  # Specified in TB
                val = val * 1024
            record["storage_gb"] = int(round(val))
        except (ValueError, TypeError):
            pass

    st = record.get("storage_type")
    if st:
        st_clean = re.sub(r"[™®]", "", str(st)).strip()
        if "NVMe" in st_clean:
            record["storage_type"] = "NVMe SSD"
        elif "PCIe" in st_clean:
            record["storage_type"] = "PCIe SSD"
        elif "SATA" in st_clean:
            record["storage_type"] = "SATA SSD"
        elif "eMMC" in st_clean:
            record["storage_type"] = "eMMC"

    return record


def normalize_display(record: Dict) -> Dict:
    res = record.get("resolution")
    width = record.get("resolution_width")
    height = record.get("resolution_height")

    if res and (not width or not height):
        m = re.search(r"(\d{3,5})[xX*×](\d{3,5})", str(res))
        if m:
            width = int(m.group(1))
            height = int(m.group(2))
            record["resolution_width"] = width
            record["resolution_height"] = height
            record["resolution"] = f"{width}x{height}"

    if width and height and not record.get("aspect_ratio"):
        ratio_val = width / height
        if abs(ratio_val - 16 / 9) < 0.05:
            record["aspect_ratio"] = "16:9"
        elif abs(ratio_val - 16 / 10) < 0.05:
            record["aspect_ratio"] = "16:10"
        elif abs(ratio_val - 3 / 2) < 0.05:
            record["aspect_ratio"] = "3:2"
        elif abs(ratio_val - 4 / 3) < 0.05:
            record["aspect_ratio"] = "4:3"

    # Infer display size from model name if missing
    if record.get("display_size_inches") is None:
        m = str(record.get("model") or "")
        if re.search(r"\b(?:14|14s|14-inch|14\.0)\b", m, re.IGNORECASE) or any(k in m for k in ["Vivobook 14", "IdeaPad 14", "Slim 14", "ThinkPad 14", "E14", "T14", " 14 "]):
            record["display_size_inches"] = 14.0
        elif re.search(r"\b(?:15|15s|15-inch|15\.6)\b", m, re.IGNORECASE) or any(k in m for k in ["Vivobook 15", "IdeaPad 15", "Slim 15", "ThinkPad 15", "E15", "T15", " 15s", " 15 "]):
            record["display_size_inches"] = 15.6
        elif re.search(r"\b(?:16|16s|16-inch|16\.0)\b", m, re.IGNORECASE) or any(k in m for k in ["Vivobook 16", "IdeaPad 16", "Slim 16", "ThinkPad 16", "E16", "T16", "Legion 16", " 16 "]):
            record["display_size_inches"] = 16.0
        elif re.search(r"\b(?:13|13s|13-inch|13\.3)\b", m, re.IGNORECASE):
            record["display_size_inches"] = 13.3
        elif re.search(r"\b(?:17|17s|17-inch|17\.3)\b", m, re.IGNORECASE):
            record["display_size_inches"] = 17.3

    return record


def normalize_os(record: Dict) -> Dict:
    os_name = record.get("operating_system")
    if os_name:
        os_str = str(os_name).strip()
        if re.search(r"Windows\s+11\s+Home", os_str, re.IGNORECASE):
            record["operating_system"] = "Windows 11 Home"
            record["windows_included"] = True
        elif re.search(r"Windows\s+11\s+Pro", os_str, re.IGNORECASE):
            record["operating_system"] = "Windows 11 Pro"
            record["windows_included"] = True
        elif re.search(r"Windows\s+11", os_str, re.IGNORECASE):
            record["operating_system"] = "Windows 11"
            record["windows_included"] = True
        elif re.search(r"Windows\s+10", os_str, re.IGNORECASE):
            record["operating_system"] = "Windows 10"
            record["windows_included"] = True
        elif re.search(r"macOS", os_str, re.IGNORECASE):
            record["operating_system"] = "macOS"
            record["windows_included"] = False
        elif re.search(r"DOS|FreeDOS", os_str, re.IGNORECASE):
            record["operating_system"] = "DOS"
            record["windows_included"] = False
        elif re.search(r"Linux|Ubuntu", os_str, re.IGNORECASE):
            record["operating_system"] = "Linux"
            record["windows_included"] = False
        elif re.search(r"No\s+OS", os_str, re.IGNORECASE):
            record["operating_system"] = "No OS"
            record["windows_included"] = False
    else:
        brand = record.get("brand")
        model = str(record.get("model") or "")
        if brand == "Apple":
            record["operating_system"] = "macOS"
            record["windows_included"] = False
        elif "Chromebook" in model:
            record["operating_system"] = "Chrome OS"
            record["windows_included"] = False
        else:
            record["operating_system"] = "Windows 11 Home"
            record["windows_included"] = True

    return record


def normalize_record(record: Dict) -> Dict:
    """Run full normalization pipeline on a record."""
    record["brand"] = normalize_brand(record.get("brand"), record.get("model"), record.get("url"))
    record = normalize_cpu(record)
    record = normalize_gpu(record)
    record = normalize_ram(record)
    record = normalize_storage(record)
    record = normalize_display(record)
    record = normalize_os(record)
    return record


def normalize_file(input_file: str, output_file: str):
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return 0

    count = 0
    with open(input_file, "r", encoding="utf-8") as f_in, \
         open(output_file, "w", encoding="utf-8") as f_out:
        for line in f_in:
            line = line.strip()
            if not line:
                continue
            record = json.loads(line)
            normalized = normalize_record(record)
            f_out.write(json.dumps(normalized, ensure_ascii=False) + "\n")
            count += 1

    print(f"Normalized {count} records from {input_file} -> {output_file}")
    return count


if __name__ == "__main__":
    src = sys.argv[1] if len(sys.argv) > 1 else "data/asus_laptops.jsonl"
    dst = sys.argv[2] if len(sys.argv) > 2 else "data/normalized/asus_normalized.jsonl"
    normalize_file(src, dst)
