import json
import re
from bs4 import BeautifulSoup


def clean(value):
    if value is None:
        return ""

    return re.sub(
        r"\s+",
        " ",
        str(value)
    ).strip()


def get_json_ld(soup):

    data = []

    for script in soup.find_all(
        "script",
        type="application/ld+json"
    ):

        try:

            content = script.string or script.get_text()

            parsed = json.loads(content)

            if isinstance(parsed, list):
                data.extend(parsed)

            else:
                data.append(parsed)

        except Exception:
            continue

    return data


def find_product(json_data):

    for item in json_data:

        if not isinstance(item, dict):
            continue

        item_type = item.get("@type")

        if item_type == "Product":
            return item

        if isinstance(item_type, list):

            if "Product" in item_type:
                return item

    return {}


def extract_tables(soup):

    specs = {}

    for table in soup.find_all("table"):

        rows = table.find_all("tr")

        for row in rows:

            cells = row.find_all(
                ["th", "td"]
            )

            if len(cells) < 2:
                continue

            key = clean(
                cells[0].get_text(" ")
            ).lower()

            value = clean(
                cells[1].get_text(" ")
            )

            if key and value:
                specs[key] = value

    return specs


def find_spec(specs, words):

    for key, value in specs.items():

        for word in words:

            if word.lower() in key.lower():
                return value

    return None


def extract_prices(text):

    patterns = [
        r"₹\s*([\d,]+)",
        r"Rs\.?\s*([\d,]+)",
        r"INR\s*([\d,]+)"
    ]

    prices = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            try:

                price = int(
                    match.replace(",", "")
                )

                if 5000 <= price <= 1000000:
                    prices.append(price)

            except:
                pass

    return sorted(set(prices))


def parse_html(
    html,
    url,
    website
):

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    json_data = get_json_ld(
        soup
    )

    product = find_product(
        json_data
    )

    specs = extract_tables(
        soup
    )

    page_text = clean(
        soup.get_text(" ")
    )

    brand = product.get(
        "brand"
    )

    if isinstance(
        brand,
        dict
    ):
        brand = brand.get(
            "name"
        )

    model = product.get(
        "name"
    )

    if not model and soup.title:
        model = soup.title.get_text()

    data = {

        "brand": clean(
            brand
        ),

        "model": clean(
            model
        ),

        "model_number":
            product.get("mpn")
            or product.get("model")
            or "",

        "cpu":
            find_spec(
                specs,
                [
                    "processor",
                    "cpu"
                ]
            ),

        "gpu":
            find_spec(
                specs,
                [
                    "graphics",
                    "gpu",
                    "graphic"
                ]
            ),

        "ram":
            find_spec(
                specs,
                [
                    "memory",
                    "ram"
                ]
            ),

        "storage":
            find_spec(
                specs,
                [
                    "storage",
                    "ssd",
                    "hard drive"
                ]
            ),

        "display":
            find_spec(
                specs,
                [
                    "display",
                    "screen"
                ]
            ),

        "operating_system":
            find_spec(
                specs,
                [
                    "operating system",
                    "os"
                ]
            ),

        "battery":
            find_spec(
                specs,
                [
                    "battery"
                ]
            ),

        "weight":
            find_spec(
                specs,
                [
                    "weight"
                ]
            ),

        "prices":
            extract_prices(
                page_text
            ),

        "website":
            website,

        "url":
            url,

        "raw_specifications":
            specs
    }

    return data