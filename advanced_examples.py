"""
Advanced usage examples and customization guides
"""

from newsletter_factory import NewsletterFactory, NewsletterSection
from data_sources import MockDataSource
from sections import *
from content_generator import EntrepreneurshipContentGenerator
from models import Company, Investment
from newsletter_factory import InvestmentStage
from datetime import datetime, timedelta


# ============================================================================
# EXAMPLE 1: Creating a Custom Section
# ============================================================================

class WeeklyQuoteSection(NewsletterSection):
    """Add inspirational quotes for entrepreneurs"""
    
    def __init__(self, quote: str, author: str):
        self.quote = quote
        self.author = author
    
    def generate(self) -> str:
        return f"""## 💭 Weekly Inspiration

> "{self.quote}"
> 
> — *{self.author}*

"""


class ResourcesSection(NewsletterSection):
    """Curated resources for AI entrepreneurs"""
    
    def __init__(self, resources: dict):
        self.resources = resources
    
    def generate(self) -> str:
        content = ["## 📚 Curated Resources", ""]
        
        for category, items in self.resources.items():
            content.append(f"### {category}")
            for item in items:
                content.append(f"- {item}")
            content.append("")
        
        return "\n".join(content)


# ============================================================================
# EXAMPLE 2: Multi-Week Trend Analysis
# ============================================================================

class MultiWeekAnalyzer:
    """Analyze trends across multiple weeks"""
    
    def __init__(self):
        self.weeks_data = []
    
    def add_week_data(self, investments, week_number):
        """Add data for a specific week"""
        self.weeks_data.append({
            'week': week_number,
            'investments': investments,
            'total_funding': sum(inv.amount for inv in investments),
            'deal_count': len(investments)
        })
    
    def generate_trend_report(self) -> str:
        """Generate multi-week trend analysis"""
        if not self.weeks_data:
            return "No data available"
        
        report = ["## 📊 Multi-Week Trend Analysis\n"]
        
        # Calculate averages
        avg_funding = sum(w['total_funding'] for w in self.weeks_data) / len(self.weeks_data)
        avg_deals = sum(w['deal_count'] for w in self.weeks_data) / len(self.weeks_data)
        
        report.append(f"**{len(self.weeks_data)}-Week Summary:**")
        report.append(f"- Average weekly funding: ${avg_funding:.1f}M")
        report.append(f"- Average deals per week: {avg_deals:.1f}")
        report.append("")
        
        # Week by week
        report.append("**Week-by-Week:**")
        for week_data in self.weeks_data:
            report.append(
                f"- Week {week_data['week']}: "
                f"${week_data['total_funding']:.1f}M across {week_data['deal_count']} deals"
            )
        
        return "\n".join(report)


# ============================================================================
# EXAMPLE 3: Filtering and Segmentation
# ============================================================================

class InvestmentFilter:
    """Filter investments by various criteria"""
    
    @staticmethod
    def by_sector(investments, sector: str):
        """Filter investments by sector"""
        return [inv for inv in investments if inv.investee.sector == sector]
    
    @staticmethod
    def by_stage(investments, stage: InvestmentStage):
        """Filter investments by funding stage"""
        return [inv for inv in investments if inv.stage == stage]
    
    @staticmethod
    def by_amount(investments, min_amount: float = 0, max_amount: float = float('inf')):
        """Filter investments by amount range"""
        return [inv for inv in investments 
                if min_amount <= inv.amount <= max_amount]
    
    @staticmethod
    def recent(investments, days: int = 7):
        """Get investments from last N days"""
        cutoff_date = datetime.now() - timedelta(days=days)
        return [inv for inv in investments if inv.date >= cutoff_date]


# ============================================================================
# EXAMPLE 4: Themed Newsletters
# ============================================================================

def create_sector_focused_newsletter(sector: str):
    """Create a newsletter focused on a specific sector"""
    
    data_source = MockDataSource()
    all_investments = data_source.fetch_investments()
    
    # Filter to sector
    sector_investments = InvestmentFilter.by_sector(all_investments, sector)
    
    if not sector_investments:
        return f"No investments found in {sector} sector"
    
    # Generate content
    gen = EntrepreneurshipContentGenerator()
    tips = gen.generate_tips_from_investments(sector_investments)
    
    # Build newsletter
    factory = NewsletterFactory(title=f"{sector} Investment Spotlight")
    
    newsletter = factory \
        .add_section(ExecutiveSummarySection(
            summary=f"Deep dive into {sector} investment activity.",
            key_takeaways=[
                f"{len(sector_investments)} deals in {sector}",
                f"Total funding: ${sum(inv.amount for inv in sector_investments):.1f}M"
            ]
        )) \
        .add_section(InvestmentHighlightsSection(sector_investments)) \
        .add_section(EntrepreneurGuidanceSection(tips)) \
        .create()
    
    return newsletter


def create_stage_focused_newsletter(stage: InvestmentStage):
    """Create a newsletter focused on a funding stage"""
    
    data_source = MockDataSource()
    all_investments = data_source.fetch_investments()
    
    # Filter to stage
    stage_investments = InvestmentFilter.by_stage(all_investments, stage)
    
    factory = NewsletterFactory(title=f"{stage.value} Round Analysis")
    
    newsletter = factory \
        .add_section(InvestmentHighlightsSection(stage_investments)) \
        .create()
    
    return newsletter


# ============================================================================
# EXAMPLE 5: Newsletter with Custom Branding
# ============================================================================

class BrandedNewsletterFactory(NewsletterFactory):
    """Extended factory with branding options"""
    
    def __init__(self, title: str, brand_name: str = "", brand_tagline: str = ""):
        super().__init__(title)
        self.brand_name = brand_name
        self.brand_tagline = brand_tagline
    
    def create(self) -> str:
        """Generate newsletter with branding"""
        newsletter = []
        
        # Brand header
        if self.brand_name:
            newsletter.append(f"# {self.brand_name}")
            newsletter.append(f"*{self.brand_tagline}*\n")
        
        # Newsletter title
        newsletter.append(f"## {self.title}")
        newsletter.append(f"*{self.date.strftime('%B %d, %Y')}*")
        newsletter.append("\n---\n")
        
        # Sections
        for section in self.sections:
            newsletter.append(section.generate())
            newsletter.append("\n")
        
        # Footer
        newsletter.append("---")
        newsletter.append(f"\n*© {self.date.year} {self.brand_name}. "
                        f"Helping entrepreneurs navigate the AI landscape.*")
        
        return "\n".join(newsletter)


# ============================================================================
# RUN EXAMPLES
# ============================================================================

if __name__ == "__main__":
    print("Advanced Newsletter Factory Examples")
    print("=" * 60)
    
    # Example 1: Custom sections
    print("\n1. Newsletter with custom sections...")
    factory = NewsletterFactory(title="Enhanced Newsletter")
    factory.add_section(WeeklyQuoteSection(
        "The best time to plant a tree was 20 years ago. The second best time is now.",
        "Chinese Proverb"
    ))
    factory.add_section(ResourcesSection({
        "Learning": [
            "Fast.ai - Deep Learning Course",
            "Hugging Face Tutorials",
            "OpenAI Cookbook"
        ],
        "Networking": [
            "AI Founders Network",
            "Local AI Meetups",
            "Y Combinator Community"
        ]
    }))
    
    newsletter = factory.create()
    with open('enhanced_newsletter.md', 'w') as f:
        f.write(newsletter)
    print("   ✓ Saved to enhanced_newsletter.md")
    
    # Example 2: Sector-focused
    print("\n2. Creating LLM-focused newsletter...")
    llm_newsletter = create_sector_focused_newsletter("LLM")
    with open('llm_newsletter.md', 'w') as f:
        f.write(llm_newsletter)
    print("   ✓ Saved to llm_newsletter.md")
    
    # Example 3: Branded newsletter
    print("\n3. Creating branded newsletter...")
    branded_factory = BrandedNewsletterFactory(
        title="Weekly AI Investment Digest",
        brand_name="AI Venture Insights",
        brand_tagline="Your guide to AI entrepreneurship"
    )
    
    data_source = MockDataSource()
    investments = data_source.fetch_investments()
    
    branded_factory.add_section(InvestmentHighlightsSection(investments[:5]))
    branded_newsletter = branded_factory.create()
    
    with open('branded_newsletter.md', 'w') as f:
        f.write(branded_newsletter)
    print("   ✓ Saved to branded_newsletter.md")
    
    # Example 4: Multi-week analysis
    print("\n4. Creating multi-week analysis...")
    analyzer = MultiWeekAnalyzer()
    
    # Simulate multiple weeks of data
    for week in range(1, 5):
        analyzer.add_week_data(investments, week)
    
    trend_report = analyzer.generate_trend_report()
    print(trend_report)
    
    print("\n" + "=" * 60)
    print("✅ All advanced examples completed!")
