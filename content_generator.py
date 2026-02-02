"""
Content generators for entrepreneurship guidance
"""

from typing import List
from models import EntrepreneurTip, MarketTrend, Investment, FactSource


def _dedupe_sources(sources: List[FactSource], *, limit: int = 5) -> List[FactSource]:
    """Dedupe sources conservatively to keep newsletters readable."""
    out: List[FactSource] = []
    seen = set()
    for s in sources or []:
        key = (getattr(s, "source_name", None), getattr(s, "url", None), getattr(s, "evidence_quote", None))
        if key in seen:
            continue
        seen.add(key)
        out.append(s)
        if len(out) >= limit:
            break
    return out


def _sources_from_investments(investments: List[Investment], *, limit: int = 5) -> List[FactSource]:
    sources: List[FactSource] = []
    for inv in investments or []:
        sources.extend(list(getattr(inv, "sources", []) or []))
    return _dedupe_sources(sources, limit=limit)


class EntrepreneurshipContentGenerator:
    """Generates actionable content for aspiring AI entrepreneurs"""
    
    @staticmethod
    def generate_tips_from_investments(investments: List[Investment]) -> List[EntrepreneurTip]:
        """
        Analyze investments to extract entrepreneurship lessons
        """
        tips = []
        
        # Analyze investment patterns
        sectors = {}
        stages = {}
        
        for inv in investments:
            sectors[inv.investee.sector] = sectors.get(inv.investee.sector, 0) + 1
            stages[inv.stage] = stages.get(inv.stage, 0) + 1
        
        # Generate sector-specific tip
        if sectors:
            hot_sector = max(sectors, key=sectors.get)
            sector_investments = [inv for inv in investments if getattr(getattr(inv, "investee", None), "sector", None) == hot_sector]
            tips.append(EntrepreneurTip(
                title=f"Focus on {hot_sector}",
                description=f"This sector received the most funding this period with {sectors[hot_sector]} deals. "
                           f"Investors are actively seeking opportunities in this space.",
                category="Market Opportunity",
                action_items=[
                    f"Research existing {hot_sector} solutions and identify gaps",
                    "Connect with founders in this space on LinkedIn",
                    "Follow key investors active in this sector",
                    "Build a prototype or proof-of-concept"
                ],
                resources=[
                    f"Papers with Code - Latest {hot_sector} research",
                    "Y Combinator Startup School",
                    "AI-focused Discord/Slack communities"
                ],
                sources=_sources_from_investments(sector_investments, limit=4),
            ))
        
        # Add funding stage insights
        tips.append(EntrepreneurTip(
            title="Understand the Funding Landscape",
            description="Different stages require different preparations. Know what investors look for at each stage.",
            category="Funding",
            action_items=[
                "Build an MVP before raising seed funding",
                "Track key metrics: user growth, engagement, revenue",
                "Prepare a compelling pitch deck (10-15 slides)",
                "Network with angel investors and VCs in your sector"
            ],
            resources=[
                "NFX Signal - Investor database",
                "First Round Review - Startup guides",
                "Crunchbase - Track investors and deals"
            ],
            # This is guidance; not all points are empirical claims. Still attach sources
            # from the current investment set for context.
            sources=_sources_from_investments(investments, limit=2),
        ))
        
        # Product development tip
        tips.append(EntrepreneurTip(
            title="Build with AI, Not Just On AI",
            description="The best AI startups use AI to solve real problems, not just showcase technology. "
                       "Focus on painful problems where AI provides 10x improvement.",
            category="Product",
            action_items=[
                "Identify a problem you personally experience",
                "Talk to 50+ potential customers before building",
                "Start with a narrow use case and expand",
                "Make it work reliably before making it fancy"
            ],
            resources=[
                "The Mom Test - Customer interview guide",
                "Superhuman's Framework for Product-Market Fit",
                "OpenAI/Anthropic API documentation"
            ],
            sources=_sources_from_investments(investments, limit=2),
        ))
        
        # Talent tip
        tips.append(EntrepreneurTip(
            title="Attract Top AI Talent",
            description="AI engineers are highly sought after. Compete on mission, learning, and equity, not just salary.",
            category="Talent",
            action_items=[
                "Write compelling blog posts about your technical challenges",
                "Open-source internal tools to build credibility",
                "Offer equity packages competitive with Big Tech",
                "Create a culture of continuous learning and research"
            ],
            resources=[
                "HuggingFace Jobs Board",
                "AI-focused recruiter networks",
                "Technical blog platforms (Medium, Dev.to)"
            ],
            sources=_sources_from_investments(investments, limit=2),
        ))
        
        # Market entry tip
        tips.append(EntrepreneurTip(
            title="Choose Your Go-To-Market Wisely",
            description="AI products can be sold B2B, B2C, or as infrastructure. Each requires different strategies.",
            category="Market",
            action_items=[
                "B2B: Focus on ROI and integration capabilities",
                "B2C: Prioritize user experience and viral growth",
                "Infrastructure: Build developer community and documentation",
                "Consider platform risk (OpenAI, Google dependencies)"
            ],
            resources=[
                "Lenny's Newsletter - Growth strategies",
                "Developer Marketing Alliance",
                "AI product community newsletters"
            ],
            sources=_sources_from_investments(investments, limit=2),
        ))
        
        return tips
    
    @staticmethod
    def generate_market_trends(investments: List[Investment]) -> List[MarketTrend]:
        """
        Analyze investments to identify market trends
        """
        trends = []
        
        # Analyze total funding and sectors
        total_funding = sum(inv.amount for inv in investments)
        sector_funding = {}
        
        for inv in investments:
            sector = inv.investee.sector
            sector_funding[sector] = sector_funding.get(sector, 0) + inv.amount
        
        # Trend 1: Overall market health
        trends.append(MarketTrend(
            trend_name="AI Investment Momentum Continues",
            description=f"${total_funding:.1f}M deployed across {len(investments)} deals this period. "
                       f"Investors remain bullish on AI despite broader market conditions.",
            impact_level="High",
            relevant_sectors=list(sector_funding.keys()),
            opportunity_areas=[
                "Enterprise AI adoption accelerating",
                "Developer tools and infrastructure in demand",
                "Vertical-specific AI solutions gaining traction"
            ],
            sources=_sources_from_investments(investments, limit=5),
        ))
        
        # Trend 2: Open source
        open_source_count = sum(
            1
            for inv in investments
            if (
                'open' in (inv.investee.description or '').lower()
                or (inv.details is not None and 'open' in inv.details.lower())
            )
        )
        
        if open_source_count > 0:
            open_source_investments = [
                inv
                for inv in investments
                if (
                    'open' in (inv.investee.description or '').lower()
                    or (inv.details is not None and 'open' in inv.details.lower())
                )
            ]
            trends.append(MarketTrend(
                trend_name="Open Source AI Models Rising",
                description="Open-source AI is attracting significant capital as companies seek alternatives "
                           "to proprietary models. This democratizes AI development.",
                impact_level="High",
                relevant_sectors=["LLM", "Computer Vision", "Developer Tools"],
                opportunity_areas=[
                    "Build on open models with domain-specific fine-tuning",
                    "Create tools for model deployment and optimization",
                    "Offer services around open-source model customization"
                ],
                sources=_sources_from_investments(open_source_investments, limit=4),
            ))
        
        # Trend 3: Sector-specific insights
        if sector_funding:
            top_sector = max(sector_funding, key=sector_funding.get)
            top_sector_investments = [inv for inv in investments if getattr(getattr(inv, "investee", None), "sector", None) == top_sector]
            trends.append(MarketTrend(
                trend_name=f"{top_sector} Leading Investment Activity",
                description=f"{top_sector} companies captured ${sector_funding[top_sector]:.1f}M in funding, "
                           f"representing the highest concentration of investor interest.",
                impact_level="High",
                relevant_sectors=[top_sector],
                opportunity_areas=[
                    f"Solve niche problems within {top_sector}",
                    "Build complementary tools and infrastructure",
                    "Target underserved customer segments"
                ],
                sources=_sources_from_investments(top_sector_investments, limit=4),
            ))
        
        return trends
    
    @staticmethod
    def get_default_investor_spotlight() -> List[dict]:
        """Return curated list of active AI investors"""
        return [
            {
                'name': 'Andreessen Horowitz (a16z)',
                'description': 'Leading VC with dedicated $4.5B AI fund',
                'focus_areas': ['Infrastructure', 'Enterprise AI', 'Consumer AI'],
                'recent_count': 12,
                'avg_check_size': '$20-50M Series A/B',
                'contact_info': 'Submit via a16z.com/portfolio, warm intro preferred'
            },
            {
                'name': 'Google Ventures (GV)',
                'description': 'Strategic investor leveraging Google AI ecosystem',
                'focus_areas': ['LLM', 'AI Safety', 'Healthcare AI'],
                'recent_count': 8,
                'avg_check_size': '$10-30M Series A',
                'contact_info': 'Focus on technical founders with AI research background'
            },
            {
                'name': 'Khosla Ventures',
                'description': 'Early-stage focused with contrarian bets on AI',
                'focus_areas': ['Developer Tools', 'Robotics', 'Climate AI'],
                'recent_count': 15,
                'avg_check_size': '$5-15M Seed/Series A',
                'contact_info': 'Known for backing bold technical visions'
            }
        ]
