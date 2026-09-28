import json
import pandas as pd
from datetime import datetime


RAW_FILE = "data/raw.jsonl"

rows = []

with open(
    RAW_FILE,
    encoding="utf-8"
) as f:

    for line in f:

        try:
            rows.append(
                json.loads(line)
            )

        except:
            continue


df = pd.DataFrame(rows)


def make_laptop_id(row):

    brand = str(
        row.get("brand", "")
    ).lower().strip()

    model_number = str(
        row.get("model_number", "")
    ).lower().strip()

    model = str(
        row.get("model", "")
    ).lower().strip()

    key = (
        brand + "_" +
        (model_number or model)
    )

    return (
        key
        .replace(" ", "_")
        .replace("/", "_")
    )


df["laptop_id"] = df.apply(
    make_laptop_id,
    axis=1
)


price_rows = []


for _, row in df.iterrows():

    prices = row.get(
        "prices_found",
        []
    )

    if not isinstance(
        prices,
        list
    ):
        continue

    for price in prices:

        price_rows.append({

            "laptop_id":
                row["laptop_id"],

            "website":
                row["website"],

            "price":
                price,

            "url":
                row["url"],

            "scraped_at":
                datetime.now().isoformat()

        })


prices = pd.DataFrame(
    price_rows
)


if not prices.empty:

    grouped = (
        prices
        .groupby("laptop_id")["price"]
        .agg([
            "min",
            "mean",
            "max"
        ])
        .reset_index()
    )

    grouped.columns = [
        "laptop_id",
        "lowest_price",
        "average_price",
        "highest_price"
    ]

    df = df.merge(
        grouped,
        on="laptop_id",
        how="left"
    )


df.drop(
    columns=["prices_found"],
    errors="ignore",
    inplace=True
)


df.to_csv(
    "data/laptops.csv",
    index=False
)

prices.to_csv(
    "data/prices.csv",
    index=False
)

print(
    f"Laptops: {len(df)}"
)

print(
    f"Prices: {len(prices)}"
)