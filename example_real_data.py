"""
Example using real data sources with web scraping and events

This demonstrates how to create newsletters with:
- Real investment data from TechCrunch, VentureBeat, Crunchbase
- Real AI events from Eventbrite and major conferences
- Automatic data freshness monitoring
- Caching to avoid excessive requests
"""

from newsletter_factory import NewsletterFactory
from scrapers.real_data_source import RealTimeDataSource
from scrapers.event_scrapers import EventAggregator
from content_generator import EntrepreneurshipContentGenerator
from sections import (
    ExecutiveSummarySection,
    InvestmentHighlightsSection,
    MarketTrendsSection,
    EntrepreneurGuidanceSection,
    InvestorSpotlightSection
)
from event_sections import (
    UpcomingEventsSection,
    EventsForEntrepreneursSection,
    EventCalendarSection
)
from data_freshness import AutoRefreshManager, get_data_status
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_newsletter_with_real_data():
    """
    Create a newsletter using real scraped data
    """
    
    print("=" * 70)
    print("AI INVESTMENT NEWSLETTER FACTORY - REAL DATA MODE")
    print("=" * 70)
    print()
    
    # Step 1: Check data freshness
    print("📊 Checking data freshness...")
    print(get_data_status())
    print()
    
    # Step 2: Auto-refresh stale data
    print("🔄 Refreshing stale data sources...")
    refresh_manager = AutoRefreshManager()
    refresh_results = refresh_manager.refresh_if_needed(force=False)
    
    print(f"  ✓ Investments refreshed: {refresh_results['investments_refreshed']}")
    print(f"  ✓ Events refreshed: {refresh_results['events_refreshed']}")
    
    if refresh_results['errors']:
        print(f"  ⚠️ Errors encountered: {len(refresh_results['errors'])}")
        for error in refresh_results['errors']:
            print(f"     - {error}")
    print()
    
    # Step 3: Fetch real investment data
    print("💰 Fetching investment data from web sources...")
    print("   Sources: TechCrunch, VentureBeat, Crunchbase News")
    
    data_source = RealTimeDataSource(use_cache=True)
    investments = data_source.fetch_investments(days_back=7)
    
    print(f"  ✓ Found {len(investments)} recent investments")
    print()
    
    # Step 4: Fetch real event data
    print("📅 Fetching AI event data...")
    print("   Sources: Eventbrite, Major Conferences")
    
    event_aggregator = EventAggregator()
    all_events = event_aggregator.fetch_upcoming_events(days_ahead=90)
    entrepreneur_events = event_aggregator.get_events_for_entrepreneurs(all_events)
    
    print(f"  ✓ Found {len(all_events)} upcoming events")
    print(f"  ✓ Found {len(entrepreneur_events)} entrepreneur-focused events")
    print()
    
    # Step 5: Generate insights
    print("🧠 Generating AI-powered insights...")
    content_gen = EntrepreneurshipContentGenerator()
    
    entrepreneur_tips = content_gen.generate_tips_from_investments(investments)
    market_trends = content_gen.generate_market_trends(investments)
    investor_spotlight = content_gen.get_default_investor_spotlight()
    
    print(f"  ✓ Generated {len(entrepreneur_tips)} entrepreneur tips")
    print(f"  ✓ Identified {len(market_trends)} market trends")
    print()
    
    # Step 6: Build newsletter
    print("🏭 Building comprehensive newsletter...")
    
    factory = NewsletterFactory(
        title="AI Investment Weekly: Your Path to AI Entrepreneurship"
    )
    
    # Calculate summary stats
    total_funding = sum(inv.amount for inv in investments)
    sectors = set(inv.investee.sector for inv in investments)
    
    newsletter = factory \
        .add_section(ExecutiveSummarySection(
            summary=f"This week's newsletter features {len(investments)} investment deals "
                   f"totaling ${total_funding:.1f}M, plus {len(all_events)} upcoming events "
                   f"to help you break into the AI industry.",
            key_takeaways=[
                f"${total_funding:.1f}M deployed across {len(investments)} deals",
                f"{len(sectors)} active sectors receiving funding",
                f"{len(entrepreneur_events)} entrepreneur events this quarter",
                "Real-time data updated every 6 hours"
            ]
        )) \
        .add_section(InvestmentHighlightsSection(investments, max_items=10)) \
        .add_section(MarketTrendsSection(market_trends)) \
        .add_section(UpcomingEventsSection(all_events, max_items=10)) \
        .add_section(EventsForEntrepreneursSection(entrepreneur_events[:5])) \
        .add_section(EntrepreneurGuidanceSection(entrepreneur_tips)) \
        .add_section(InvestorSpotlightSection(investor_spotlight)) \
        .add_section(EventCalendarSection(all_events[:15])) \
        .create()
    
    print("  ✓ Newsletter created with all sections")
    print()
    
    return newsletter


def save_newsletter(content: str, filename: str = "ai_newsletter_real_data.md"):
    """Save newsletter to file"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"💾 Newsletter saved to {filename}")


def main():
    """Main execution"""
    
    try:
        # Create newsletter with real data
        newsletter_content = create_newsletter_with_real_data()
        
        # Save to file
        save_newsletter(newsletter_content)
        
        # Print preview
        print()
        print("=" * 70)
        print("NEWSLETTER PREVIEW (first 1500 chars)")
        print("=" * 70)
        print(newsletter_content[:1500])
        print("\n[... continued in ai_newsletter_real_data.md ...]")
        print()
        
        # Show data freshness status
        print("=" * 70)
        print("DATA FRESHNESS REPORT")
        print("=" * 70)
        print(get_data_status())
        
        print()
        print("✅ Newsletter generation complete!")
        print()
        print("💡 Tips:")
        print("   - Data is cached for 6 hours to avoid excessive requests")
        print("   - Run again to use cached data (much faster)")
        print("   - Force refresh with: refresh_all_data(force=True)")
        print("   - Check data age with: get_data_status()")
        
    except Exception as e:
        logger.error(f"Error creating newsletter: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nNote: Web scraping requires internet connection and may fail if:")
        print("  - Websites have changed their structure")
        print("  - You're being rate-limited")
        print("  - Network issues")
        print("\nThe system will fall back to sample data if scraping fails.")


if __name__ == "__main__":
    main()
