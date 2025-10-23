"""
Simple Thun Real Estate Scraper - Quick Start
==============================================

A simplified version for quick testing and learning.
"""

import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


async def scrape_thun_properties_simple():
    """Simple function to scrape Thun real estate listings."""

    # Define what data to extract
    schema = {
        "name": "Properties",
        "baseSelector": "article, div[class*='property'], div[class*='listing']",
        "fields": [
            {"name": "title", "selector": "h1, h2, h3", "type": "text"},
            {"name": "price", "selector": "[class*='price']", "type": "text"},
            {"name": "address", "selector": "[class*='address'], [class*='location']", "type": "text"},
            {"name": "rooms", "selector": "[class*='room']", "type": "text"},
            {"name": "area", "selector": "[class*='area'], [class*='surface']", "type": "text"},
            {"name": "link", "selector": "a", "type": "attribute", "attribute": "href"},
        ]
    }

    # Configure browser
    browser_config = BrowserConfig(
        headless=True,
        user_agent_mode="random"
    )

    # URL to scrape - modify this to your target website
    url = "https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste"

    print(f"🏠 Scraping Thun properties from: {url}\n")

    # Start crawler
    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Configure extraction
        config = CrawlerRunConfig(
            cache_mode=CacheMode.BYPASS,
            extraction_strategy=JsonCssExtractionStrategy(schema),
            delay_before_return_html=3000  # Wait 3 seconds for page to load
        )

        # Scrape the page
        result = await crawler.arun(url=url, config=config)

        if result.success:
            # Parse results
            properties = json.loads(result.extracted_content)

            print(f"✅ Found {len(properties)} properties!\n")

            # Display first 5 properties
            for i, prop in enumerate(properties[:5], 1):
                print(f"{i}. {prop.get('title', 'No title')}")
                print(f"   💰 Price: {prop.get('price', 'N/A')}")
                print(f"   📍 Location: {prop.get('address', 'N/A')}")
                print(f"   🛏️  Rooms: {prop.get('rooms', 'N/A')}")
                print(f"   📏 Area: {prop.get('area', 'N/A')}")
                print()

            # Save to file
            with open("thun_properties_simple.json", "w", encoding="utf-8") as f:
                json.dump(properties, f, indent=2, ensure_ascii=False)

            print(f"💾 Saved all {len(properties)} properties to: thun_properties_simple.json")

        else:
            print(f"❌ Failed to scrape: {result.error_message}")


if __name__ == "__main__":
    asyncio.run(scrape_thun_properties_simple())
