from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin


html = Path(
    "data/test.html"
).read_text(
    encoding="utf-8"
)

soup = BeautifulSoup(
    html,
    "lxml"
)

base_url = "https://www.asus.com"

urls = set()

for link in soup.find_all("a", href=True):

    href = link["href"]

    if "/laptops/" in href:

        full_url = urljoin(
            base_url,
            href
        )

        urls.add(full_url)


print(
    f"Found {len(urls)} possible laptop URLs\n"
)

for url in sorted(urls):

    print(url)