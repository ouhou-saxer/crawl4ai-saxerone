"""
ImmoThunersee.ch Property Scraper
==================================

Specialized scraper for www.immothunersee.ch real estate listings.

Usage:
    # Inspect mode - discover selectors
    python immothunersee_scraper.py --inspect

    # Scrape mode - extract properties
    python immothunersee_scraper.py --scrape
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy


class ImmoThunerseeScr:
    """Scraper specifically designed for www.immothunersee.ch"""

    BASE_URL = "https://www.immothunersee.ch"
    LISTINGS_URL = "https://www.immothunersee.ch/immobilien"

    def __init__(self, output_dir: str = "immothunersee_data"):
        """Initialize the scraper."""
        self.output_dir = output_dir
        self.results = []
        os.makedirs(output_dir, exist_ok=True)

        # Browser configuration
        self.browser_config = BrowserConfig(
            headless=True,
            user_agent_mode="random",
            java_script_enabled=True,
            viewport_width=1920,
            viewport_height=1080
        )

    def get_extraction_schema(self) -> dict:
        """
        Get extraction schema for immothunersee.ch.

        This schema uses common patterns found in real estate websites.
        May need adjustment based on actual site structure.
        """
        return {
            "name": "ImmoThunerseeProperties",
            "baseSelector": """
                article.property,
                div.property-item,
                div.listing-item,
                div[class*='property'],
                div[class*='listing'],
                div[class*='immobilie'],
                div.card,
                li[class*='property'],
                div.result-item
            """,
            "fields": [
                {
                    "name": "title",
                    "selector": """
                        h1, h2, h3, h4,
                        .title,
                        .property-title,
                        [class*='title'],
                        [class*='Title']
                    """,
                    "type": "text"
                },
                {
                    "name": "price",
                    "selector": """
                        .price,
                        .property-price,
                        [class*='price'],
                        [class*='Price'],
                        [class*='preis'],
                        [class*='Preis']
                    """,
                    "type": "text"
                },
                {
                    "name": "location",
                    "selector": """
                        address,
                        .location,
                        .address,
                        .property-location,
                        [class*='location'],
                        [class*='Location'],
                        [class*='address'],
                        [class*='Address'],
                        [class*='ort'],
                        [class*='Ort']
                    """,
                    "type": "text"
                },
                {
                    "name": "rooms",
                    "selector": """
                        [class*='room'],
                        [class*='Room'],
                        [class*='zimmer'],
                        [class*='Zimmer'],
                        [title*='Zimmer'],
                        [title*='zimmer']
                    """,
                    "type": "text"
                },
                {
                    "name": "area",
                    "selector": """
                        [class*='area'],
                        [class*='Area'],
                        [class*='surface'],
                        [class*='Surface'],
                        [class*='flache'],
                        [class*='Flache'],
                        [class*='wohnflache'],
                        [title*='Wohnfläche']
                    """,
                    "type": "text"
                },
                {
                    "name": "description",
                    "selector": """
                        p.description,
                        .property-description,
                        [class*='description'],
                        [class*='Description'],
                        [class*='beschreibung']
                    """,
                    "type": "text"
                },
                {
                    "name": "type",
                    "selector": """
                        .property-type,
                        [class*='type'],
                        [class*='Type'],
                        [class*='kategorie'],
                        [class*='Kategorie']
                    """,
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

    async def inspect_page(self, url: Optional[str] = None) -> Dict:
        """
        Inspect the page structure to help identify correct selectors.

        Args:
            url: URL to inspect (defaults to main listings page)

        Returns:
            Dictionary with page structure information
        """
        if url is None:
            url = self.LISTINGS_URL

        print(f"🔍 Inspecting: {url}")
        print("=" * 70)

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                delay_before_return_html=3000,
                page_timeout=30000
            )

            result = await crawler.arun(url=url, config=config)

            if result.success:
                print("✅ Page loaded successfully!\n")

                # Get page info
                html = result.html

                # Save raw HTML for inspection
                html_file = os.path.join(self.output_dir, "page_structure.html")
                with open(html_file, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"💾 Raw HTML saved to: {html_file}")

                # Save markdown version
                md_file = os.path.join(self.output_dir, "page_content.md")
                with open(md_file, "w", encoding="utf-8") as f:
                    f.write(result.markdown or "No markdown available")
                print(f"📝 Markdown content saved to: {md_file}")

                # Extract links
                links = result.links
                if links:
                    print(f"\n🔗 Found {len(links.get('internal', []))} internal links")
                    property_links = [
                        link for link in links.get('internal', [])
                        if any(keyword in link.lower() for keyword in ['immobilie', 'property', 'detail', 'objekt'])
                    ]
                    if property_links:
                        print(f"🏠 Property-related links: {len(property_links)}")
                        print("Sample property links:")
                        for link in property_links[:5]:
                            print(f"   - {link}")

                # Extract media
                media = result.media
                if media and media.get('images'):
                    print(f"\n🖼️  Found {len(media['images'])} images")

                print("\n" + "=" * 70)
                print("📊 INSPECTION COMPLETE")
                print("=" * 70)
                print("\nNext steps:")
                print("1. Open page_structure.html in a browser")
                print("2. Use DevTools to inspect property listing elements")
                print("3. Update the extraction schema with correct selectors")
                print("4. Run in scrape mode: python immothunersee_scraper.py --scrape")

                return {
                    "success": True,
                    "url": url,
                    "html_length": len(html),
                    "links_count": len(links.get('internal', [])),
                    "images_count": len(media.get('images', [])) if media else 0
                }

            else:
                print(f"❌ Failed to load page: {result.error_message}")
                return {"success": False, "error": result.error_message}

    async def scrape_properties(
        self,
        url: Optional[str] = None,
        max_pages: int = 1
    ) -> List[Dict]:
        """
        Scrape property listings.

        Args:
            url: URL to scrape (defaults to main listings page)
            max_pages: Maximum number of pages to scrape

        Returns:
            List of extracted properties
        """
        if url is None:
            url = self.LISTINGS_URL

        print(f"🏠 Scraping ImmoThunersee.ch Properties")
        print(f"🔗 URL: {url}")
        print(f"📄 Max pages: {max_pages}")
        print("=" * 70)

        all_properties = []

        async with AsyncWebCrawler(config=self.browser_config) as crawler:
            for page in range(1, max_pages + 1):
                print(f"\n📄 Page {page}/{max_pages}")

                # Construct page URL
                page_url = url
                if page > 1:
                    # Common pagination patterns
                    page_url = f"{url}?page={page}"
                    # Alternative: page_url = f"{url}/page/{page}"

                # Configure extraction
                schema = self.get_extraction_schema()
                extraction_strategy = JsonCssExtractionStrategy(schema)

                config = CrawlerRunConfig(
                    cache_mode=CacheMode.BYPASS,
                    extraction_strategy=extraction_strategy,
                    delay_before_return_html=3000,
                    page_timeout=30000,
                    wait_for="() => { return document.readyState === 'complete'; }"
                )

                # Scrape page
                result = await crawler.arun(url=page_url, config=config)

                if result.success:
                    try:
                        properties = json.loads(result.extracted_content)
                        print(f"✅ Found {len(properties)} properties on page {page}")

                        # Clean and normalize data
                        for prop in properties:
                            # Ensure link is absolute
                            if prop.get('link') and not prop['link'].startswith('http'):
                                if prop['link'].startswith('/'):
                                    prop['link'] = f"{self.BASE_URL}{prop['link']}"
                                else:
                                    prop['link'] = f"{self.BASE_URL}/{prop['link']}"

                            # Same for images
                            if prop.get('image') and not prop['image'].startswith('http'):
                                if prop['image'].startswith('/'):
                                    prop['image'] = f"{self.BASE_URL}{prop['image']}"
                                else:
                                    prop['image'] = f"{self.BASE_URL}/{prop['image']}"

                        all_properties.extend(properties)

                        # Show sample
                        if properties and page == 1:
                            print("\n📋 Sample property:")
                            sample = properties[0]
                            for key, value in sample.items():
                                if value:
                                    print(f"   {key}: {value[:100] if isinstance(value, str) else value}")

                        # If no properties found, might be end of listings
                        if len(properties) == 0:
                            print("No more properties found, stopping.")
                            break

                    except json.JSONDecodeError as e:
                        print(f"⚠️  Error parsing JSON: {e}")
                        print("Raw content sample:", result.extracted_content[:200] if result.extracted_content else "None")

                else:
                    print(f"❌ Failed to scrape page {page}: {result.error_message}")

                # Respectful delay between pages
                if page < max_pages:
                    await asyncio.sleep(2)

        self.results = all_properties
        print("\n" + "=" * 70)
        print(f"✨ Total properties scraped: {len(all_properties)}")
        print("=" * 70)

        return all_properties

    def save_results(self, format: str = "json") -> Optional[str]:
        """Save scraped results to file."""
        if not self.results:
            print("⚠️  No results to save")
            return None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format == "json":
            filename = os.path.join(self.output_dir, f"properties_{timestamp}.json")
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(self.results)} properties to: {filename}")
            return filename

        elif format == "csv":
            import csv
            filename = os.path.join(self.output_dir, f"properties_{timestamp}.csv")

            # Get all unique keys
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

    def print_summary(self):
        """Print summary of scraped properties."""
        if not self.results:
            print("No properties found.")
            return

        print("\n" + "=" * 70)
        print("📊 SCRAPING SUMMARY")
        print("=" * 70)
        print(f"Total properties: {len(self.results)}")

        # Statistics
        with_price = sum(1 for p in self.results if p.get('price'))
        with_location = sum(1 for p in self.results if p.get('location'))
        with_image = sum(1 for p in self.results if p.get('image'))
        with_link = sum(1 for p in self.results if p.get('link'))

        print(f"With price: {with_price} ({with_price/len(self.results)*100:.1f}%)")
        print(f"With location: {with_location} ({with_location/len(self.results)*100:.1f}%)")
        print(f"With image: {with_image} ({with_image/len(self.results)*100:.1f}%)")
        print(f"With link: {with_link} ({with_link/len(self.results)*100:.1f}%)")

        # Show sample properties
        print("\n📋 Sample Properties:")
        print("-" * 70)
        for i, prop in enumerate(self.results[:3], 1):
            print(f"\n{i}. {prop.get('title', 'No title')}")
            print(f"   💰 Price: {prop.get('price', 'N/A')}")
            print(f"   📍 Location: {prop.get('location', 'N/A')}")
            print(f"   🛏️  Rooms: {prop.get('rooms', 'N/A')}")
            print(f"   📏 Area: {prop.get('area', 'N/A')}")
            print(f"   🏷️  Type: {prop.get('type', 'N/A')}")
            if prop.get('link'):
                print(f"   🔗 Link: {prop.get('link')}")
        print("=" * 70)


async def main():
    """Main function."""
    import argparse

    parser = argparse.ArgumentParser(description="ImmoThunersee.ch Property Scraper")
    parser.add_argument(
        "--mode",
        choices=["inspect", "scrape"],
        default="scrape",
        help="Mode: inspect (discover selectors) or scrape (extract properties)"
    )
    parser.add_argument(
        "--inspect",
        action="store_true",
        help="Run in inspect mode (shortcut)"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Custom URL to scrape (optional)"
    )
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to scrape (default: 1)"
    )

    args = parser.parse_args()

    # Handle --inspect shortcut
    if args.inspect:
        args.mode = "inspect"

    # Create scraper
    scraper = ImmoThunerseeScr()

    if args.mode == "inspect":
        # Inspection mode
        await scraper.inspect_page(url=args.url)

    else:
        # Scraping mode
        properties = await scraper.scrape_properties(
            url=args.url,
            max_pages=args.pages
        )

        if properties:
            # Save results
            scraper.save_results(format="json")
            scraper.save_results(format="csv")

            # Print summary
            scraper.print_summary()
        else:
            print("\n⚠️  No properties were extracted.")
            print("\nTroubleshooting:")
            print("1. Run in inspect mode: python immothunersee_scraper.py --inspect")
            print("2. Check the saved HTML file to verify page structure")
            print("3. Update CSS selectors in get_extraction_schema()")


if __name__ == "__main__":
    asyncio.run(main())
