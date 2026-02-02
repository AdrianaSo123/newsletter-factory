"""
Content sections for the newsletter
"""

from typing import List
from newsletter_factory import NewsletterSection
from models import Investment, EntrepreneurTip, MarketTrend


class InvestmentHighlightsSection(NewsletterSection):
    """Section showcasing recent investment activities"""
    
    def __init__(self, investments: List[Investment], max_items: int = 10):
        self.investments = sorted(
            investments, 
            key=lambda x: x.date, 
            reverse=True
        )[:max_items]
    
    def generate(self) -> str:
        content = ["## 💰 Investment Highlights", ""]
        content.append("*Recent funding rounds and acquisitions in the AI space*\n")
        
        for inv in self.investments:
            content.append(f"### {inv.investee.name} - {inv.format_amount()}")
            content.append(f"- **Investor:** {inv.investor.name}")
            content.append(f"- **Stage:** {inv.stage.value}")
            content.append(f"- **Sector:** {inv.investee.sector}")
            content.append(f"- **Date:** {inv.date.strftime('%B %d, %Y')}")
            
            if inv.details:
                content.append(f"- **Details:** {inv.details}")
            
            if inv.key_insights:
                content.append("- **Key Insights:**")
                for insight in inv.key_insights:
                    content.append(f"  - {insight}")

            # Evidence / grounding
            sources = getattr(inv, "sources", [])
            if sources:
                src = sources[0]
                if getattr(inv, "confidence", None) is not None:
                    content.append(f"- **Confidence:** {inv.confidence:.2f}")
                if src.evidence_quote:
                    content.append(f"- **Evidence:** \"{src.evidence_quote}\"")
                if src.url:
                    content.append(f"- **Source:** {src.source_name} — {src.url}")
                else:
                    content.append(f"- **Source:** {src.source_name}")
            
            content.append("")
        
        return "\n".join(content)


class MarketTrendsSection(NewsletterSection):
    """Section analyzing market trends"""
    
    def __init__(self, trends: List[MarketTrend]):
        self.trends = trends
    
    def generate(self) -> str:
        content = ["## 📈 Market Trends", ""]
        content.append("*What's shaping the AI investment landscape*\n")
        
        for trend in self.trends:
            impact_emoji = {"High": "🔥", "Medium": "⚡", "Low": "💡"}.get(
                trend.impact_level, "📊"
            )
            
            content.append(f"### {impact_emoji} {trend.trend_name}")
            content.append(f"{trend.description}\n")
            
            if trend.relevant_sectors:
                content.append("**Relevant Sectors:**")
                content.append(", ".join(trend.relevant_sectors) + "\n")
            
            if trend.opportunity_areas:
                content.append("**Opportunity Areas:**")
                for area in trend.opportunity_areas:
                    content.append(f"- {area}")
                content.append("")
        
        return "\n".join(content)


class EntrepreneurGuidanceSection(NewsletterSection):
    """Section with actionable advice for entrepreneurs"""
    
    def __init__(self, tips: List[EntrepreneurTip]):
        self.tips = tips
    
    def generate(self) -> str:
        content = ["## 🚀 How to Get Involved: Entrepreneur's Playbook", ""]
        content.append("*Actionable insights for aspiring AI entrepreneurs*\n")
        
        # Group tips by category
        categories = {}
        for tip in self.tips:
            if tip.category not in categories:
                categories[tip.category] = []
            categories[tip.category].append(tip)
        
        for category, tips in categories.items():
            content.append(f"### {category}")
            content.append("")
            
            for tip in tips:
                content.append(f"**{tip.title}**")
                content.append(f"{tip.description}\n")
                
                if tip.action_items:
                    content.append("*Action Items:*")
                    for item in tip.action_items:
                        content.append(f"- [ ] {item}")
                    content.append("")
                
                if tip.resources:
                    content.append("*Resources:*")
                    for resource in tip.resources:
                        content.append(f"- {resource}")
                    content.append("")
        
        return "\n".join(content)


class ExecutiveSummarySection(NewsletterSection):
    """Brief overview of the newsletter"""
    
    def __init__(self, summary: str, key_takeaways: List[str]):
        self.summary = summary
        self.key_takeaways = key_takeaways
    
    def generate(self) -> str:
        content = ["## 📋 Executive Summary", ""]
        content.append(self.summary)
        content.append("\n**Key Takeaways:**")
        
        for takeaway in self.key_takeaways:
            content.append(f"- {takeaway}")
        
        content.append("")
        return "\n".join(content)


class InvestorSpotlightSection(NewsletterSection):
    """Highlight active investors in the AI space"""
    
    def __init__(self, investor_data: List[dict]):
        self.investor_data = investor_data
    
    def generate(self) -> str:
        content = ["## 🎯 Investor Spotlight", ""]
        content.append("*Most active investors in AI this period*\n")
        
        for investor in self.investor_data:
            content.append(f"### {investor['name']}")
            content.append(f"{investor['description']}\n")
            content.append(f"- **Focus Areas:** {', '.join(investor['focus_areas'])}")
            content.append(f"- **Recent Investments:** {investor['recent_count']}")
            content.append(f"- **Average Check Size:** {investor['avg_check_size']}")
            
            if investor.get('contact_info'):
                content.append(f"- **How to Reach:** {investor['contact_info']}")
            
            content.append("")
        
        return "\n".join(content)
