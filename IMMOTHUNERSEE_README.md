# ImmoThunersee.ch Property Scraper

Specialized web scraper for extracting property listings from **www.immothunersee.ch**.

## Overview

This scraper is specifically designed for ImmoThunersee.ch, a real estate platform for the Thun region. It extracts:

- Property titles
- Prices (sale/rent)
- Locations/addresses
- Number of rooms
- Living area (m²)
- Property descriptions
- Property type
- Images
- Direct links to listings

## Files

- **`immothunersee_scraper.py`** - Full-featured scraper with inspect mode
- **`immothunersee_simple.py`** - Simple version for quick testing
- **`IMMOTHUNERSEE_README.md`** - This documentation

## Quick Start

### Method 1: Simple Scraper (Fastest)

```bash
python immothunersee_simple.py
```

This will scrape the main listings page and save results to `immothunersee_properties.json`.

### Method 2: Full Scraper (More Features)

```bash
# Scrape 1 page
python immothunersee_scraper.py --scrape

# Scrape multiple pages
python immothunersee_scraper.py --scrape --pages 5

# Scrape custom URL
python immothunersee_scraper.py --scrape --url "https://www.immothunersee.ch/custom-url"
```

## Inspect Mode (Troubleshooting)

If the scraper doesn't find properties, use inspect mode to analyze the page structure:

```bash
python immothunersee_scraper.py --inspect
```

This will:
1. Download the HTML structure
2. Save it to `immothunersee_data/page_structure.html`
3. Save markdown version to `immothunersee_data/page_content.md`
4. List all property-related links found

**Then you can:**
1. Open `page_structure.html` in a browser
2. Use DevTools (F12) to inspect property elements
3. Update CSS selectors in the script if needed

## Usage Examples

### Example 1: Basic Scraping

```python
import asyncio
from immothunersee_scraper import ImmoThunerseeScr

async def main():
    scraper = ImmoThunerseeScr()

    # Scrape properties
    properties = await scraper.scrape_properties(max_pages=1)

    # Save results
    scraper.save_results(format="json")
    scraper.save_results(format="csv")

    # Print summary
    scraper.print_summary()

asyncio.run(main())
```

### Example 2: Multiple Pages

```python
import asyncio
from immothunersee_scraper import ImmoThunerseeScr

async def main():
    scraper = ImmoThunerseeScr(output_dir="all_properties")

    # Scrape first 3 pages
    properties = await scraper.scrape_properties(max_pages=3)

    print(f"Total properties found: {len(properties)}")

    # Filter by criteria
    expensive = [p for p in properties if 'CHF' in p.get('price', '')]
    print(f"Properties with CHF pricing: {len(expensive)}")

    scraper.save_results(format="json")

asyncio.run(main())
```

### Example 3: Inspect and Scrape

```python
import asyncio
from immothunersee_scraper import ImmoThunerseeScr

async def main():
    scraper = ImmoThunerseeScr()

    # First, inspect the page
    print("Step 1: Inspecting page structure...")
    await scraper.inspect_page()

    # Then scrape
    print("\nStep 2: Scraping properties...")
    await scraper.scrape_properties()

    scraper.save_results(format="json")

asyncio.run(main())
```

## Command Line Options

```bash
# Inspect mode
python immothunersee_scraper.py --inspect

# Scrape mode (default)
python immothunersee_scraper.py --scrape

# Scrape multiple pages
python immothunersee_scraper.py --scrape --pages 5

# Scrape custom URL
python immothunersee_scraper.py --scrape --url "https://www.immothunersee.ch/kaufen"

# Combine options
python immothunersee_scraper.py --scrape --url "https://www.immothunersee.ch/mieten" --pages 3
```

## Output Files

### JSON Format
```json
[
  {
    "title": "3.5-Zimmer-Wohnung in Thun",
    "price": "CHF 1,800 / Monat",
    "location": "Thun",
    "rooms": "3.5",
    "area": "95 m²",
    "type": "Wohnung",
    "description": "Schöne Wohnung mit Seeblick...",
    "link": "https://www.immothunersee.ch/detail/12345",
    "image": "https://www.immothunersee.ch/images/property.jpg"
  }
]
```

### CSV Format
All properties in spreadsheet format with columns for each field.

## Customizing the Scraper

### Update CSS Selectors

If the website structure changes, update the schema in `get_extraction_schema()`:

```python
def get_extraction_schema(self) -> dict:
    return {
        "name": "ImmoThunerseeProperties",
        "baseSelector": "div.new-property-class",  # Update this
        "fields": [
            {
                "name": "title",
                "selector": "h2.new-title-class",  # Update selectors
                "type": "text"
            },
            # ... more fields
        ]
    }
```

### Add New Fields

Add more fields to extract:

```python
{
    "name": "year_built",
    "selector": "[class*='baujahr']",
    "type": "text"
},
{
    "name": "property_id",
    "selector": "[data-id]",
    "type": "attribute",
    "attribute": "data-id"
}
```

### Change Wait Time

If properties don't load in time:

```python
config = CrawlerRunConfig(
    delay_before_return_html=5000,  # Wait 5 seconds instead of 3
    page_timeout=60000,              # Increase timeout to 60 seconds
)
```

## Troubleshooting

### Issue: No properties found

**Solution:**
1. Run inspect mode: `python immothunersee_scraper.py --inspect`
2. Check `page_structure.html` to see actual HTML
3. Update CSS selectors based on actual structure
4. Test with simple scraper first

### Issue: Incomplete data

**Cause:** Some fields may not exist on all properties

**Solution:**
```python
# Filter for complete properties
complete_properties = [
    p for p in properties
    if p.get('title') and p.get('price') and p.get('location')
]
```

### Issue: Images/Links are relative URLs

**Solution:** The scraper automatically converts relative URLs to absolute URLs:
```python
# Automatic conversion
if not prop['link'].startswith('http'):
    prop['link'] = f"{self.BASE_URL}{prop['link']}"
```

### Issue: Rate limiting or blocked

**Solution:**
1. Increase delay between requests:
   ```python
   await asyncio.sleep(5)  # Wait 5 seconds between pages
   ```

2. Use different user agents (already implemented with `user_agent_mode="random"`)

3. Scrape fewer pages at a time

## Best Practices

### 1. Respectful Scraping

```python
# Add delays between requests
await asyncio.sleep(2)  # 2 seconds between pages

# Don't scrape too many pages at once
max_pages = 5  # Limit to 5 pages per run
```

### 2. Error Handling

```python
try:
    properties = await scraper.scrape_properties()
    if properties:
        scraper.save_results(format="json")
except Exception as e:
    print(f"Error: {e}")
    # Save partial results
    if scraper.results:
        scraper.save_results(format="json")
```

### 3. Data Validation

```python
# Validate before saving
valid_properties = []
for prop in properties:
    if prop.get('title') and prop.get('price'):
        # Clean price
        prop['price'] = prop['price'].strip()
        # Ensure absolute URL
        if prop.get('link') and not prop['link'].startswith('http'):
            prop['link'] = f"https://www.immothunersee.ch{prop['link']}"
        valid_properties.append(prop)

scraper.results = valid_properties
```

### 4. Regular Updates

Website structures change. Schedule regular checks:

```bash
# Run weekly to check if scraper still works
# Add to cron or task scheduler
0 0 * * 0 python immothunersee_scraper.py --scrape --pages 1
```

## Advanced Features

### Filter by Property Type

```python
properties = await scraper.scrape_properties()

# Filter apartments
apartments = [p for p in properties if 'wohnung' in p.get('type', '').lower()]

# Filter houses
houses = [p for p in properties if 'haus' in p.get('type', '').lower()]
```

### Extract Detailed Info

Extend the scraper to get detailed property pages:

```python
async def get_property_details(self, url: str) -> dict:
    """Scrape detailed information from a property page."""
    config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=2000
    )

    result = await crawler.arun(url=url, config=config)
    # Extract detailed info...
    return details
```

### Schedule Regular Scraping

```python
import asyncio
from datetime import datetime

async def daily_scrape():
    """Run daily scraping task."""
    while True:
        print(f"Starting scrape at {datetime.now()}")

        scraper = ImmoThunerseeScr()
        await scraper.scrape_properties(max_pages=3)
        scraper.save_results(format="json")

        # Wait 24 hours
        await asyncio.sleep(86400)

asyncio.run(daily_scrape())
```

## Technical Details

### Dependencies

- **crawl4ai** - Main scraping framework
- **asyncio** - Asynchronous operation
- **json** - JSON parsing
- **csv** - CSV export

### Browser Configuration

```python
BrowserConfig(
    headless=True,              # No visible browser window
    user_agent_mode="random",   # Random user agent each request
    java_script_enabled=True,   # Execute JavaScript
    viewport_width=1920,        # Screen resolution
    viewport_height=1080
)
```

### Extraction Strategy

Uses **JsonCssExtractionStrategy** for structured data extraction:
- Fast and efficient
- No LLM costs
- Requires correct CSS selectors
- Returns JSON format

## Performance

- **Single page**: ~3-5 seconds
- **Multiple pages (5)**: ~15-25 seconds
- **Memory usage**: Low (~50-100MB)
- **Network**: Minimal bandwidth

## Legal & Ethical Considerations

✅ **Allowed:**
- Personal research
- Market analysis
- Educational purposes
- Non-commercial use

⚠️ **Be Careful:**
- Respect robots.txt
- Don't overload servers
- Add appropriate delays
- Check Terms of Service

❌ **Not Allowed:**
- Reselling scraped data
- Commercial use without permission
- Bypassing authentication
- Scraping personal user data

## Support

For issues with:
- **This scraper**: Check the troubleshooting section above
- **crawl4ai**: Visit https://docs.crawl4ai.com/
- **Website changes**: Run inspect mode and update selectors

## Example Complete Workflow

```python
import asyncio
from immothunersee_scraper import ImmoThunerseeScr

async def complete_workflow():
    """Complete workflow with all features."""

    # Initialize
    scraper = ImmoThunerseeScr(output_dir="thun_listings")

    # Step 1: Inspect (optional, for first run)
    print("Step 1: Inspecting page...")
    await scraper.inspect_page()

    # Step 2: Scrape properties
    print("\nStep 2: Scraping properties...")
    properties = await scraper.scrape_properties(max_pages=3)

    # Step 3: Filter and validate
    print("\nStep 3: Validating data...")
    valid = [p for p in properties if p.get('title') and p.get('price')]
    print(f"Valid properties: {len(valid)}/{len(properties)}")

    # Step 4: Save in multiple formats
    print("\nStep 4: Saving results...")
    scraper.results = valid
    scraper.save_results(format="json")
    scraper.save_results(format="csv")

    # Step 5: Display summary
    print("\nStep 5: Summary")
    scraper.print_summary()

    return valid

if __name__ == "__main__":
    results = asyncio.run(complete_workflow())
    print(f"\n✨ Done! Collected {len(results)} properties")
```

## License

Provided as-is for educational purposes. Use responsibly and ethically.
