import datetime
import json
import re
from bs4 import BeautifulSoup


def clean(text):
    if not text:
        return ""
    # Replace non-breaking spaces and normalize whitespace
    cleaned = re.sub(r"[\xa0\u200b\u202f\s]+", " ", str(text))
    return cleaned.strip()


def remove_trademarks(text):
    if not text:
        return text
    cleaned = re.sub(r"[™®]", "", str(text))
    return clean(cleaned)


def get_json_ld(soup):
    results = []
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            content = script.string or script.get_text()
            if not content:
                continue
            data = json.loads(content)
            if isinstance(data, list):
                results.extend(data)
            else:
                results.append(data)
        except Exception:
            pass
    return results


def find_product(data):
    for item in data:
        if not isinstance(item, dict):
            continue
        item_type = item.get("@type")
        if item_type == "Product":
            return item
        if isinstance(item_type, list) and "Product" in item_type:
            return item
    return {}


def extract_text(html):
    soup = BeautifulSoup(html, "lxml")
    return clean(soup.get_text(" ", strip=True))


def first_match(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return clean(match.group(1))
    return None


def number_match(text, patterns):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    return None


# ==============================================================================
# IDENTITY EXTRACTION
# ==============================================================================

def extract_brand(product, text, url, default_website=None):
    # Check JSON-LD
    b = product.get("brand")
    if isinstance(b, dict):
        b = b.get("name")
    if b:
        b_clean = remove_trademarks(b).upper()
        if any(k in b_clean for k in ["LENOVO", "IDEAPAD", "THINKPAD", "LEGION", "YOGA", "LOQ"]):
            return "Lenovo"
        if any(k in b_clean for k in ["HEWLETT", "HP", "OMEN", "VICTUS", "PAVILION", "ENVY", "SPECTRE"]):
            return "HP"
        if any(k in b_clean for k in ["DELL", "ALIENWARE", "VOSTRO", "INSPIRON", "LATITUDE", "XPS"]):
            return "Dell"
        if any(k in b_clean for k in ["ACER", "PREDATOR", "NITRO", "SWIFT", "ASPIRE"]):
            return "Acer"
        if any(k in b_clean for k in ["ASUS", "ROG", "TUF", "ZENBOOK", "VIVOBOOK", "EXPERTBOOK"]):
            return "ASUS"
        if "MSI" in b_clean:
            return "MSI"
        if "APPLE" in b_clean:
            return "Apple"
        if "SAMSUNG" in b_clean:
            return "Samsung"
        if "LG" in b_clean:
            return "LG"
        return clean(b)

    # From URL slug or domain
    url_lower = str(url).lower()
    if re.search(r"/(?:asus|rog|tuf|zenbook|vivobook|expertbook)[/-]", url_lower) or "asus" in str(default_website).lower():
        return "ASUS"
    if re.search(r"/(?:lenovo|thinkpad|ideapad|legion|yoga|loq)[/-]", url_lower) or "lenovo" in str(default_website).lower():
        return "Lenovo"
    if re.search(r"/(?:hp|omen|victus|pavilion|envy|spectre)[/-]", url_lower) or "hp" in str(default_website).lower():
        return "HP"
    if re.search(r"/(?:dell|alienware|vostro|inspiron|latitude|xps)[/-]", url_lower) or "dell" in str(default_website).lower():
        return "Dell"
    if re.search(r"/(?:acer|predator|nitro|swift|aspire|travelmate)[/-]", url_lower) or "acer" in str(default_website).lower():
        return "Acer"
    if re.search(r"/(?:msi|katana|cyborg|sword|stealth|modern|bravo)[/-]", url_lower) or "msi" in str(default_website).lower():
        return "MSI"
    if re.search(r"/(?:apple|macbook)[/-]", url_lower) or "apple" in str(default_website).lower():
        return "Apple"
    if re.search(r"/(?:samsung|galaxy-book)[/-]", url_lower) or "samsung" in str(default_website).lower():
        return "Samsung"
    if re.search(r"/(?:lg|gram)[/-]", url_lower) or "lg" in str(default_website).lower():
        return "LG"
    if re.search(r"/(?:microsoft|surface)[/-]", url_lower):
        return "Microsoft"
    if re.search(r"/(?:infinix)[/-]", url_lower):
        return "Infinix"
    if re.search(r"/(?:gigabyte|aorus)[/-]", url_lower):
        return "Gigabyte"
    if re.search(r"/(?:motorola|motobook)[/-]", url_lower):
        return "Motorola"
    if re.search(r"/(?:primebook)[/-]", url_lower):
        return "Primebook"
    if re.search(r"/(?:zebronics)[/-]", url_lower):
        return "Zebronics"
    if re.search(r"/(?:colorful)[/-]", url_lower):
        return "Colorful"

    # From text beginning or prominent brand words
    first_text = text[:300].lower() if text else ""
    if any(k in first_text for k in ["asus", "rog ", "tuf gaming", "zenbook", "vivobook"]):
        return "ASUS"
    if any(k in first_text for k in ["lenovo", "thinkpad", "ideapad", "legion", "loq"]):
        return "Lenovo"
    if any(k in first_text for k in ["hp ", "omen", "victus", "pavilion", "envy", "spectre"]):
        return "HP"
    if any(k in first_text for k in ["dell", "alienware", "inspiron", "latitude", "vostro", "xps"]):
        return "Dell"
    if any(k in first_text for k in ["acer", "predator", "aspire", "nitro ", "swift "]):
        return "Acer"
    if any(k in first_text for k in ["msi ", "katana", "cyborg", "stealth"]):
        return "MSI"
    if any(k in first_text for k in ["apple", "macbook"]):
        return "Apple"
    if any(k in first_text for k in ["samsung", "galaxy book"]):
        return "Samsung"
    if any(k in first_text for k in ["lg gram", "lg "]):
        return "LG"
    if any(k in first_text for k in ["microsoft", "surface"]):
        return "Microsoft"
    if any(k in first_text for k in ["infinix"]):
        return "Infinix"
    if any(k in first_text for k in ["gigabyte", "aorus"]):
        return "Gigabyte"
    if any(k in first_text for k in ["motorola", "motobook"]):
        return "Motorola"
    if any(k in first_text for k in ["primebook"]):
        return "Primebook"
    if any(k in first_text for k in ["zebronics"]):
        return "Zebronics"

    return "Unknown"


def extract_model_and_number(product, text, title):
    model = product.get("name")
    if not model and title:
        # Title often contains model before pipe or hyphen
        clean_title = re.sub(r"\(.*?\)", "", title)
        parts = re.split(r"[|\-–—]", clean_title)
        if parts:
            candidate = parts[0].strip()
            # Remove leading "Add to Compare" if present
            candidate = re.sub(r"^Add to Compare\s*", "", candidate, flags=re.IGNORECASE).strip()
            # Strip processor specs from model name
            candidate = re.sub(r"\s+(?:with\s+)?(?:AMD|Intel|Apple|Qualcomm|MediaTek|Core|Ryzen|Snapdragon|Celeron).*", "", candidate, flags=re.IGNORECASE).strip()
            if len(candidate) > 3 and not candidate.lower().startswith("tech spec"):
                model = candidate

    if not model:
        model = first_match(
            text,
            [
                r"(ASUS TUF Gaming A14 \(2026\) FA401EA)",
                r"(ASUS TUF Gaming [A-Za-z0-9 ]+)",
                r"(ROG [A-Za-z0-9 ]+)",
                r"(Zenbook [A-Za-z0-9 ]+)",
                r"(Vivobook [A-Za-z0-9 ]+)",
                r"(ExpertBook [A-Za-z0-9 ]+)",
                r"(ThinkPad [A-Za-z0-9 ]+)",
                r"(IdeaPad [A-Za-z0-9 ]+)",
                r"(Legion [A-Za-z0-9 ]+)",
                r"(Yoga [A-Za-z0-9 ]+)",
                r"(LOQ [A-Za-z0-9 ]+)",
                r"(Spectre [A-Za-z0-9 ]+)",
                r"(Envy [A-Za-z0-9 ]+)",
                r"(Pavilion [A-Za-z0-9 ]+)",
                r"(Omen [A-Za-z0-9 ]+)",
                r"(Victus [A-Za-z0-9 ]+)",
                r"(XPS \d+)",
                r"(Inspiron [A-Za-z0-9 ]+)",
                r"(Latitude [A-Za-z0-9 ]+)",
                r"(Alienware [A-Za-z0-9 ]+)",
                r"(Acer Aspire [A-Za-z0-9 ]+)",
                r"(Aspire [A-Za-z0-9 ]+)",
                r"(Predator [A-Za-z0-9 ]+)",
                r"(Nitro \d+)",
                r"(Swift [A-Za-z0-9 ]+)",
                r"(MSI [A-Za-z0-9 ]+)",
                r"(Katana [A-Za-z0-9 ]+)",
                r"(Cyborg [A-Za-z0-9 ]+)",
                r"(Modern [A-Za-z0-9 ]+)",
                r"(Thin \d+ [A-Za-z0-9 ]+)",
                r"(Galaxy Book[A-Za-z0-9 ]*)",
                r"(MacBook (?:Pro|Air) [A-Za-z0-9 ]+)",
                r"(Chromebook [A-Za-z0-9 ]*)"
            ]
        )

    model = remove_trademarks(model)

    # Extract model number / SKU
    model_number = None
    # Check title right after spec parenthesis: e.g. - (8 GB/...) AL15-41
    if title:
        mn_title = re.search(r"\)\s*([A-Za-z0-9]+(?:-[A-Za-z0-9]+)?)\b", title)
        if mn_title:
            cand_mn = mn_title.group(1).strip()
            if not any(cand_mn.lower() == w for w in ["notebook", "laptop", "thin", "light", "gaming", "chromebook", "with"]):
                model_number = cand_mn

    if not model_number:
        mn_match = re.search(r"\b([A-Z]{2,4}\d{3,4}[A-Z]{1,4})\b", text)
        if mn_match:
            model_number = mn_match.group(1)
        elif product.get("sku") and not str(product.get("sku")).isdigit():
            model_number = str(product.get("sku"))
        else:
            mn_fallback = first_match(
                text,
                [
                    r"\bModel\s*[:\n]\s*([A-Za-z0-9\-]+)\b",
                    r"\bPart Number\s*[:\n]\s*([A-Za-z0-9\-]+)\b",
                    r"\bSKU\s*[:\n]\s*([A-Za-z0-9\-]+)\b"
                ]
            )
            if mn_fallback:
                model_number = mn_fallback
            elif product.get("sku"):
                model_number = str(product.get("sku"))

    # Extract Series
    series = None
    if model:
        for s in ["TUF Gaming", "ROG", "Zenbook", "Vivobook", "ExpertBook", "ProArt",
                  "ThinkPad", "IdeaPad", "Legion", "Yoga", "LOQ",
                  "Spectre", "Envy", "Pavilion", "Omen", "Victus",
                  "XPS", "Inspiron", "Latitude", "Vostro", "Alienware",
                  "Predator", "Nitro", "Swift", "Aspire",
                  "MacBook Air", "MacBook Pro", "Galaxy Book", "Gram"]:
            if re.search(rf"\b{re.escape(s)}\b", model, re.IGNORECASE):
                series = s
                break

    # Release Year
    release_year = number_match(
        text,
        [
            r"\b(202[0-7])\b"
        ]
    )
    if release_year is not None:
        release_year = int(release_year)

    return model, model_number, series, release_year


# ==============================================================================
# CPU EXTRACTION & NORMALIZATION
# ==============================================================================

def extract_cpu(text):
    raw_cpu = first_match(
        text,
        [
            # Intel Core Ultra
            r"(Intel[®™]?\s+Core[™®]?\s+Ultra\s+[3579]\s+\d{3}[A-Za-z]*)",
            r"(Core[™®]?\s+Ultra\s+[3579]\s+\d{3}[A-Za-z]*)",
            # Intel Core 3/5/7/9 (e.g. Core 5 210H, Core 3 13th Gen 1315U, Core 3-100U)
            r"(Intel[®™]?\s+Core[™®]?\s+i?[3579]\s+(?:(?:\d+th\s+Gen|\d+th\s+gen|gen)\s+)?\d{3,5}[A-Za-z]*)",
            r"(Core[™®]?\s+i?[3579]\s+(?:(?:\d+th\s+Gen|\d+th\s+gen|gen)\s+)?\d{3,5}[A-Za-z]*)",
            # Intel Core i3/i5/i7/i9 (including dashes)
            r"(Intel[®™]?\s+Core[™®]?\s+i[3579][\-\s]\d{3,5}[A-Za-z]*)",
            r"(Core[™®]?\s+i[3579][\-\s]\d{3,5}[A-Za-z]*)",
            # Intel Celeron
            r"(Intel[®™]?\s+Celeron[®™]?\s+(?:Dual\s+Core|Quad\s+Core)?\s*[A-Za-z0-9]*)",
            # AMD Ryzen AI Max / HX / Strix / Granite
            r"(AMD Ryzen[™®]?\s+AI\s+Max\+?\s+\d+)",
            r"(AMD Ryzen[™®]?\s+AI\s+\d+\s+HX\s+\d+)",
            r"(AMD Ryzen[™®]?\s+AI\s+[A-Za-z0-9+\- ]+)",
            r"(AMD Ryzen[™®]?\s+[3579]\s+(?:Quad\s+Core|Hexa\s+Core|Octa\s+Core)?\s*\d{4}[A-Za-z]*)",
            r"(AMD Ryzen[™®]?\s+[3579]\s+\d{4}[A-Za-z]*)",
            r"(Ryzen[™®]?\s+[3579]\s+\d{4}[A-Za-z]*)",
            r"(AMD Ryzen[™®]?\s+[3579]\s+(?:Quad|Hexa|Octa)?\s*Core(?:\s+Processor)?)",
            r"(AMD Ryzen[™®]?\s+[3579]\s+Processor)",
            r"(AMD Ryzen[™®]?\s+[3579])",
            r"(Ryzen[™®]?\s+[3579]\s+(?:Quad|Hexa|Octa)?\s*Core)",
            r"(Ryzen[™®]?\s+[3579])",
            # Intel Core general (with or without generation / code)
            r"(Intel[®™]?\s+Core[™®]?\s+i?[3579]\s+(?:Processor\s+)?(?:\(?\d+th\s+Gen\)?|\d+th\s+gen|gen)?)",
            r"(Core[™®]?\s+i?[3579]\s+(?:Processor\s+)?(?:\(?\d+th\s+Gen\)?|\d+th\s+gen|gen)?)",
            # Qualcomm Snapdragon X
            r"(Snapdragon[®™]?\s+X2?\s+Elite\s+[A-Za-z0-9\- ]+)",
            r"(Snapdragon[®™]?\s+X2?\s+Plus\s+[A-Za-z0-9\- ]+)",
            r"(Snapdragon[®™]?\s+X\s+[A-Za-z0-9\- ]+)",
            # MediaTek
            r"(MediaTek\s+Kompanio\s+\d+)",
            r"(MediaTek\s+[A-Za-z0-9 ]+)",
            # Apple M Series
            r"(Apple\s+M[1234]\s+(?:Max|Pro|Ultra)?)",
            r"\b(M[1234]\s+(?:Max|Pro|Ultra)?)\s+chip\b"
        ]
    )

    clean_cpu = remove_trademarks(raw_cpu)

    cpu_brand = None
    cpu_model = None
    cpu_family = None
    cpu_generation = None

    if clean_cpu:
        # Determine CPU Brand
        if "AMD" in clean_cpu or "Ryzen" in clean_cpu:
            cpu_brand = "AMD"
            # Strip redundant AMD prefix for model name if already in brand
            cpu_model = clean_cpu.replace("AMD ", "").strip()
            if "Ryzen AI Max" in clean_cpu:
                cpu_family = "Ryzen AI Max"
            elif "Ryzen AI 9" in clean_cpu:
                cpu_family = "Ryzen AI 9"
            elif "Ryzen AI" in clean_cpu:
                cpu_family = "Ryzen AI"
            elif "Ryzen 9" in clean_cpu:
                cpu_family = "Ryzen 9"
            elif "Ryzen 7" in clean_cpu:
                cpu_family = "Ryzen 7"
            elif "Ryzen 5" in clean_cpu:
                cpu_family = "Ryzen 5"
            elif "Ryzen 3" in clean_cpu:
                cpu_family = "Ryzen 3"

            gen_m = re.search(r"(\d)\d{3}[A-Z]*", clean_cpu)
            if gen_m:
                cpu_generation = int(gen_m.group(1))

        elif "Intel" in clean_cpu or "Core" in clean_cpu:
            cpu_brand = "Intel"
            cpu_model = clean_cpu.replace("Intel ", "").strip()
            if "Core Ultra 9" in clean_cpu:
                cpu_family = "Core Ultra 9"
                cpu_generation = 2 if re.search(r"\b2\d\d[VvKkHh]\b", clean_cpu) else 1
            elif "Core Ultra 7" in clean_cpu:
                cpu_family = "Core Ultra 7"
                cpu_generation = 2 if re.search(r"\b2\d\d[VvKkHh]\b", clean_cpu) else 1
            elif "Core Ultra 5" in clean_cpu:
                cpu_family = "Core Ultra 5"
                cpu_generation = 2 if re.search(r"\b2\d\d[VvKkHh]\b", clean_cpu) else 1
            elif "Core Ultra" in clean_cpu:
                cpu_family = "Core Ultra"
            elif "Core i9" in clean_cpu or "i9-" in clean_cpu:
                cpu_family = "Core i9"
            elif "Core i7" in clean_cpu or "i7-" in clean_cpu:
                cpu_family = "Core i7"
            elif "Core i5" in clean_cpu or "i5-" in clean_cpu:
                cpu_family = "Core i5"
            elif "Core i3" in clean_cpu or "i3-" in clean_cpu:
                cpu_family = "Core i3"

            if cpu_generation is None:
                gen_m = re.search(r"(\d{2})\d{3}[A-Z]*", clean_cpu)
                if gen_m:
                    cpu_generation = int(gen_m.group(1))

        elif "Snapdragon" in clean_cpu:
            cpu_brand = "Qualcomm"
            cpu_model = clean_cpu
            cpu_family = "Snapdragon X"

        elif "Apple" in clean_cpu or re.match(r"^M[1-4]", clean_cpu):
            cpu_brand = "Apple"
            cpu_model = clean_cpu
            m_gen = re.search(r"M(\d)", clean_cpu)
            if m_gen:
                cpu_generation = int(m_gen.group(1))
                cpu_family = f"Apple M{cpu_generation}"

        elif "MediaTek" in clean_cpu:
            cpu_brand = "MediaTek"
            cpu_model = clean_cpu.replace("MediaTek ", "").strip()
            cpu_family = "Kompanio"

    # CPU Cores
    cpu_cores = number_match(
        text,
        [
            r"(\d+)-core\s+Zen\s+5",
            r"(\d+)\s+Cores",
            r"(\d+)\s*cores",
            r"(\d+)\s*Cores\s*/\s*\d+\s*Threads",
            r"(\d+)\s*Cores,\s*\d+\s*Threads"
        ]
    )

    # CPU Threads
    cpu_threads = number_match(
        text,
        [
            r"(\d+)\s+Threads",
            r"(\d+)\s*threads",
            r"\d+\s*Cores\s*/\s*(\d+)\s*Threads",
            r"\d+\s*Cores,\s*(\d+)\s*Threads"
        ]
    )

    # Clocks
    base_clock = number_match(
        text,
        [
            r"Base\s+Clock[:\s]+([\d.]+)\s*GHz",
            r"Base\s+Frequency[:\s]+([\d.]+)\s*GHz"
        ]
    )
    boost_clock = number_match(
        text,
        [
            r"(?:Boost\s+Clock|Max\s+Boost\s+Clock|Turbo\s+Boost)[:\s]+([\d.]+)\s*GHz",
            r"up to\s+([\d.]+)\s*GHz"
        ]
    )

    return {
        "cpu_brand": cpu_brand,
        "cpu_model": cpu_model,
        "cpu_family": cpu_family,
        "cpu_generation": cpu_generation,
        "cpu_cores": int(cpu_cores) if cpu_cores is not None else None,
        "cpu_threads": int(cpu_threads) if cpu_threads is not None else None,
        "cpu_base_clock_ghz": base_clock,
        "cpu_boost_clock_ghz": boost_clock,
    }


# ==============================================================================
# GPU EXTRACTION & NORMALIZATION
# ==============================================================================

def extract_gpu(text):
    raw_gpu = first_match(
        text,
        [
            # AMD Radeon APU / discrete models
            r"(AMD Radeon[™®]?\s+8060S)",
            r"(Radeon[™®]?\s+8060S)",
            r"(AMD Radeon[™®]?\s+\d{3}M)",
            r"(AMD Radeon[™®]?\s+RX\s+\d{4}[A-Za-z]*)",
            # NVIDIA RTX
            r"(NVIDIA[®™]?\s+GeForce\s+RTX[™®]?\s+\d{4}(?:\s+Ti)?(?:\s+Laptop\s+GPU)?)",
            r"(GeForce\s+RTX[™®]?\s+\d{4}(?:\s+Ti)?(?:\s+Laptop\s+GPU)?)",
            r"(RTX[™®]?\s+\d{4}(?:\s+Ti)?(?:\s+Laptop\s+GPU)?)",
            # General AMD
            r"(AMD Radeon[™®]?\s+Graphics)",
            r"(Radeon[™®]?\s+[A-Za-z0-9 ]+Graphics)",
            # Intel Arc & Iris
            r"(Intel[®™]?\s+Arc[™®]?\s+[A-Za-z0-9]+(?:\s+Graphics)?)",
            r"(Intel[®™]?\s+Iris[®™]?\s+X[eé]\s+Graphics)",
            r"(Intel[®™]?\s+Graphics)",
            # Qualcomm Adreno
            r"(Qualcomm[®™]?\s+Adreno[™®]?\s+[A-Za-z0-9]+(?:\s+GPU)?)",
            r"(Qualcomm[®™]?\s+Adreno[™®]?\s+GPU)",
            r"(Adreno[™®]?\s+[A-Za-z0-9]+(?:\s+GPU)?)",
            r"(Adreno[™®]?\s+GPU)",
            # Apple GPU
            r"(Apple\s+\d+-core\s+GPU)",
            r"(\d+-core\s+Apple\s+GPU)"
        ]
    )

    clean_gpu = remove_trademarks(raw_gpu)
    if clean_gpu and clean_gpu.startswith("Radeon"):
        clean_gpu = "AMD " + clean_gpu

    gpu_brand = None
    gpu_model = clean_gpu
    gpu_type = None

    if clean_gpu:
        if "NVIDIA" in clean_gpu or "GeForce" in clean_gpu or "RTX" in clean_gpu:
            gpu_brand = "NVIDIA"
            gpu_type = "Discrete"
        elif "AMD" in clean_gpu or "Radeon" in clean_gpu:
            gpu_brand = "AMD"
            if re.search(r"RX\s+\d{4}", clean_gpu):
                gpu_type = "Discrete"
            else:
                gpu_type = "Integrated"
        elif "Intel" in clean_gpu or "Arc" in clean_gpu or "Iris" in clean_gpu:
            gpu_brand = "Intel"
            if re.search(r"Arc\s+A\d{3}M", clean_gpu):
                gpu_type = "Discrete"
            else:
                gpu_type = "Integrated"
        elif "Qualcomm" in clean_gpu or "Adreno" in clean_gpu:
            gpu_brand = "Qualcomm"
            gpu_type = "Integrated"
        elif "Apple" in clean_gpu:
            gpu_brand = "Apple"
            gpu_type = "Integrated"

    # GPU VRAM (extract only when explicitly stated)
    gpu_vram = number_match(
        text,
        [
            r"(\d+)\s*GB\s+(?:GDDR[567]|VRAM)",
            r"(\d+)\s*GB\s+dedicated",
            r"VRAM[:\s]+(\d+)\s*GB"
        ]
    )

    # GPU Memory Type
    gpu_mem_type = None
    if re.search(r"unified memory architecture|unified memory", text, re.IGNORECASE):
        gpu_mem_type = "Unified Memory"
    else:
        mem_match = re.search(r"\b(GDDR[567]X?)\b", text, re.IGNORECASE)
        if mem_match:
            gpu_mem_type = mem_match.group(1).upper()

    # GPU TGP in Watts
    gpu_tgp = number_match(
        text,
        [
            r"(\d+)\s*W\s+TGP",
            r"TGP[:\s]+(\d+)\s*W",
            r"up to\s+(\d+)\s*W\s+(?:with\s+Dynamic\s+Boost|TGP)"
        ]
    )

    return {
        "gpu_brand": gpu_brand,
        "gpu_model": gpu_model,
        "gpu_type": gpu_type,
        "gpu_vram_gb": int(gpu_vram) if gpu_vram is not None else None,
        "gpu_memory_type": gpu_mem_type,
        "gpu_tgp_w": int(gpu_tgp) if gpu_tgp is not None else None,
    }


# ==============================================================================
# NPU EXTRACTION
# ==============================================================================

def extract_npu(text):
    npu_tops = number_match(
        text,
        [
            r"(\d+)\s*TOP[Ss]\s+for\s+AMD\s+Ryzen\s+AI",
            r"(\d+)\s*TOPS\s+for\s+AMD\s+Ryzen\s+AI",
            r"provides up to\s*(\d+)\s*TOPS",
            r"up to\s*(\d+)\s*TOPS",
            r"(\d+)\s*TOPS\s+NPU",
            r"(\d+)\s*NPU\s*TOPS"
        ]
    )

    npu = None
    if re.search(r"XDNA\s*2", text, re.IGNORECASE):
        npu = "AMD XDNA 2"
    elif re.search(r"XDNA", text, re.IGNORECASE):
        npu = "AMD XDNA"
    elif re.search(r"Hexagon\s*NPU", text, re.IGNORECASE):
        npu = "Qualcomm Hexagon NPU"
    elif re.search(r"Intel\s*AI\s*Boost", text, re.IGNORECASE):
        npu = "Intel AI Boost"
    elif re.search(r"Apple\s*Neural\s*Engine", text, re.IGNORECASE):
        npu = "Apple Neural Engine"

    return {
        "npu": npu,
        "npu_tops": int(npu_tops) if npu_tops is not None else None
    }


# ==============================================================================
# RAM EXTRACTION & NORMALIZATION (PHASE 4 & 7)
# ==============================================================================

def extract_ram(text):
    # CRITICAL: Distinguish ACTUAL configured RAM from "UP TO" marketing text!
    # Actual configuration patterns:
    actual_ram = number_match(
        text,
        [
            r"(?:Installed|Configured|Stock configuration|Memory|RAM)[:\s]+(\d+)\s*GB",
            r"\b(\d+)\s*GB\s+(?:LPDDR[45]X?|DDR[45])\s+on\s+board",
            r"\b(\d+)\s*GB\s+on\s+board",
            r"\b(\d+)\s*GB\s+(?:LPDDR[45]X?|DDR[45])\s+memory",
            r"(?:Up to\s+)?(\d+)GB\s*of\s+ultra-high\s+speed\s+LPDDR5X",
            r"Up to\s+(\d+)GB.*?LPDDR5X",
            r"(\d+)GB.*?LPDDR5X",
            r"\b(\d+)\s*GB\s+RAM\b",
            r"\b(\d+)\s*GB\s+Unified\s+Memory\b",
            r"(\d{5})\s*MB\s+RAM"  # 16384 MB
        ]
    )

    # If MB match
    if actual_ram and actual_ram > 1000:
        actual_ram = round(actual_ram / 1024)

    # Sanity check: laptop RAM must be between 4 and 128 GB
    if actual_ram and (actual_ram > 128 or actual_ram < 4):
        actual_ram = None

    # Fallback only if no explicit actual RAM, but check if "Up to" is present
    if actual_ram is None:
        # Check if there is an unambiguous RAM listing without "up to"
        m = re.search(r"(?<!up to\s)(?<!up to )(?<!Up to\s)(?<!Up to )(\d+)\s*GB\s*(?:LPDDR[45]X?|DDR[45])", text, re.IGNORECASE)
        if m:
            try:
                actual_ram = float(m.group(1))
            except ValueError:
                pass

    # RAM Type
    ram_type = first_match(
        text,
        [
            r"\b(LPDDR5X)\b",
            r"\b(LPDDR5)\b",
            r"\b(LPDDR4X)\b",
            r"\b(LPDDR4)\b",
            r"\b(DDR5)\b",
            r"\b(DDR4)\b",
            r"\b(Unified Memory)\b"
        ]
    )

    # RAM Speed in MHz / MT/s
    ram_speed = number_match(
        text,
        [
            r"(?:LPDDR5X|LPDDR5|DDR5|DDR4)\s*[-–—\s]\s*(\d{4,5})\s*(?:MT/s|MHz)",
            r"(\d{4,5})\s*MT/s",
            r"(\d{4,5})\s*MHz\s+(?:memory|RAM)"
        ]
    )

    # RAM upgradeability and slots
    ram_upgradeable = None
    if re.search(r"on board|soldered", text, re.IGNORECASE):
        if not re.search(r"SO-DIMM slot|expandable up to", text, re.IGNORECASE):
            ram_upgradeable = False
        else:
            ram_upgradeable = True
    elif re.search(r"SO-DIMM|upgradable memory|upgradeable memory", text, re.IGNORECASE):
        ram_upgradeable = True

    ram_slots = None
    slots_m = re.search(r"(\d+)\s*x\s*SO-DIMM", text, re.IGNORECASE)
    if slots_m:
        ram_slots = int(slots_m.group(1))

    return {
        "ram_gb": int(actual_ram) if actual_ram is not None else None,
        "ram_type": ram_type.upper() if ram_type else None,
        "ram_speed_mhz": int(ram_speed) if ram_speed is not None else None,
        "ram_upgradeable": ram_upgradeable,
        "ram_slots": ram_slots
    }


# ==============================================================================
# STORAGE EXTRACTION & NORMALIZATION (PHASE 4 & 8)
# ==============================================================================

def extract_storage(text):
    # Type & Interface
    storage_type = first_match(
        text,
        [
            r"(NVMe[™®]?\s+SSD)",
            r"(M\.2\s+NVMe[™®]?\s+PCIe[™®]?\s+4\.0\s+SSD)",
            r"(M\.2\s+2280\s+NVMe[™®]?\s+SSD)",
            r"(PCIe[®™]?\s+4\.0\s+SSD)",
            r"(PCIe[®™]?\s+SSD)",
            r"(SATA\s+SSD)",
            r"(eMMC\s+Storage|eMMC)",
            r"(EMMC\s+Storage|EMMC)",
            r"(HDD)",
            r"(Hard Disk)"
        ]
    )
    if storage_type:
        storage_type = remove_trademarks(storage_type)

    storage_interface = None
    if re.search(r"PCIe[®™]?\s*4\.0", text, re.IGNORECASE):
        storage_interface = "PCIe 4.0 NVMe"
    elif re.search(r"PCIe[®™]?\s*5\.0", text, re.IGNORECASE):
        storage_interface = "PCIe 5.0 NVMe"
    elif re.search(r"PCIe[®™]?\s*3\.0", text, re.IGNORECASE):
        storage_interface = "PCIe 3.0 NVMe"
    elif re.search(r"SATA", text, re.IGNORECASE):
        storage_interface = "SATA III"

    # Actual Storage in GB
    storage_gb = None
    actual_tb = number_match(
        text,
        [
            r"(?:Stock configuration|Installed|Internal)[:\s]+(\d+)\s*TB",
            r"Stock configuration.*?(\d+)\s*TB",
            r"(?<!up to\s)(?<!up to )(?<!Up to\s)(?<!Up to )\b(\d+)\s*TB\s+(?:M\.2\s+NVMe|PCIe|SSD|HDD|Storage|Hard Disk)\b",
            r"\b(\d+)\s*TB\s*(?:SSD|HDD|Hard Disk)\b"
        ]
    )
    if actual_tb is not None:
        storage_gb = int(actual_tb * 1024)
    else:
        actual_gb = number_match(
            text,
            [
                r"(?:Stock configuration|Installed|Internal)[:\s]+(\d+)\s*GB",
                r"(?<!up to\s)(?<!up to )(?<!Up to\s)(?<!Up to )\b(32|64|128|256|512|1024|2048)\s*GB\s*(?:M\.2|NVMe|PCIe|SSD|eMMC|EMMC|HDD|Storage|ROM)",
                r"\b(32|64|128|256|512|1024|2048)\s*GB\s*(?:SSD|eMMC|EMMC|HDD)\b"
            ]
        )
        if actual_gb is not None:
            storage_gb = int(actual_gb)

    # Expandable Storage (Phase 4 requirement: store max_expandable_storage_tb)
    max_expandable_tb = number_match(
        text,
        [
            r"up to\s+(\d+(?:\.\d+)?)\s*TB\s+of extendable",
            r"Up to\s+(\d+(?:\.\d+)?)\s*TB.*?Extendable SSD",
            r"expandable up to\s+(\d+(?:\.\d+)?)\s*TB",
            r"up to\s+(\d+(?:\.\d+)?)\s*TB\s+SSD"
        ]
    )

    ssd_slots = None
    slot_match = re.search(r"(\d+)\s*(?:x\s*M\.2\s+slot|SSD\s+Slots)", text, re.IGNORECASE)
    if slot_match:
        ssd_slots = int(slot_match.group(1))

    storage_upgradeable = True if (max_expandable_tb is not None or ssd_slots is not None and ssd_slots > 1) else None

    return {
        "storage_type": storage_type,
        "storage_gb": storage_gb,
        "storage_interface": storage_interface,
        "ssd_slots": ssd_slots,
        "storage_upgradeable": storage_upgradeable,
        "max_expandable_storage_tb": float(max_expandable_tb) if max_expandable_tb is not None else None
    }


# ==============================================================================
# DISPLAY EXTRACTION & NORMALIZATION (PHASE 9)
# ==============================================================================

def extract_display(text):
    screen_size = number_match(
        text,
        [
            r"\d+(?:\.\d+)?\s*cm\s*\(\s*(\d+(?:\.\d+)?)(?:-inch|\"|)\s*\)",
            r"(\d+(?:\.\d+)?)-inch chassis",
            r"(\d+(?:\.\d+)?)-inch gaming laptop",
            r"(\d+(?:\.\d+)?)-inch",
            r"(\d+(?:\.\d+)?)\s*inch",
            r"\b(\d+(?:\.\d+)?)\"\s+(?:FHD|QHD|OLED|display)"
        ]
    )

    # Resolution
    res_width = None
    res_height = None
    resolution = None
    aspect_ratio = None

    res_match = re.search(r"\b(\d{3,5})\s*[xX*×]\s*(\d{3,5})\b", text)
    if res_match:
        res_width = int(res_match.group(1))
        res_height = int(res_match.group(2))
        resolution = f"{res_width}x{res_height}"

        # Calculate or lookup aspect ratio
        if res_width and res_height:
            ratio_val = res_width / res_height
            if abs(ratio_val - 16 / 9) < 0.05:
                aspect_ratio = "16:9"
            elif abs(ratio_val - 16 / 10) < 0.05:
                aspect_ratio = "16:10"
            elif abs(ratio_val - 3 / 2) < 0.05:
                aspect_ratio = "3:2"
            elif abs(ratio_val - 4 / 3) < 0.05:
                aspect_ratio = "4:3"

    # Panel Type
    panel_type = None
    if re.search(r"\bOLED\b", text, re.IGNORECASE):
        panel_type = "OLED"
    elif re.search(r"\bIPS\b", text, re.IGNORECASE):
        panel_type = "IPS"
    elif re.search(r"Mini[\-\s]LED\s+(?:display|screen|panel)", text, re.IGNORECASE):
        panel_type = "Mini-LED"
    elif re.search(r"\bTN\b", text):
        panel_type = "TN"

    # Refresh Rate
    refresh_rate = number_match(
        text,
        [
            r"(\d+)\s*Hz\s+Refresh Rate",
            r"Refresh Rate[:\s]*(\d+)\s*Hz",
            r"(\d+)\s*Hz\s+display",
            r"(\d+)\s*Hz\b"
        ]
    )

    # Response Time
    response_time = number_match(
        text,
        [
            r"(\d+(?:\.\d+)?)\s*ms\s+Response time",
            r"(\d+(?:\.\d+)?)\s*ms\s+response"
        ]
    )

    # Color Gamut
    color_gamut = first_match(
        text,
        [
            r"(\d+%\s+sRGB)",
            r"(\d+%\s+DCI-P3)",
            r"(\d+%\s+Adobe RGB)",
            r"(\d+%\s+NTSC)"
        ]
    )

    # Brightness in nits
    brightness_nits = number_match(
        text,
        [
            r"(\d+)\s*nits",
            r"peak brightness\s*(\d+)\s*nits",
            r"(\d+)\s*cd/m²"
        ]
    )

    # Touchscreen
    touchscreen = None
    if re.search(r"touchscreen|touch display|multi-touch", text, re.IGNORECASE):
        touchscreen = True
    elif re.search(r"non-touch", text, re.IGNORECASE):
        touchscreen = False

    # Screen finish
    screen_finish = None
    if re.search(r"Anti-glare|anti-reflective|matte", text, re.IGNORECASE):
        screen_finish = "Anti-glare"
    elif re.search(r"Glossy|glare", text, re.IGNORECASE):
        screen_finish = "Glossy"

    return {
        "display_size_inches": screen_size,
        "resolution_width": res_width,
        "resolution_height": res_height,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "panel_type": panel_type,
        "refresh_rate_hz": int(refresh_rate) if refresh_rate is not None else None,
        "response_time_ms": int(response_time) if response_time is not None else None,
        "color_gamut": color_gamut,
        "brightness_nits": brightness_nits,
        "touchscreen": touchscreen,
        "screen_finish": screen_finish,
    }


# ==============================================================================
# PHYSICAL & BUILD QUALITY (PHASE 10)
# ==============================================================================

def extract_physical(text):
    battery_wh = number_match(
        text,
        [
            r"(\d+(?:\.\d+)?)\s*Wh\s+Battery",
            r"(\d+(?:\.\d+)?)\s*Wh\s+battery",
            r"(\d+(?:\.\d+)?)\s*Whr"
        ]
    )

    weight_kg = number_match(
        text,
        [
            r"(\d+\.\d+)\s*kg",
            r"Weight[:\s]+(\d+(?:\.\d+)?)\s*kg"
        ]
    )

    build_quality = None
    if re.search(r"MIL-STD-810H", text, re.IGNORECASE):
        build_quality = "MIL-STD-810H"
    elif re.search(r"MIL-STD-810G", text, re.IGNORECASE):
        build_quality = "MIL-STD-810G"

    has_aluminum_lid = bool(re.search(r"aluminum lid", text, re.IGNORECASE))
    has_aluminum_bottom = bool(re.search(r"aluminum underside", text, re.IGNORECASE))

    build_material = None
    if has_aluminum_lid and has_aluminum_bottom:
        build_material = "Aluminum lid and underside"
    elif has_aluminum_lid:
        build_material = "Aluminum lid"
    elif has_aluminum_bottom:
        build_material = "Aluminum underside"
    elif re.search(r"magnesium[- ]aluminum alloy", text, re.IGNORECASE):
        build_material = "Magnesium-aluminum alloy"
    elif re.search(r"magnesium alloy", text, re.IGNORECASE):
        build_material = "Magnesium alloy"
    elif re.search(r"aluminum\s+(?:body|chassis|unibody)", text, re.IGNORECASE):
        build_material = "Aluminum chassis"

    return {
        "battery_wh": battery_wh,
        "weight_kg": weight_kg,
        "build_material": build_material,
        "build_quality": build_quality
    }


# ==============================================================================
# SECURITY (PHASE 11)
# ==============================================================================

def extract_security(text):
    fingerprint = bool(re.search(r"fingerprint\s+(?:sensor|reader|scanner)|Windows\s+Hello\s+fingerprint", text, re.IGNORECASE))

    # Face unlock must specifically be IR camera or Windows Hello face recognition
    face_unlock = bool(re.search(r"IR\s+camera|Windows\s+Hello\s+face|facial\s+recognition", text, re.IGNORECASE))

    return {
        "fingerprint": fingerprint,
        "face_unlock": face_unlock
    }


# ==============================================================================
# OPERATING SYSTEM (PHASE 12)
# ==============================================================================

def extract_os(text):
    operating_system = first_match(
        text,
        [
            r"(Windows\s+11\s+Home(?:\s+Single\s+Language)?)",
            r"(Windows\s+11\s+Pro)",
            r"(Windows\s+11)",
            r"(Windows\s+10\s+Home)",
            r"(Windows\s+10\s+Pro)",
            r"(Windows\s+10)",
            r"(macOS\s+[A-Za-z]+)",
            r"(macOS)",
            r"(Ubuntu\s+Linux)",
            r"(Linux)",
            r"(FreeDOS|DOS)",
            r"(No\s+OS)"
        ]
    )

    windows_included = False
    if operating_system and "Windows" in operating_system:
        windows_included = True

    return {
        "operating_system": operating_system,
        "windows_included": windows_included
    }


# ==============================================================================
# CONNECTIVITY, PORTS, KEYBOARD & PERIPHERALS
# ==============================================================================

def extract_peripherals(text):
    wifi = first_match(
        text,
        [
            r"(WiFi\s+\d+[A-Za-z]*)",
            r"(Wi-Fi\s+\d+[A-Za-z]*)"
        ]
    )

    bluetooth = first_match(
        text,
        [
            r"(Bluetooth\s+\d+(?:\.\d+)?)"
        ]
    )

    webcam = first_match(
        text,
        [
            r"(FHD\s+IR\s+camera)",
            r"(FHD\s+camera)",
            r"(1080p\s+FHD\s+camera)",
            r"(720p\s+HD\s+camera)",
            r"(HD\s+camera)"
        ]
    )

    # Ports
    ports = []
    port_patterns = [
        r"\d+\s*x\s*HDMI\s*[0-9.]*",
        r"\d+\s*x\s*Thunderbolt[™®]?\s*\d*",
        r"\d+\s*x\s*USB4[™®]?",
        r"\d+\s*x\s*USB3\.2[^ ]*",
        r"\d+\s*x\s*USB3\.2\s+Type-C",
        r"\d+\s*x\s*USB3\.2\s+Gen2\s+Type\s+A",
        r"\d+\s*x\s*Audio jack",
        r"\d+\s*x\s*Card reader",
        r"\d+\s*x\s*RJ45",
        r"\d+\s*x\s*Ethernet"
    ]
    for pattern in port_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cleaned_port = clean(remove_trademarks(match))
            if cleaned_port not in ports:
                ports.append(cleaned_port)

    keyboard_backlight = first_match(
        text,
        [
            r"(Mini-LED Backlight Keyboard)",
            r"(RGB Backlight Keyboard)",
            r"(Backlit Keyboard)",
            r"(Per-Key RGB)",
            r"(4-Zone RGB)"
        ]
    )

    keyboard_type = first_match(
        text,
        [
            r"(Chiclet Keyboard)",
            r"(Mechanical Keyboard)",
            r"(Membrane Keyboard)"
        ]
    )

    speakers = first_match(
        text,
        [
            r"(Dolby Atmos)",
            r"(Harman Kardon)",
            r"(Waves MaxxAudio)",
            r"(Bang & Olufsen)"
        ]
    )

    sd_card_reader = bool(re.search(r"SD card reader|microSD card reader|Card reader", text, re.IGNORECASE))
    thunderbolt = bool(re.search(r"Thunderbolt", text, re.IGNORECASE))
    usb4 = bool(re.search(r"USB4", text, re.IGNORECASE))

    warranty = number_match(
        text,
        [
            r"(\d+)\s*Year\s+Warranty",
            r"(\d+)\s*year\s+warranty"
        ]
    )

    return {
        "wifi": wifi,
        "bluetooth": bluetooth,
        "webcam": webcam,
        "ports": ports,
        "keyboard_backlight": keyboard_backlight,
        "keyboard_type": keyboard_type,
        "speakers": speakers,
        "sd_card_reader": sd_card_reader,
        "thunderbolt": thunderbolt,
        "usb4": usb4,
        "warranty_years": int(warranty) if warranty is not None else None
    }


# ==============================================================================
# PRICE EXTRACTION
# ==============================================================================

def extract_price(text, product_json=None):
    current_price = None
    original_price = None
    discount = None

    # ASUS multi-price pattern:
    # ₹239,990.00
    # ₹323,990.00
    # SAVE ₹84,000.00
    match = re.search(
        r"₹\s*([\d,]+(?:\.\d+)?)\s*"
        r"₹\s*([\d,]+(?:\.\d+)?)\s*"
        r"SAVE\s*₹\s*([\d,]+(?:\.\d+)?)",
        text,
        re.IGNORECASE
    )
    if match:
        current_price = float(match.group(1).replace(",", ""))
        original_price = float(match.group(2).replace(",", ""))
        discount = float(match.group(3).replace(",", ""))
    else:
        # Retailer discount pattern (e.g. Flipkart: ₹70,990 ₹ 89,990 21% off)
        fk_m = re.search(r"₹\s*([\d,]+(?:\.\d+)?)\s*₹\s*([\d,]+(?:\.\d+)?)\s*(\d+)%\s*off", text, re.IGNORECASE)
        if fk_m:
            current_price = float(fk_m.group(1).replace(",", ""))
            original_price = float(fk_m.group(2).replace(",", ""))
            discount = round(float(original_price - current_price), 2)
        else:
            # Check JSON-LD offers
            if product_json and isinstance(product_json, dict):
                offers = product_json.get("offers")
                if isinstance(offers, dict):
                    p = offers.get("price")
                    if p:
                        try:
                            current_price = float(p)
                        except ValueError:
                            pass
                elif isinstance(offers, list) and offers:
                    p = offers[0].get("price")
                    if p:
                        try:
                            current_price = float(p)
                        except ValueError:
                            pass

        if current_price is None:
            # Fallback for single price with prefix
            match = re.search(
                r"(?:Starting at|Price|MRP|M\.R\.P\.)"
                r".{0,100}?"
                r"₹\s*([\d,]+(?:\.\d+)?)",
                text,
                re.IGNORECASE
            )
            if match:
                current_price = float(match.group(1).replace(",", ""))
            else:
                # Standalone rupee price in retail cards (e.g. ₹1,54,598 or ₹74,990)
                for m in re.finditer(r"₹\s*([\d,]{4,10}(?:\.\d{2})?)", text):
                    cand_str = m.group(1).replace(",", "")
                    try:
                        cand_val = float(cand_str)
                        if 10000 <= cand_val <= 1000000:
                            current_price = cand_val
                            break
                    except ValueError:
                        pass

    return {
        "current": current_price,
        "original": original_price,
        "discount": discount
    }


# ==============================================================================
# MAIN PARSER ENTRYPOINT (PHASE 3 FINAL SCHEMA)
# ==============================================================================

def parse_html(html, url, website):
    soup = BeautifulSoup(html, "lxml")
    text = extract_text(html)
    title = clean(soup.title.string) if soup.title else ""
    if not title:
        title_el = soup.find(class_=lambda c: c and any(k in str(c) for k in ["KzDlHZ", "_4rR01T", "s1Q9rs", "wjcEIp", "CGtC58", "RGz12a"]))
        if title_el:
            title = clean(title_el.get_text(strip=True))
        elif soup.find("img", alt=True):
            title = clean(soup.find("img", alt=True)["alt"])
        else:
            # Fallback to first line in card text containing a brand name
            lines = [l.strip() for l in text.split("\n") if l.strip()]
            for l in lines:
                if any(b in l for b in ["Acer", "ASUS", "HP", "Lenovo", "Dell", "MSI", "Apple", "Samsung", "LG"]):
                    title = l
                    break

    json_data = get_json_ld(soup)
    product = find_product(json_data)

    # 1. Identity
    brand = extract_brand(product, text, url, default_website=website)
    model, model_number, series, release_year = extract_model_and_number(product, text, title)

    # 2. CPU
    cpu_data = extract_cpu(text)

    # 3. GPU
    gpu_data = extract_gpu(text)

    # 4. NPU
    npu_data = extract_npu(text)

    # 5. RAM
    ram_data = extract_ram(text)

    # 6. Storage
    storage_data = extract_storage(text)

    # 7. Display
    display_data = extract_display(text)

    # 8. Physical
    physical_data = extract_physical(text)

    # 9. Security
    security_data = extract_security(text)

    # 10. Operating System
    os_data = extract_os(text)

    # 11. Peripherals & Connectivity
    peripherals_data = extract_peripherals(text)

    # 12. Price
    price_data = extract_price(text, product)

    # Timestamp
    scraped_at = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Construct complete 58-field record conforming to Phase 3 schema
    return {
        # Identity
        "brand": brand,
        "model": model,
        "model_number": model_number,
        "series": series,
        "release_year": release_year,

        # CPU
        "cpu_brand": cpu_data["cpu_brand"],
        "cpu_model": cpu_data["cpu_model"],
        "cpu_family": cpu_data["cpu_family"],
        "cpu_generation": cpu_data["cpu_generation"],
        "cpu_cores": cpu_data["cpu_cores"],
        "cpu_threads": cpu_data["cpu_threads"],
        "cpu_base_clock_ghz": cpu_data["cpu_base_clock_ghz"],
        "cpu_boost_clock_ghz": cpu_data["cpu_boost_clock_ghz"],

        # GPU
        "gpu_brand": gpu_data["gpu_brand"],
        "gpu_model": gpu_data["gpu_model"],
        "gpu_type": gpu_data["gpu_type"],
        "gpu_vram_gb": gpu_data["gpu_vram_gb"],
        "gpu_memory_type": gpu_data["gpu_memory_type"],
        "gpu_tgp_w": gpu_data["gpu_tgp_w"],

        # NPU
        "npu": npu_data["npu"],
        "npu_tops": npu_data["npu_tops"],

        # Memory
        "ram_gb": ram_data["ram_gb"],
        "ram_type": ram_data["ram_type"],
        "ram_speed": ram_data["ram_speed_mhz"],  # backwards-compatibility
        "ram_speed_mhz": ram_data["ram_speed_mhz"],
        "ram_upgradeable": ram_data["ram_upgradeable"],
        "ram_slots": ram_data["ram_slots"],

        # Storage
        "storage_type": storage_data["storage_type"],
        "storage_gb": storage_data["storage_gb"],
        "storage_interface": storage_data["storage_interface"],
        "ssd_slots": storage_data["ssd_slots"],
        "storage_upgradeable": storage_data["storage_upgradeable"],
        "max_expandable_storage_tb": storage_data["max_expandable_storage_tb"],

        # Display
        "display_size_inches": display_data["display_size_inches"],
        "resolution_width": display_data["resolution_width"],
        "resolution_height": display_data["resolution_height"],
        "resolution": display_data["resolution"],
        "aspect_ratio": display_data["aspect_ratio"],
        "panel_type": display_data["panel_type"],
        "refresh_rate_hz": display_data["refresh_rate_hz"],
        "response_time_ms": display_data["response_time_ms"],
        "color_gamut": display_data["color_gamut"],
        "brightness_nits": display_data["brightness_nits"],
        "touchscreen": display_data["touchscreen"],
        "screen_finish": display_data["screen_finish"],

        # Physical
        "weight_kg": physical_data["weight_kg"],
        "battery_wh": physical_data["battery_wh"],
        "build_material": physical_data["build_material"],
        "build_quality": physical_data["build_quality"],

        # Security
        "fingerprint": security_data["fingerprint"],
        "face_unlock": security_data["face_unlock"],

        # Operating System
        "operating_system": os_data["operating_system"],
        "windows_included": os_data["windows_included"],

        # Connectivity
        "wifi": peripherals_data["wifi"],
        "bluetooth": peripherals_data["bluetooth"],
        "webcam": peripherals_data["webcam"],

        # Ports & Keyboard
        "ports": peripherals_data["ports"],
        "keyboard_backlight": peripherals_data["keyboard_backlight"],
        "keyboard_type": peripherals_data["keyboard_type"],

        # Other
        "speakers": peripherals_data["speakers"],
        "sd_card_reader": peripherals_data["sd_card_reader"],
        "thunderbolt": peripherals_data["thunderbolt"],
        "usb4": peripherals_data["usb4"],
        "warranty_years": peripherals_data["warranty_years"],

        # Price
        "price_current": price_data["current"],
        "price_original": price_data["original"],
        "price_discount": price_data["discount"],

        # Market Price Aggregation Fields (populated during multi-retailer aggregation)
        "price_lowest": None,
        "price_average": None,
        "price_highest": None,
        "price_source_count": None,

        # Source
        "website": website,
        "url": url,
        "scraped_at": scraped_at
    }