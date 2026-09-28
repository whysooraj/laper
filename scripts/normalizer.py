import re


def clean_text(value):
    if not value:
        return ""

    value = re.sub(r"\s+", " ", str(value))
    return value.strip()


def first_number(text):
    if not text:
        return None

    match = re.search(r"[\d,.]+", text)

    if not match:
        return None

    try:
        return float(match.group().replace(",", ""))
    except:
        return None


def extract_gb(text):
    if not text:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*(TB|GB)",
        text,
        re.I
    )

    if not match:
        return None

    value = float(match.group(1))
    unit = match.group(2).lower()

    if unit == "tb":
        value *= 1024

    return value


def extract_ghz(text):
    if not text:
        return None

    values = re.findall(
        r"(\d+(?:\.\d+)?)\s*GHz",
        text,
        re.I
    )

    if not values:
        return None

    return [float(x) for x in values]


def extract_cores(text):
    if not text:
        return None

    match = re.search(
        r"(\d+)[-\s]?core",
        text,
        re.I
    )

    return int(match.group(1)) if match else None


def extract_threads(text):
    if not text:
        return None

    match = re.search(
        r"(\d+)[-\s]?thread",
        text,
        re.I
    )

    return int(match.group(1)) if match else None


def extract_resolution(text):
    if not text:
        return None

    match = re.search(
        r"(\d{3,5})\s*[x×]\s*(\d{3,5})",
        text,
        re.I
    )

    if not match:
        return None

    return f"{match.group(1)}x{match.group(2)}"


def extract_refresh_rate(text):
    if not text:
        return None

    match = re.search(
        r"(\d{2,4})\s*Hz",
        text,
        re.I
    )

    return int(match.group(1)) if match else None


def extract_screen_size(text):
    if not text:
        return None

    match = re.search(
        r'(\d{2}(?:\.\d+)?)["\s-]*(?:inch|inches)',
        text,
        re.I
    )

    return float(match.group(1)) if match else None


def extract_weight(text):
    if not text:
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)\s*kg",
        text,
        re.I
    )

    return float(match.group(1)) if match else None


def extract_price(text):
    if not text:
        return None

    prices = re.findall(
        r"(?:₹|Rs\.?|INR)\s*([\d,]+)",
        text,
        re.I
    )

    values = []

    for price in prices:
        try:
            value = int(price.replace(",", ""))

            if 10000 <= value <= 1000000:
                values.append(value)
        except:
            pass

    return values