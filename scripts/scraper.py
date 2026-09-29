import asyncio
from pathlib import Path

from crawlee.crawlers import (
    PlaywrightCrawler,
    PlaywrightCrawlingContext
)


BASE_DIR = Path(__file__).resolve().parent

URL_FILE = BASE_DIR / "urls" / "laptops.txt"

OUTPUT_FILE = BASE_DIR / "data" / "product.html"


async def main():

    print("Starting scraper...")

    BASE_DIR.joinpath("data").mkdir(
        exist_ok=True
    )

    urls = [
        url.strip()
        for url in URL_FILE.read_text(
            encoding="utf-8"
        ).splitlines()
        if url.strip()
    ]

    print("URLs found:", len(urls))

    crawler = PlaywrightCrawler(
        max_requests_per_crawl=len(urls),
        max_request_retries=2,
        browser_launch_options={
            "headless": True
        }
    )

    @crawler.router.default_handler
    async def handler(
        context: PlaywrightCrawlingContext
    ):

        print("\n===== PRODUCT PAGE =====")

        print(
            context.request.loaded_url
        )

        await context.page.wait_for_load_state(
            "domcontentloaded"
        )

        await context.page.wait_for_timeout(
            5000
        )

        html = await context.page.content()

        print(
            "HTML size:",
            len(html)
        )

        OUTPUT_FILE.write_text(
            html,
            encoding="utf-8"
        )

        print(
            "Saved:",
            OUTPUT_FILE
        )

    await crawler.run(urls)

    print("\nFinished.")


if __name__ == "__main__":
    asyncio.run(main())