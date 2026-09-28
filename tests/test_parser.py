import json
from pathlib import Path

from parser import parse_html


HTML_FILE = Path(
    "data/product.html"
)


html = HTML_FILE.read_text(
    encoding="utf-8"
)


result = parse_html(
    html,
    "test-url",
    "asus"
)


print(
    json.dumps(
        result,
        indent=4,
        ensure_ascii=False
    )
)