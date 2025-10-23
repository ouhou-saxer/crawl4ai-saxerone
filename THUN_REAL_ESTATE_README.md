# Thun Real Estate Scraper

A web scraper for extracting real estate listings from property websites in Thun, Switzerland, built with crawl4ai.

## Overview

This project provides tools to scrape property listings from Swiss real estate websites, focusing on the Thun region. It extracts comprehensive property data including:

- Property titles and descriptions
- Prices (rent/sale)
- Addresses and locations
- Number of rooms
- Living area (m²)
- Property images
- Direct links to listings

## Files

- **`thun_real_estate_scraper.py`** - Full-featured scraper with multiple schema support
- **`thun_real_estate_simple.py`** - Simplified version for quick testing
- **`THUN_REAL_ESTATE_README.md`** - This documentation file

## Requirements

```bash
# Install crawl4ai
pip install crawl4ai

# Or if not already installed
pip install -r requirements.txt
```

## Quick Start

### Option 1: Simple Scraper (Recommended for beginners)

```bash
python thun_real_estate_simple.py
```

This will:
1. Scrape a default Thun property listing page
2. Display the first 5 properties in the terminal
3. Save all results to `thun_properties_simple.json`

### Option 2: Full-Featured Scraper

```bash
python thun_real_estate_scraper.py
```

This will:
1. Scrape multiple property websites
2. Use optimized extraction schemas
3. Save results in both JSON and CSV formats
4. Display a comprehensive summary

## Usage Examples

### Example 1: Basic Scraping

```python
import asyncio
from thun_real_estate_scraper import ThunRealEstateScraper

async def main():
    scraper = ThunRealEstateScraper(output_dir="my_properties")
    await scraper.scrape_thun_properties()
    scraper.save_results(format="json")
    scraper.print_summary()

asyncio.run(main())
```

### Example 2: Custom URLs

```python
import asyncio
from thun_real_estate_scraper import ThunRealEstateScraper

async def main():
    scraper = ThunRealEstateScraper()

    # Scrape specific URLs
    custom_urls = [
        "https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste",
        "https://www.immoscout24.ch/de/immobilien/mieten/ort-thun",
    ]

    await scraper.scrape_thun_properties(
        urls=custom_urls,
        schema_type="homegate"  # Use optimized schema for homegate.ch
    )

    scraper.save_results(format="csv")

asyncio.run(main())
```

### Example 3: Different Schema Types

```python
# Use different schemas for different websites
await scraper.scrape_thun_properties(
    urls=["https://www.homegate.ch/..."],
    schema_type="homegate"  # Options: 'homegate', 'immoscout', 'generic'
)
```

## Supported Websites

The scraper includes optimized extraction schemas for:

1. **Homegate.ch** - Switzerland's leading real estate platform
   - Schema type: `"homegate"`
   - URLs: `https://www.homegate.ch/kaufen/immobilien/ort-thun/`

2. **ImmoScout24.ch** - Popular Swiss property portal
   - Schema type: `"immoscout"`
   - URLs: `https://www.immoscout24.ch/de/immobilien/ort-thun`

3. **Generic** - Works with most real estate websites
   - Schema type: `"generic"`
   - Use for other property websites

## Configuration Options

### Browser Configuration

```python
browser_config = BrowserConfig(
    headless=True,              # Run without visible browser
    user_agent_mode="random",   # Rotate user agents
    viewport_width=1920,        # Browser window width
    viewport_height=1080        # Browser window height
)
```

### Crawler Configuration

```python
config = CrawlerRunConfig(
    cache_mode=CacheMode.BYPASS,        # Don't use cache
    delay_before_return_html=3000,      # Wait 3 seconds before extraction
    page_timeout=30000,                 # 30 second page timeout
)
```

## Output Format

### JSON Output

```json
[
  {
    "title": "Beautiful 3.5-room apartment in Thun",
    "price": "CHF 2,500 / month",
    "address": "Thun, Bern",
    "rooms": "3.5",
    "area": "95 m²",
    "description": "Modern apartment with lake view...",
    "link": "https://www.example.com/property/12345",
    "image": "https://www.example.com/images/property.jpg"
  }
]
```

### CSV Output

Properties are saved with columns for each field (title, price, address, rooms, area, etc.)

## Advanced Usage

### Scraping Multiple Pages

```python
async def scrape_multiple_pages():
    scraper = ThunRealEstateScraper()
    all_properties = []

    # Scrape pages 1-5
    for page in range(1, 6):
        url = f"https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste?ep={page}"
        properties = await scraper.scrape_page(
            crawler,
            url,
            scraper.get_homegate_schema()
        )
        all_properties.extend(properties)

    return all_properties
```

### Custom Schema

```python
custom_schema = {
    "name": "CustomProperties",
    "baseSelector": "div.property-card",  # Main container for each property
    "fields": [
        {"name": "title", "selector": "h2.title", "type": "text"},
        {"name": "price", "selector": "span.price", "type": "text"},
        {"name": "custom_field", "selector": ".custom", "type": "text"},
    ]
}

extraction_strategy = JsonCssExtractionStrategy(custom_schema)
config = CrawlerRunConfig(extraction_strategy=extraction_strategy)
```

## Troubleshooting

### No Properties Found

If the scraper returns 0 properties:

1. **Check CSS selectors**: The website structure may have changed
   - Inspect the website with browser DevTools
   - Update the schema selectors accordingly

2. **Try different schema types**:
   ```python
   # Try generic schema
   await scraper.scrape_thun_properties(schema_type="generic")
   ```

3. **Increase wait time**:
   ```python
   config = CrawlerRunConfig(
       delay_before_return_html=5000  # Wait 5 seconds
   )
   ```

### Connection Issues

If you encounter connection errors:

1. Check your internet connection
2. The website may be blocking automated requests
3. Try using proxies (advanced):
   ```python
   browser_config = BrowserConfig(
       proxy_config={"server": "http://proxy-server:port"}
   )
   ```

### Website Structure Changed

Websites update their HTML structure frequently. If scraping stops working:

1. Use browser DevTools to inspect the new structure
2. Update CSS selectors in the schema
3. Consider using the `generic` schema as a fallback

## Best Practices

1. **Be Respectful**
   - Add delays between requests (`await asyncio.sleep(2)`)
   - Don't overload servers with too many concurrent requests
   - Check the website's `robots.txt` and Terms of Service

2. **Error Handling**
   - Always check `result.success` before processing data
   - Implement retry logic for failed requests
   - Save partial results regularly

3. **Data Quality**
   - Validate extracted data before saving
   - Clean and normalize prices, addresses, etc.
   - Remove duplicate listings

4. **Performance**
   - Use `arun_many()` for parallel crawling of multiple URLs
   - Cache results when appropriate
   - Limit concurrent requests to avoid IP bans

## Example: Complete Workflow

```python
import asyncio
import json
from thun_real_estate_scraper import ThunRealEstateScraper

async def complete_workflow():
    """Complete scraping workflow with error handling."""

    # Initialize scraper
    scraper = ThunRealEstateScraper(output_dir="thun_data")

    try:
        # Define URLs to scrape
        urls = [
            "https://www.homegate.ch/kaufen/immobilien/ort-thun/trefferliste",
            "https://www.homegate.ch/mieten/immobilien/ort-thun/trefferliste",
        ]

        # Scrape properties
        print("Starting scraping...")
        properties = await scraper.scrape_thun_properties(
            urls=urls,
            schema_type="homegate"
        )

        # Validate data
        valid_properties = [
            p for p in properties
            if p.get('title') and p.get('price')
        ]

        print(f"Valid properties: {len(valid_properties)}/{len(properties)}")

        # Save results
        scraper.results = valid_properties
        scraper.save_results(format="json")
        scraper.save_results(format="csv")

        # Print summary
        scraper.print_summary()

        return valid_properties

    except Exception as e:
        print(f"Error during scraping: {e}")
        return []

if __name__ == "__main__":
    results = asyncio.run(complete_workflow())
    print(f"\nTotal properties collected: {len(results)}")
```

## Legal Notice

This scraper is provided for educational purposes. When using this tool:

- Respect website Terms of Service
- Check and follow `robots.txt` rules
- Don't scrape personal or sensitive data without permission
- Consider rate limiting and ethical scraping practices
- Commercial use may require permission from website owners

## Support

For issues or questions about crawl4ai, visit:
- Documentation: https://docs.crawl4ai.com/
- GitHub: https://github.com/unclecode/crawl4ai

## License

This code is provided as-is for educational and research purposes.
