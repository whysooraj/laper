# 🧪 Tests Directory (`tests/`)

## Overview & Purpose
The `tests/` directory contains unit and integration test scripts designed to verify parser extraction integrity, HTML DOM decoding, and preprocessing output sanity.

---

## 📁 Test Files & Responsibilities

| File | Purpose | How Created | How Used |
| :--- | :--- | :--- | :--- |
| `test_parser.py` | Integration test verifying HTML spec extraction against sample product HTML (`data/product.html`). | Created to test and validate regex/DOM extraction logic for ASUS and OEM store listings. | Run via: `python tests/test_parser.py` or `pytest tests/`. |

---

## 💻 Running Tests

```bash
# Run parser test script:
python tests/test_parser.py
```
Outputs parsed JSON object verifying all target specification fields (CPU, RAM, Storage, Price, Display).
