"""
Thun Real Estate Scraper
========================

This script scrapes real estate listings from property websites in Thun, Switzerland.
It extracts property details including prices, locations, descriptions, and images.

Usage:
    python thun_real_estate_scraper.py

Requirements:
    - crawl4ai installed
    - Internet connection
"""

import asyncio
import json
import os
from datetime import datetime
from typing import List, Dict
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class ThunRealEstateScraper:
    """Scraper for real estate listings in Thun, Switzerland."""

    def __init__(self, output_dir: str = "thun_properties"):
        """
        Initialize the scraper.

        Args:
            output_dir: Directory to save scraped data
        """
        self.output_dir = output_dir
        self.results = []

        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)

        # Browser configuration for stealth crawling
        self.browser_config = BrowserConfig(
            headless=True,
            user_agent_mode="random",  # Rotate user agents to avoid detection
            java_script_enabled=True,
            viewport_width=1920,
            viewport_height=1080
        )

    def get_homegate_schema(self) -> dict:
        """
        Get extraction schema for homegate.ch - one of Switzerland's largest real estate platforms.

        Returns:
            JSON schema for extracting property data
        """
        return {
            "name": "ThunProperties",
            "baseSelector": "article[data-test='result-list-item'], div.ResultList_listItem__YDfZ_, div[class*='ListItem']",
            "fields": [
                {
                    "name": "title",
                    "selector": "h3, .ListItemTitle_title__Bi3Yw, [class*='Title']",
                    "type": "text"
                },
                {
                    "name": "price",
                    "selector": "span[data-test='price'], .ListItemPrice_price__PZ9Au, [class*='Price']",
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": "address, .ListItemAddress_address__JBkXz, [class*='Address']",
                    "type": "text"
                },
                {
                    "name": "rooms",
                    "selector": "span[data-test='rooms'], [class*='Rooms']",
                    "type": "text"
                },
                {
                    "name": "area",
                    "selector": "span[data-test='surface-living'], [class*='Surface']",
                    "type": "text"
                },
                {
                    "name": "description",
                    "selector": "p[class*='description'], .ListItemDescription_description__Gxx9y",
                    "type": "text"
                },
                {
                    "name": "link",
                    "selector": "a[href*='/detail/'], a[data-test='listing-link']",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "image",
                    "selector": "img[data-test='listing-image'], img[class*='ListItemImage']",
                    "type": "attribute",
                    "attribute": "src"
                }
            ]
        }

    def get_immoscout_schema(self) -> dict:
        """
        Get extraction schema for immoscout24.ch.

        Returns:
            JSON schema for extracting property data
        """
        return {
            "name": "ThunProperties",
            "baseSelector": "article.resultlist-item, div[class*='PropertyCard']",
            "fields": [
                {
                    "name": "title",
                    "selector": "h3, .property-title",
                    "type": "text"
                },
                {
                    "name": "price",
                    "selector": "span.price, [class*='Price']",
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": ".address, [class*='Location']",
                    "type": "text"
                },
                {
                    "name": "rooms",
                    "selector": "span[title*='Zimmer'], [class*='Rooms']",
                    "type": "text"
                },
                {
                    "name": "area",
                    "selector": "span[title*='Wohnfläche'], [class*='Area']",
                    "type": "text"
                },
                {
                    "name": "link",
                    "selector": "a[href*='/detail/']",
                    "type": "attribute",
                    "attribute": "href"
                },
                {
                    "name": "image",
                    "selector": "img.property-image",
                    "type": "attribute",
                    "attribute": "src"
                }
            ]
        }

    def get_generic_schema(self) -> dict:
        """
        Get a generic extraction schema that works with most real estate sites.

        Returns:
            JSON schema for extracting property data
        """
        return {
            "name": "ThunProperties",
            "baseSelector": "article, div[class*='property'], div[class*='listing'], div[class*='result']",
            "fields": [
                {
                    "name": "title",
                    "selector": "h1, h2, h3, h4, [class*='title'], [class*='Title']",
                    "type": "text"
                },
                {
                    "name": "price",
                    "selector": "[class*='price'], [class*='Price'], [data-test*='price']",
                    "type": "text"
                },
                {
                    "name": "address",
                    "selector": "address, [class*='address'], [class*='Address'], [class*='location'], [class*='Location']",
                    "type": "text"
                },
                {
                    "name": "rooms",
                    "selector": "[class*='room'], [class*='Room'], [data-test*='room']",
                    "type": "text"
                },
                {
                    "name": "area",
                    "selector": "[class*='area'], [class*='Area'], [class*='surface'], [class*='Surface']",
                    "type": "text"
                },
                {
                    "name": "description",
                    "selector": "p[class*='description'], [class*='Description']",
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

    async def scrape_page(
        self,
        crawler: AsyncWebCrawler,
        url: str,
        schema: dict,
        wait_time: int = 3000
    ) -> List[Dict]:
        """
        Scrape a single page.

        Args:
            crawler: AsyncWebCrawler instance
            url: URL to scrape
            schema: Extraction schema
            wait_time: Time to wait for page load (milliseconds)

        Returns:
            List of extracted properties
        """
        print(f"🔍 Scraping: {url}")

        try:
            # Configure crawler with extraction strategy
            extraction_strategy = JsonCssExtractionStrategy(schema)

            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                extraction_strategy=extraction_strategy,
                wait_for="() => { return document.readyState === 'complete'; }",
                page_timeout=30000,
                delay_before_return_html=wait_time
            )

            # Execute crawl
            result = await crawler.arun(url=url, config=config)

            if result.success:
                # Parse extracted content
                if result.extracted_content:
                    properties = json.loads(result.extracted_content)
                    print(f"✅ Found {len(properties)} properties")
                    return properties
                else:
                    print("⚠️  No properties extracted (check CSS selectors)")
                    return []
            else:
                print(f"❌ Failed to scrape: {result.error_message}")
                return []

        except Exception as e:
            print(f"❌ Error scraping {url}: {str(e)}")
            return []

    async def scrape_thun_properties(
        self,
        urls: List[str] = None,
        schema_type: str = "generic"
    ) -> List[Dict]:
        """
        Scrape real estate properties from Thun.

        Args:
            urls: List of URLs to scrape. If None, uses default Thun property search URLs
            schema_type: Type of schema to use ('homegate', 'immoscout', 'generic')

        Returns:
            List of all scraped properties
        """
        # Default URLs for Thun properties if none provided
        if urls is None:
            urls = [
                # Homegate - Thun region
                "https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste",
                "https://www.homegate.ch/mieten/immobilien/ort-thun/trefferliste",

                # ImmoScout24 - Thun region
                "https://www.immoscout24.ch/de/immobilien/kaufen/ort-thun",
                "https://www.immoscout24.ch/de/immobilien/mieten/ort-thun",
            ]

        # Select schema based on type
        if schema_type == "homegate":
            schema = self.get_homegate_schema()
        elif schema_type == "immoscout":
            schema = self.get_immoscout_schema()
        else:
            schema = self.get_generic_schema()

        print(f"🏠 Starting Thun Real Estate Scraper")
        print(f"📊 Schema type: {schema_type}")
        print(f"🔗 URLs to scrape: {len(urls)}")
        print("=" * 60)

        # Initialize crawler
        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            all_properties = []

            # Scrape each URL
            for url in urls:
                properties = await self.scrape_page(crawler, url, schema)
                all_properties.extend(properties)

                # Small delay between requests to be respectful
                await asyncio.sleep(2)

            self.results = all_properties
            print("=" * 60)
            print(f"✨ Total properties scraped: {len(all_properties)}")

            return all_properties

    def save_results(self, format: str = "json") -> str:
        """
        Save scraped results to file.

        Args:
            format: Output format ('json' or 'csv')

        Returns:
            Path to saved file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            filename = os.path.join(self.output_dir, f"thun_properties_{timestamp}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.results)} properties to: {filename}")
            return filename

        elif format == "csv":
            import csv
            filename = os.path.join(self.output_dir, f"thun_properties_{timestamp}.csv")

            if self.results:
                # Get all unique keys from all properties
                fieldnames = set()
                for prop in self.results:
                    fieldnames.update(prop.keys())
                fieldnames = sorted(list(fieldnames))

                with open(filename, "w", encoding="utf-8", newline="") as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(self.results)

                print(f"💾 Saved {len(self.results)} properties to: {filename}")
                return filename
            else:
                print("⚠️  No results to save")
                return None

    def print_summary(self):
        """Print a summary of scraped properties."""
        if not self.results:
            print("No properties found.")
            return

        print("\n" + "=" * 60)
        print("📊 SCRAPING SUMMARY")
        print("=" * 60)
        print(f"Total properties: {len(self.results)}")

        # Count properties with prices
        with_price = sum(1 for p in self.results if p.get("price"))
        print(f"With price info: {with_price}")

        # Count properties with images
        with_image = sum(1 for p in self.results if p.get("image"))
        print(f"With images: {with_image}")

        # Show sample properties
        print("\n📋 Sample Properties:")
        print("-" * 60)
        for i, prop in enumerate(self.results[:3], 1):
            print(f"\n{i}. {prop.get('title', 'No title')}")
            print(f"   Price: {prop.get('price', 'N/A')}")
            print(f"   Address: {prop.get('address', 'N/A')}")
            print(f"   Rooms: {prop.get('rooms', 'N/A')}")
            print(f"   Area: {prop.get('area', 'N/A')}")
            if prop.get('link'):
                print(f"   Link: {prop.get('link')}")
        print("=" * 60)


async def main():
    """Main function to run the scraper."""

    # Create scraper instance
    scraper = ThunRealEstateScraper(output_dir="thun_properties")

    # Example 1: Scrape with generic schema (works with most sites)
    print("\n🚀 Example 1: Generic scraping")
    print("-" * 60)
    await scraper.scrape_thun_properties(schema_type="generic")

    # Save results
    scraper.save_results(format="json")
    scraper.save_results(format="csv")

    # Print summary
    scraper.print_summary()

    # Example 2: Scrape specific URL with custom configuration
    print("\n\n🚀 Example 2: Custom URL scraping")
    print("-" * 60)
    custom_urls = [
        "https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste",
    ]

    scraper2 = ThunRealEstateScraper(output_dir="thun_properties")
    await scraper2.scrape_thun_properties(
        urls=custom_urls,
        schema_type="homegate"
    )

    scraper2.save_results(format="json")
    scraper2.print_summary()


if __name__ == "__main__":
    # Run the scraper
    asyncio.run(main())
