"""
Example usage of the Newsletter Factory

This demonstrates how to use the factory to create a comprehensive
AI investment newsletter with entrepreneurship guidance.
"""

from newsletter_factory import NewsletterFactory
from data_sources import MockDataSource
from content_generator import EntrepreneurshipContentGenerator
from sections import (
    ExecutiveSummarySection,
    InvestmentHighlightsSection,
    MarketTrendsSection,
    EntrepreneurGuidanceSection,
    InvestorSpotlightSection
)


def create_weekly_newsletter():
    """Create a complete weekly AI investment newsletter"""
    
    # Step 1: Fetch investment data
    print("📊 Fetching investment data...")
    data_source = MockDataSource()
    investments = data_source.fetch_investments(days_back=7)
    print(f"✓ Found {len(investments)} investments\n")
    
    # Step 2: Generate insights and guidance
    print("🧠 Generating entrepreneurship insights...")
    content_gen = EntrepreneurshipContentGenerator()
    
    entrepreneur_tips = content_gen.generate_tips_from_investments(investments)
    market_trends = content_gen.generate_market_trends(investments)
    investor_spotlight = content_gen.get_default_investor_spotlight()
    print(f"✓ Generated {len(entrepreneur_tips)} tips and {len(market_trends)} trends\n")
    
    # Step 3: Create newsletter using factory pattern
    print("🏭 Building newsletter...")
    factory = NewsletterFactory(title="AI Investment Weekly: Your Path to AI Entrepreneurship")
    
    # Build newsletter with sections
    newsletter = factory \
        .add_section(ExecutiveSummarySection(
            summary="This week saw strong investment activity in AI, with major funding rounds "
                   "across infrastructure, LLMs, and consumer AI. The market continues to reward "
                   "companies building foundational models and developer tools.",
            key_takeaways=[
                f"${sum(inv.amount for inv in investments):.1f}M deployed across {len(investments)} deals",
                "Open-source AI models gaining serious investor attention",
                "Enterprise AI adoption accelerating beyond experimentation phase",
                "Developer tools and infrastructure remain hot investment areas"
            ]
        )) \
        .add_section(InvestmentHighlightsSection(investments)) \
        .add_section(MarketTrendsSection(market_trends)) \
        .add_section(EntrepreneurGuidanceSection(entrepreneur_tips)) \
        .add_section(InvestorSpotlightSection(investor_spotlight)) \
        .create()
    
    print("✓ Newsletter created!\n")
    
    return newsletter


def save_newsletter(content: str, filename: str = "newsletter.md"):
    """Save newsletter to a markdown file"""
    with open(filename, 'w') as f:
        f.write(content)
    print(f"💾 Newsletter saved to {filename}")


def main():
    """Main execution"""
    print("=" * 60)
    print("AI INVESTMENT NEWSLETTER FACTORY")
    print("=" * 60)
    print()
    
    # Create the newsletter
    newsletter_content = create_weekly_newsletter()
    
    # Save to file
    save_newsletter(newsletter_content, "ai_investment_newsletter.md")
    
    # Print preview
    print("\n" + "=" * 60)
    print("NEWSLETTER PREVIEW (first 1000 chars)")
    print("=" * 60)
    print(newsletter_content[:1000])
    print("\n[... continued in ai_investment_newsletter.md ...]")
    print("\n✅ Newsletter generation complete!")


if __name__ == "__main__":
    main()
