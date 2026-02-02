# AI Investment Newsletter Factory - Real Data Edition

A production-ready Python framework for creating newsletters about AI company investments with **real-time web scraping**, event tracking, and automated data freshness monitoring.

## 🎯 What's New: Real Data Features

### ✅ Real-Time Investment Data
- Scrapes **TechCrunch**, **VentureBeat**, and **Crunchbase News**
- Automatic data extraction and parsing
- Intelligent caching (6-hour expiry)
- Fallback to sample data if scraping fails

### ✅ Live Event Tracking
- Scrapes **Eventbrite** for AI events
- Tracks major AI conferences (NeurIPS, ICML, etc.)
- Categorizes by type: Conference, Workshop, Meetup, Hackathon
- Filters events for entrepreneurs

### ✅ Data Freshness System
- Monitors data age automatically
- Auto-refreshes stale data
- Configurable expiry times
- Status reporting

## 🚀 Quick Start

### Installation

```bash
# Install dependencies
pip install -r requirements.txt

# For development without all deps, install minimal set:
pip install requests beautifulsoup4 lxml feedparser python-dateutil fake-useragent tenacity
```

### Run with Real Data

```bash
# Create newsletter with live scraped data
python example_real_data.py
```

This will:
1. Check data freshness
2. Scrape investment news from multiple sources
3. Fetch upcoming AI events
4. Generate insights and guidance
5. Create a comprehensive newsletter
6. Save to `ai_newsletter_real_data.md`

### Quick Test (No Scraping)

```bash
# Use sample data for testing
python example.py
```

## 📊 Data Sources

### Investment Data
| Source | Type | Update Frequency | Cache Duration |
|--------|------|------------------|----------------|
| TechCrunch | RSS Feed | Real-time | 6 hours |
| VentureBeat | Web Scraping | Real-time | 6 hours |
| Crunchbase News | RSS Feed | Real-time | 6 hours |

### Event Data
| Source | Type | Update Frequency | Cache Duration |
|--------|------|------------------|----------------|
| Eventbrite | Web Scraping | Real-time | 24 hours |
| Major Conferences | Curated | Manual | 24 hours |
| Meetup.com | API (requires key) | Real-time | 24 hours |

## 🛠️ Architecture

```
newsletter factory/
├── scrapers/
│   ├── base_scraper.py          # Base infrastructure
│   ├── investment_scrapers.py   # TechCrunch, VentureBeat, etc.
│   ├── event_scrapers.py        # Eventbrite, conferences
│   └── real_data_source.py      # Unified data source
├── cache/                        # Cached scraped data
├── data_freshness.py            # Freshness monitoring
├── event_sections.py            # Event newsletter sections
├── example_real_data.py         # Real data example
└── [other files...]
```

## 💻 Usage Examples

### Basic: Create Newsletter with Real Data

```python
from scrapers.real_data_source import RealTimeDataSource
from newsletter_factory import NewsletterFactory
from sections import InvestmentHighlightsSection

# Fetch real investment data
data_source = RealTimeDataSource(use_cache=True)
investments = data_source.fetch_investments(days_back=7)

# Create newsletter
factory = NewsletterFactory(title="AI Investment Weekly")
newsletter = factory \
    .add_section(InvestmentHighlightsSection(investments)) \
    .create()

print(newsletter)
```

### Advanced: Monitor Data Freshness

```python
from data_freshness import AutoRefreshManager, get_data_status

# Check data age
print(get_data_status())

# Auto-refresh stale data
manager = AutoRefreshManager()
results = manager.refresh_if_needed()

# Force refresh
results = manager.refresh_if_needed(force=True)
```

### Events: Fetch and Display AI Events

```python
from scrapers.event_scrapers import EventAggregator
from event_sections import UpcomingEventsSection

# Fetch events
aggregator = EventAggregator()
events = aggregator.fetch_upcoming_events(days_ahead=90)

# Filter for entrepreneurs
entrepreneur_events = aggregator.get_events_for_entrepreneurs(events)

# Add to newsletter
from newsletter_factory import NewsletterFactory
factory = NewsletterFactory()
factory.add_section(UpcomingEventsSection(events))
```

### Customization: Configure Scraping Behavior

```python
from scrapers.base_scraper import ScraperConfig

# Adjust rate limiting
ScraperConfig.REQUESTS_PER_MINUTE = 20
ScraperConfig.DELAY_BETWEEN_REQUESTS = 3.0

# Adjust cache duration
ScraperConfig.CACHE_EXPIRY_HOURS = 12

# Disable SSL verification (not recommended)
ScraperConfig.VERIFY_SSL = False
```

## 🔧 Configuration

### Environment Variables (Optional)

Create a `.env` file:

```bash
# API Keys (optional, for extended functionality)
CRUNCHBASE_API_KEY=your_key_here
MEETUP_API_KEY=your_key_here

# Scraper Settings
CACHE_EXPIRY_HOURS=6
REQUESTS_PER_MINUTE=30
```

### Freshness Thresholds

Edit `data_freshness.py`:

```python
class DataFreshnessMonitor:
    INVESTMENT_DATA_MAX_AGE = 6   # Hours
    EVENT_DATA_MAX_AGE = 24        # Hours
```

## 📝 Newsletter Sections

### Investment Sections
- **Investment Highlights** - Recent funding rounds with details
- **Market Trends** - AI sector analysis
- **Investor Spotlight** - Active VC profiles

### Event Sections
- **Upcoming Events** - Categorized by timeframe
- **Events for Entrepreneurs** - Founder-focused opportunities  
- **Event Calendar** - Table view of all events

### Guidance Sections
- **Entrepreneur Playbook** - Actionable tips by category
- **Executive Summary** - Key takeaways

## 🤖 How Scraping Works

### Rate Limiting
- Polite scraping with configurable delays
- Respects robots.txt
- Random user agent rotation
- Request throttling

### Caching Strategy
```
1. Check cache for existing data
2. If fresh (< 6 hours old), return cached
3. If stale, fetch new data
4. Parse and validate
5. Cache for future requests
```

### Error Handling
- Graceful fallback to sample data
- Retry logic with exponential backoff
- Detailed logging
- Cache prevents data loss

## 🚨 Troubleshooting

### No data returned
- **Cause**: Website structure changed or rate limited
- **Solution**: Check logs, clear cache, or wait before retrying

```python
# Clear cache
from scrapers.base_scraper import CacheManager
cache = CacheManager()
cache.clear_expired(max_age_hours=0)
```

### Scraping is slow
- **Cause**: Rate limiting and politeness delays
- **Solution**: Enable caching (default), increase cache duration

### SSL errors
- **Cause**: Certificate issues
- **Solution**: Update certificates or disable verification (not recommended)

## 🎓 Advanced Features

### Custom Scrapers

Create your own scraper:

```python
from scrapers.base_scraper import BaseScraper

class MyCustomScraper(BaseScraper):
    def scrape(self):
        html = self._fetch_url("https://example.com")
        soup = self._parse_html(html)
        # Your parsing logic
        return data
```

### Scheduled Updates

Use with cron for automated newsletters:

```bash
# Run every 6 hours
0 */6 * * * cd /path/to/newsletter-factory && python example_real_data.py
```

### Integration with Email

```python
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

# Create newsletter
newsletter = create_newsletter_with_real_data()

# Send via email
message = Mail(
    from_email='your@email.com',
    to_emails='subscriber@email.com',
    subject='AI Investment Weekly',
    html_content=newsletter)

sg = SendGridAPIClient('YOUR_API_KEY')
sg.send(message)
```

## 📊 Data Quality

- ✅ **Deduplication**: Removes duplicate investments
- ✅ **Validation**: Checks required fields
- ✅ **Normalization**: Standardizes company names, amounts
- ✅ **Source Attribution**: Tracks data origin
- ✅ **Fallback**: Uses sample data if scraping fails

## 🔐 Legal & Ethics

- Respects robots.txt
- Rate limiting prevents server overload
- Caching reduces request frequency
- User agent identification
- For personal/educational use
- Check website ToS before commercial use

## 🤝 Contributing

Add new data sources:

1. Create scraper in `scrapers/`
2. Extend `InvestmentDataAggregator` or `EventAggregator`
3. Add tests
4. Update documentation

## 📄 License

MIT License - See LICENSE file

---

**Built to democratize access to AI investment intelligence for aspiring entrepreneurs.** 🚀

For questions or issues, check the logs in `cache/` directory.
