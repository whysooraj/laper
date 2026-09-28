from pathlib import Path
from bs4 import BeautifulSoup

html = Path("data/product.html").read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(html, "lxml")

text = soup.get_text(
    "\n",
    strip=True
)

Path("data/page_text.txt").write_text(
    text,
    encoding="utf-8"
)

print("Saved:", Path("data/page_text.txt").resolve())
print("Characters:", len(text))