# AI Investment Newsletter Factory

A reusable Python framework for creating newsletters about AI company investments, designed to help aspiring entrepreneurs stay informed and learn how to break into the AI industry.

## 🎯 Purpose

This factory enables you to:
- Track and report on AI investment activities (who's investing in whom)
- Analyze market trends in the AI ecosystem
- Provide actionable entrepreneurship guidance
- Spotlight active investors and funding opportunities
- Generate professional newsletters automatically

## 🏗️ Architecture

The project uses the **Factory Pattern** for flexible newsletter creation:

```
newsletter_factory.py   → Core factory and base classes
models.py              → Data models (Investment, Company, etc.)
data_sources.py        → Investment data fetching (API, CSV, Mock)
sections.py            → Newsletter section generators
content_generator.py   → AI-powered insights and tips
example.py            → Usage examples
```

## 🚀 Quick Start

### Basic Usage

```python
from newsletter_factory import NewsletterFactory
from data_sources import MockDataSource
from sections import InvestmentHighlightsSection

# Fetch investment data
data_source = MockDataSource()
investments = data_source.fetch_investments(days_back=7)

# Create newsletter
factory = NewsletterFactory(title="AI Investment Weekly")
newsletter = factory \
    .add_section(InvestmentHighlightsSection(investments)) \
    .create()

print(newsletter)
```

### Run the Example

```bash
python example.py
```

This generates a complete newsletter with:
- Executive summary
- Investment highlights
- Market trends analysis
- Entrepreneur guidance
- Investor spotlight

## 📊 Data Sources

### Mock Data (for testing)
```python
from data_sources import MockDataSource
source = MockDataSource()
investments = source.fetch_investments()
```

### CSV Import
```python
from data_sources import CSVDataSource
source = CSVDataSource('investments.csv')
investments = source.fetch_investments()
```

### External API (customize)
```python
from data_sources import APIDataSource
source = APIDataSource(api_key='your_key', base_url='https://api.example.com')
investments = source.fetch_investments()
```

## 🧩 Available Sections

| Section | Description |
|---------|-------------|
| `ExecutiveSummarySection` | Brief overview and key takeaways |
| `InvestmentHighlightsSection` | Recent funding rounds and deals |
| `MarketTrendsSection` | Analysis of market movements |
| `EntrepreneurGuidanceSection` | Actionable advice for founders |
| `InvestorSpotlightSection` | Active investor profiles |

## 🎨 Customization

### Create Custom Sections

```python
from newsletter_factory import NewsletterSection

class CustomSection(NewsletterSection):
    def __init__(self, data):
        self.data = data
    
    def generate(self) -> str:
        return f"## My Custom Section\n\n{self.data}"

# Use it
factory.add_section(CustomSection("Custom content"))
```

### Generate Smart Insights

```python
from content_generator import EntrepreneurshipContentGenerator

gen = EntrepreneurshipContentGenerator()

# Auto-generate tips from investment data
tips = gen.generate_tips_from_investments(investments)

# Identify market trends
trends = gen.generate_market_trends(investments)
```

## 📝 Example Newsletter Output

```markdown
# AI Investment Weekly: Your Path to AI Entrepreneurship
*February 01, 2026*

---

## 📋 Executive Summary

This week saw strong investment activity in AI...

**Key Takeaways:**
- $11,082.4M deployed across 5 deals
- Open-source AI models gaining serious investor attention
...

## 💰 Investment Highlights

### Anthropic - $450.0M
- **Investor:** Google Ventures
- **Stage:** Series C
- **Sector:** LLM
...
```

## 🔧 Requirements

- Python 3.8+
- No external dependencies for basic usage
- Optional: `requests` for API data sources

## 📚 Use Cases

1. **Weekly Investment Newsletter**: Track AI funding rounds
2. **Investor Research**: Analyze active VCs and investment patterns
3. **Entrepreneur Education**: Learn from successful funding strategies
4. **Market Analysis**: Identify hot sectors and emerging trends
5. **Deal Flow Tracking**: Monitor competitive landscape

## 🤝 Contributing

To add new features:
1. Create custom `NewsletterSection` classes in `sections.py`
2. Add new `DataSource` implementations in `data_sources.py`
3. Extend `EntrepreneurshipContentGenerator` for new insights
4. Update examples to showcase new functionality

## 📖 Learn More

- [Factory Pattern](https://refactoring.guru/design-patterns/factory-method)
- [Crunchbase API](https://data.crunchbase.com/docs) - Investment data
- [Y Combinator](https://www.ycombinator.com/) - Startup resources
- [NFX Signal](https://signal.nfx.com/) - Investor database

## 📄 License

MIT License - feel free to use this for your newsletters!

---

**Built to help aspiring AI entrepreneurs navigate the investment landscape and find their path into the industry.** 🚀
