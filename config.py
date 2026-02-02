# Newsletter Factory Configuration

# This file shows how to configure the newsletter factory
# for different use cases and data sources

from newsletter_factory import NewsletterFactory
from data_sources import MockDataSource, CSVDataSource, APIDataSource
from sections import *
from content_generator import EntrepreneurshipContentGenerator

# ============================================================================
# CONFIGURATION OPTIONS
# ============================================================================

class NewsletterConfig:
    """Configuration for newsletter generation"""
    
    # Newsletter metadata
    TITLE = "AI Investment Weekly: Your Path to AI Entrepreneurship"
    
    # Data source settings
    DATA_SOURCE = "mock"  # Options: 'mock', 'csv', 'api'
    CSV_FILE_PATH = "sample_data.csv"
    API_KEY = "your_api_key_here"
    API_BASE_URL = "https://api.example.com"
    
    # Content settings
    DAYS_LOOKBACK = 7  # How many days of data to include
    MAX_INVESTMENTS = 10  # Max investments to show in highlights
    
    # Section toggles (enable/disable sections)
    INCLUDE_EXECUTIVE_SUMMARY = True
    INCLUDE_INVESTMENT_HIGHLIGHTS = True
    INCLUDE_MARKET_TRENDS = True
    INCLUDE_ENTREPRENEUR_GUIDANCE = True
    INCLUDE_INVESTOR_SPOTLIGHT = True
    
    # Output settings
    OUTPUT_FORMAT = "markdown"  # Future: 'html', 'pdf'
    OUTPUT_FILENAME = "ai_investment_newsletter.md"


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

class PresetConfigs:
    """Pre-configured newsletter templates"""
    
    @staticmethod
    def quick_update():
        """Brief update with just investments and trends"""
        return {
            'title': 'AI Investment Quick Update',
            'sections': ['executive_summary', 'investment_highlights'],
            'max_investments': 5,
            'days_lookback': 3
        }
    
    @staticmethod
    def entrepreneur_focused():
        """Deep dive for aspiring entrepreneurs"""
        return {
            'title': 'AI Entrepreneur Playbook',
            'sections': ['entrepreneur_guidance', 'investor_spotlight', 'market_trends'],
            'days_lookback': 30
        }
    
    @staticmethod
    def investor_research():
        """Focus on investor activity and patterns"""
        return {
            'title': 'AI Investor Intelligence',
            'sections': ['investor_spotlight', 'investment_highlights', 'market_trends'],
            'max_investments': 15,
            'days_lookback': 14
        }
    
    @staticmethod
    def comprehensive():
        """Full newsletter with all sections"""
        return {
            'title': 'AI Investment Weekly: Complete Edition',
            'sections': ['executive_summary', 'investment_highlights', 
                        'market_trends', 'entrepreneur_guidance', 'investor_spotlight'],
            'max_investments': 10,
            'days_lookback': 7
        }


# ============================================================================
# BUILDER FUNCTION
# ============================================================================

def build_newsletter(config=None):
    """
    Build a newsletter based on configuration
    
    Args:
        config: Dict with configuration options (uses defaults if None)
    
    Returns:
        Complete newsletter content as string
    """
    if config is None:
        config = PresetConfigs.comprehensive()
    
    # Initialize data source
    if NewsletterConfig.DATA_SOURCE == 'csv':
        data_source = CSVDataSource(NewsletterConfig.CSV_FILE_PATH)
    elif NewsletterConfig.DATA_SOURCE == 'api':
        data_source = APIDataSource(
            NewsletterConfig.API_KEY,
            NewsletterConfig.API_BASE_URL
        )
    else:
        data_source = MockDataSource()
    
    # Fetch data
    investments = data_source.fetch_investments(
        days_back=config.get('days_lookback', NewsletterConfig.DAYS_LOOKBACK)
    )
    
    # Generate insights
    content_gen = EntrepreneurshipContentGenerator()
    entrepreneur_tips = content_gen.generate_tips_from_investments(investments)
    market_trends = content_gen.generate_market_trends(investments)
    investor_spotlight = content_gen.get_default_investor_spotlight()
    
    # Build newsletter
    factory = NewsletterFactory(title=config.get('title', NewsletterConfig.TITLE))
    
    # Add sections based on config
    sections_map = {
        'executive_summary': lambda: ExecutiveSummarySection(
            summary=f"This period featured {len(investments)} notable investment deals "
                   f"totaling ${sum(inv.amount for inv in investments):.1f}M.",
            key_takeaways=[
                f"${sum(inv.amount for inv in investments):.1f}M in total funding",
                f"{len(set(inv.investee.sector for inv in investments))} active sectors",
                "Strong momentum in AI infrastructure and tooling",
                "Increasing focus on practical AI applications"
            ]
        ),
        'investment_highlights': lambda: InvestmentHighlightsSection(
            investments,
            max_items=config.get('max_investments', NewsletterConfig.MAX_INVESTMENTS)
        ),
        'market_trends': lambda: MarketTrendsSection(market_trends),
        'entrepreneur_guidance': lambda: EntrepreneurGuidanceSection(entrepreneur_tips),
        'investor_spotlight': lambda: InvestorSpotlightSection(investor_spotlight)
    }
    
    for section_name in config.get('sections', []):
        if section_name in sections_map:
            factory.add_section(sections_map[section_name]())
    
    return factory.create()


# ============================================================================
# USAGE EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("Newsletter Factory - Configuration Examples\n")
    print("=" * 60)
    
    # Example 1: Use preset configuration
    print("\n1. Creating comprehensive newsletter...")
    newsletter = build_newsletter(PresetConfigs.comprehensive())
    with open('comprehensive_newsletter.md', 'w') as f:
        f.write(newsletter)
    print("   ✓ Saved to comprehensive_newsletter.md")
    
    # Example 2: Quick update
    print("\n2. Creating quick update...")
    newsletter = build_newsletter(PresetConfigs.quick_update())
    with open('quick_update.md', 'w') as f:
        f.write(newsletter)
    print("   ✓ Saved to quick_update.md")
    
    # Example 3: Entrepreneur-focused
    print("\n3. Creating entrepreneur playbook...")
    newsletter = build_newsletter(PresetConfigs.entrepreneur_focused())
    with open('entrepreneur_playbook.md', 'w') as f:
        f.write(newsletter)
    print("   ✓ Saved to entrepreneur_playbook.md")
    
    # Example 4: Custom configuration
    print("\n4. Creating custom newsletter...")
    custom_config = {
        'title': 'My Custom AI Newsletter',
        'sections': ['investment_highlights', 'market_trends'],
        'max_investments': 3,
        'days_lookback': 14
    }
    newsletter = build_newsletter(custom_config)
    with open('custom_newsletter.md', 'w') as f:
        f.write(newsletter)
    print("   ✓ Saved to custom_newsletter.md")
    
    print("\n" + "=" * 60)
    print("✅ All newsletters generated successfully!")
