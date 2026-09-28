import argparse
import json
import os
import sys
from typing import Any, Dict, List, Union

import joblib
import numpy as np
import pandas as pd

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PACKAGE_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

MODEL_PATH = os.path.join(PACKAGE_DIR, "saved_model", "best_laptop_price_model.joblib")
REPORT_PATH = os.path.join(PACKAGE_DIR, "saved_model", "model_benchmark_report.json")

_CACHED_MODEL = None


def load_model():
    """
    Loads and caches the best trained model pipeline.
    """
    global _CACHED_MODEL
    if _CACHED_MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(
                f"Trained model artifact not found at: {MODEL_PATH}\n"
                f"Please train the model first by running: python model/train.py"
            )
        _CACHED_MODEL = joblib.load(MODEL_PATH)
    return _CACHED_MODEL


def predict_laptop_price(specs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Predicts the fair market retail price for any laptop configuration,
    including completely new or unseen brands, CPUs, or hardware specs.

    Args:
        specs: Dictionary of laptop hardware attributes.
               Supported keys:
                 - 'brand' (e.g. 'ASUS', 'Lenovo', 'HP', 'Apple')
                 - 'model' (e.g. 'Vivobook 15', 'Legion 5')
                 - 'cpu_brand' (e.g. 'Intel', 'AMD', 'Apple', 'Qualcomm')
                 - 'cpu_model' (e.g. 'Core i5 1335U', 'Ryzen 7 7730U', 'M3 Pro')
                 - 'cpu_family' (optional, inferred if omitted)
                 - 'ram_gb' (e.g. 8, 16, 32, 64)
                 - 'ram_type' (e.g. 'DDR5', 'LPDDR5X', 'DDR4')
                 - 'storage_gb' (e.g. 256, 512, 1024, 2048)
                 - 'storage_type' (e.g. 'NVMe SSD', 'SSD', 'eMMC')
                 - 'display_size_inches' (e.g. 14.0, 15.6, 16.0)
                 - 'gpu_type' ('Integrated' or 'Discrete')
                 - 'operating_system' (e.g. 'Windows 11 Home', 'macOS')

    Returns:
        Dict with predicted price (float), formatted price string, and confidence band.
    """
    model = load_model()

    # Apply defaults for any omitted fields
    default_specs = {
        "brand": "Unknown",
        "model": "Generic Laptop",
        "cpu_brand": "Intel",
        "cpu_model": "Core i5",
        "cpu_family": "Core i5",
        "ram_gb": 16,
        "ram_type": "DDR5",
        "storage_gb": 512,
        "storage_type": "SSD",
        "display_size_inches": 15.6,
        "gpu_type": "Integrated",
        "operating_system": "Windows 11 Home"
    }

    full_specs = default_specs.copy()
    full_specs.update(specs)

    # Invert to DataFrame
    df_input = pd.DataFrame([full_specs])

    # Predict price
    predicted_val = float(model.predict(df_input)[0])
    predicted_val = max(10000.0, round(predicted_val, 2))

    # Compute ±9% empirical confidence interval
    band_pct = 0.09
    price_low = round(predicted_val * (1.0 - band_pct), 2)
    price_high = round(predicted_val * (1.0 + band_pct), 2)

    return {
        "status": "success",
        "predicted_price_inr": predicted_val,
        "predicted_price_formatted": f"₹{predicted_val:,.2f}",
        "estimated_fair_range": {
            "low": price_low,
            "high": price_high,
            "formatted": f"₹{price_low:,.2f} – ₹{price_high:,.2f}"
        },
        "specifications_evaluated": {
            "brand": full_specs.get("brand"),
            "model": full_specs.get("model"),
            "cpu": f"{full_specs.get('cpu_brand')} {full_specs.get('cpu_model')}",
            "ram": f"{full_specs.get('ram_gb')} GB {full_specs.get('ram_type')}",
            "storage": f"{full_specs.get('storage_gb')} GB {full_specs.get('storage_type')}",
            "display": f"{full_specs.get('display_size_inches')}\"",
            "gpu_type": full_specs.get("gpu_type"),
            "os": full_specs.get("operating_system")
        }
    }


def predict_batch(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Predicts prices for a list of unseen laptop configurations.
    """
    results = []
    for r in records:
        results.append(predict_laptop_price(r))
    return results


def run_unseen_verification_demo():
    """
    Demonstrates predictions on 3 diverse, completely unseen laptop configurations.
    """
    print("\n" + "=" * 70)
    print("VERIFICATION: PREDICTING PRICES ON UNSEEN / NOVEL LAPTOP CONFIGURATIONS")
    print("=" * 70)

    unseen_samples = [
        {
            "name": "Unseen Budget Student Laptop",
            "specs": {
                "brand": "Lenovo",
                "model": "IdeaPad Slim 1 15",
                "cpu_brand": "AMD",
                "cpu_model": "Ryzen 3 7320U",
                "cpu_family": "Ryzen 3",
                "ram_gb": 8,
                "ram_type": "LPDDR5",
                "storage_gb": 512,
                "storage_type": "SSD",
                "display_size_inches": 15.6,
                "gpu_type": "Integrated",
                "operating_system": "Windows 11 Home"
            }
        },
        {
            "name": "Unseen Flagship Thin & Light Workstation",
            "specs": {
                "brand": "ASUS",
                "model": "Zenbook S 14 OLED",
                "cpu_brand": "Intel",
                "cpu_model": "Core Ultra 7 258V",
                "cpu_family": "Core Ultra 7",
                "ram_gb": 32,
                "ram_type": "LPDDR5X",
                "storage_gb": 1024,
                "storage_type": "NVMe SSD",
                "display_size_inches": 14.0,
                "gpu_type": "Integrated",
                "operating_system": "Windows 11 Home"
            }
        },
        {
            "name": "Unseen High-End Gaming Laptop",
            "specs": {
                "brand": "Dell",
                "model": "Alienware m16 R2",
                "cpu_brand": "Intel",
                "cpu_model": "Core Ultra 9 185H",
                "cpu_family": "Core Ultra 9",
                "ram_gb": 32,
                "ram_type": "DDR5",
                "storage_gb": 2048,
                "storage_type": "NVMe SSD",
                "display_size_inches": 16.0,
                "gpu_type": "Discrete",
                "operating_system": "Windows 11 Home"
            }
        }
    ]

    for item in unseen_samples:
        print(f"\nConfiguration: {item['name']}")
        res = predict_laptop_price(item["specs"])
        s = res["specifications_evaluated"]
        print(f"  Specs:     {s['brand']} | {s['cpu']} | {s['ram']} | {s['storage']} | {s['display']} | GPU: {s['gpu_type']}")
        print(f"  Predicted: {res['predicted_price_formatted']}")
        print(f"  Fair Band: {res['estimated_fair_range']['formatted']}")

    print("\n" + "=" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(description="LPARA Laptop Price Prediction Inference Engine")
    parser.add_argument("--brand", type=str, default="ASUS", help="Laptop brand (e.g. ASUS, Lenovo, HP, Dell, Apple)")
    parser.add_argument("--model", type=str, default="Vivobook 15", help="Model name")
    parser.add_argument("--cpu_brand", type=str, default="Intel", help="CPU brand (Intel, AMD, Apple, Qualcomm)")
    parser.add_argument("--cpu_model", type=str, default="Core i5 1335U", help="CPU model")
    parser.add_argument("--ram_gb", type=int, default=16, help="RAM in GB (e.g. 8, 16, 32)")
    parser.add_argument("--ram_type", type=str, default="DDR5", help="RAM type (DDR5, DDR4, LPDDR5X)")
    parser.add_argument("--storage_gb", type=int, default=512, help="Storage in GB (e.g. 512, 1024)")
    parser.add_argument("--storage_type", type=str, default="SSD", help="Storage type (SSD, NVMe SSD, eMMC)")
    parser.add_argument("--display_size", type=float, default=15.6, help="Display size in inches (e.g. 14.0, 15.6, 16.0)")
    parser.add_argument("--gpu_type", type=str, default="Integrated", choices=["Integrated", "Discrete"], help="GPU type")
    parser.add_argument("--os", type=str, default="Windows 11 Home", help="Operating system")
    parser.add_argument("--file", type=str, default=None, help="Path to JSON file containing laptop specifications to predict")
    parser.add_argument("--demo", action="store_true", help="Run verification demo on 3 unseen laptops")

    args = parser.parse_args()

    if args.demo:
        run_unseen_verification_demo()
        return

    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: file not found {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if isinstance(data, list):
            results = predict_batch(data)
            print(json.dumps(results, indent=2))
        else:
            result = predict_laptop_price(data)
            print(json.dumps(result, indent=2))
        return

    # Single laptop prediction via CLI args
    laptop_specs = {
        "brand": args.brand,
        "model": args.model,
        "cpu_brand": args.cpu_brand,
        "cpu_model": args.cpu_model,
        "ram_gb": args.ram_gb,
        "ram_type": args.ram_type,
        "storage_gb": args.storage_gb,
        "storage_type": args.storage_type,
        "display_size_inches": args.display_size,
        "gpu_type": args.gpu_type,
        "operating_system": args.os
    }

    res = predict_laptop_price(laptop_specs)
    print("\n" + "=" * 60)
    print("LPARA LAPTOP PRICE VALUATION RESULT")
    print("=" * 60)
    for k, v in res["specifications_evaluated"].items():
        print(f"  {k.capitalize():15s}: {v}")
    print("-" * 60)
    print(f"  PREDICTED PRICE: {res['predicted_price_formatted']}")
    print(f"  FAIR PRICE BAND: {res['estimated_fair_range']['formatted']}")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
