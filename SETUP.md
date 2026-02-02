# Setup Guide - Real Data Newsletter Factory

Quick setup guide to get started with real web scraping.

## Installation

### Step 1: Install Dependencies

```bash
# Install all dependencies
pip install -r requirements.txt

# OR install minimal set (recommended for testing)
pip install requests beautifulsoup4 lxml feedparser python-dateutil fake-useragent tenacity pandas
```

### Step 2: Test Installation

```bash
# Test with sample data first
python example.py
```

Quick test command (recommended):

```bash
./scripts/run_tests.sh
# or
make test
```

### Step 3: Run with Real Data

```bash
# This will scrape live data from web sources
python example_real_data.py
```

## What Happens on First Run?

1. **Checks data freshness** - Sees that no data exists
2. **Starts scraping** - Fetches from TechCrunch, VentureBeat, Crunchbase
3. **Caches data** - Stores in `cache/` directory for 6 hours
4. **Generates newsletter** - Creates comprehensive markdown file
5. **Saves metadata** - Tracks when data was last updated

## Expected Output

```
AI INVESTMENT NEWSLETTER FACTORY - REAL DATA MODE
==============================================================================

📊 Checking data freshness...
**Investments:** ❌ No data
**Events:** ❌ No data

🔄 Refreshing stale data sources...
  ✓ Investments refreshed: True
  ✓ Events refreshed: True

💰 Fetching investment data from web sources...
   Sources: TechCrunch, VentureBeat, Crunchbase News
  ✓ Found 15 recent investments

📅 Fetching AI event data...
   Sources: Eventbrite, Major Conferences
  ✓ Found 8 upcoming events
  ✓ Found 3 entrepreneur-focused events

🧠 Generating AI-powered insights...
  ✓ Generated 5 entrepreneur tips
  ✓ Identified 3 market trends

🏭 Building comprehensive newsletter...
  ✓ Newsletter created with all sections

💾 Newsletter saved to ai_newsletter_real_data.md

✅ Newsletter generation complete!
```

## File Structure After First Run

```
newsletter factory/
├── cache/
│   ├── data_metadata.json        # Freshness tracking
│   ├── [hash].json               # Cached web pages
│   └── ...
├── ai_newsletter_real_data.md    # Generated newsletter
└── ...
```

## Subsequent Runs

On subsequent runs within 6 hours:
- ✅ Uses cached data (instant)
- ⏭️ Skips web scraping
- 📝 Still generates fresh newsletter

After 6 hours:
- 🔄 Auto-refreshes stale data
- 🌐 Scrapes again
- 💾 Updates cache

## Common Issues

### Issue: No investments found

**Cause**: Scraping failed or no recent AI funding news

**Solution**: 
- Check internet connection
- System falls back to sample data automatically
- Check logs for specific errors

### Issue: "Rate limited" or slow performance

**Cause**: Too many requests to same website

**Solution**:
- Wait a few minutes
- Use cached data (automatic)
- Adjust `ScraperConfig.REQUESTS_PER_MINUTE`

### Issue: SSL certificate errors

**Cause**: Certificate verification issues

**Solution**:
```python
# Temporarily disable (not recommended for production)
from scrapers.base_scraper import ScraperConfig
ScraperConfig.VERIFY_SSL = False
```

## Testing Without Scraping

Use the mock data example:

```bash
python example.py  # Uses sample data, no web requests
```

## Force Refresh Cache

```bash
python -c "from data_freshness import refresh_all_data; refresh_all_data(force=True)"
```

## Check Data Status

```bash
python -c "from data_freshness import get_data_status; print(get_data_status())"
```

## Environment Variables (Optional)

Create `.env` file:

```bash
# Optional API keys for enhanced data
CRUNCHBASE_API_KEY=your_key_here
MEETUP_API_KEY=your_key_here

# Scraper configuration
CACHE_EXPIRY_HOURS=6
REQUESTS_PER_MINUTE=30
DELAY_BETWEEN_REQUESTS=2.0
```

## Next Steps

1. ✅ Run `example_real_data.py` successfully
2. 📧 Set up email distribution (see README)
3. ⏰ Schedule with cron for automated newsletters
4. 🎨 Customize sections for your audience
5. 🔌 Add more data sources

## Support

- Check logs in `cache/` directory
- Review `README_REAL_DATA.md` for detailed docs
- Enable debug logging: `logging.basicConfig(level=logging.DEBUG)`

---

Ready to create AI investment newsletters with real data! 🚀
