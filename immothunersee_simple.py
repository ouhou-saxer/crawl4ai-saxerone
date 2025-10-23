"""
Simple ImmoThunersee.ch Scraper
================================

Quick and simple script to scrape properties from www.immothunersee.ch

Usage:
    python immothunersee_simple.py
"""

import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def scrape_immothunersee():
    """Simple function to scrape ImmoThunersee.ch properties."""

    # Target URL
    url = "https://www.immothunersee.ch/immobilien"

    # Define extraction schema
    schema = {
        "name": "ImmoThunerseeProperties",
        "baseSelector": """
            article.property,
            div.property-item,
            div.listing-item,
            div[class*='property'],
            div[class*='listing'],
            div.card
        """,
        "fields": [
            {
                "name": "title",
                "selector": "h1, h2, h3, h4, .title, [class*='title']",
                "type": "text"
            },
            {
                "name": "price",
                "selector": ".price, [class*='price'], [class*='preis']",
                "type": "text"
            },
            {
                "name": "location",
                "selector": "address, .location, .address, [class*='location']",
                "type": "text"
            },
            {
                "name": "rooms",
                "selector": "[class*='room'], [class*='zimmer']",
                "type": "text"
            },
            {
                "name": "area",
                "selector": "[class*='area'], [class*='flache']",
                "type": "text"
            },
            {
                "name": "description",
                "selector": ".description, [class*='description']",
                "type": "text"
            },
            {
                "name": "link",
                "selector": "a",
                "type": "attribute",
                "attribute": "href"
            },
            {
                "name": "image",
                "selector": "img",
                "type": "attribute",
                "attribute": "src"
            }
        ]
    }

    print(f"🏠 Scraping properties from: {url}\n")

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        user_agent_mode="random",
        java_script_enabled=True
    )

    # Start crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Configure extraction
        extraction_strategy = JsonCssExtractionStrategy(schema)
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=extraction_strategy,
            delay_before_return_html=3000  # Wait 3 seconds
        )

        # Scrape the page
        result = await crawler.arun(url=url, config=config)

        if result.success:
            # Parse results
            properties = json.loads(result.extracted_content)

            print(f"✅ Found {len(properties)} properties!\n")

            # Filter out empty results
            valid_properties = [
                p for p in properties
                if p.get('title') or p.get('price')
            ]

            print(f"Valid properties: {len(valid_properties)}\n")

            # Display first 5 properties
            print("📋 Sample Properties:")
            print("-" * 70)
            for i, prop in enumerate(valid_properties[:5], 1):
                print(f"\n{i}. {prop.get('title', 'No title')}")
                if prop.get('price'):
                    print(f"   💰 Price: {prop.get('price')}")
                if prop.get('location'):
                    print(f"   📍 Location: {prop.get('location')}")
                if prop.get('rooms'):
                    print(f"   🛏️  Rooms: {prop.get('rooms')}")
                if prop.get('area'):
                    print(f"   📏 Area: {prop.get('area')}")
                if prop.get('link'):
                    print(f"   🔗 Link: {prop.get('link')}")

            # Save to file
            with open("immothunersee_properties.json", "w", encoding="utf-8") as f:
                json.dump(valid_properties, f, indent=2, ensure_ascii=False)

            print(f"\n💾 Saved {len(valid_properties)} properties to: immothunersee_properties.json")

            if len(valid_properties) == 0:
                print("\n⚠️  No properties found. This could mean:")
                print("   1. The website structure has changed")
                print("   2. The CSS selectors need to be updated")
                print("   3. The page requires more time to load")
                print("\n💡 Try running the full scraper in inspect mode:")
                print("   python immothunersee_scraper.py --inspect")

        else:
            print(f"❌ Failed to scrape: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(scrape_immothunersee())
