"""
Data models for investment tracking and newsletter content
"""

from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
from newsletter_factory import InvestmentStage


@dataclass
class FactSource:
    """Grounding/evidence for a extracted fact."""

    source_name: str
    url: Optional[str] = None
    retrieved_at: Optional[datetime] = None
    evidence_quote: Optional[str] = None


@dataclass
class Company:
    """Represents a company in the AI ecosystem"""
    name: str
    description: str
    sector: str  # e.g., "LLM", "Computer Vision", "Robotics", etc.
    website: Optional[str] = None
    founded_year: Optional[int] = None
    
    def __str__(self) -> str:
        return f"{self.name} ({self.sector})"


@dataclass
class Investment:
    """Represents an investment event"""
    investor: Company
    investee: Company
    amount: float  # in millions USD
    stage: InvestmentStage
    date: datetime
    details: Optional[str] = None
    key_insights: List[str] = field(default_factory=list)
    sources: List[FactSource] = field(default_factory=list)
    confidence: float = 0.5
    
    def format_amount(self) -> str:
        """Format the investment amount"""
        if self.amount >= 1000:
            return f"${self.amount/1000:.1f}B"
        return f"${self.amount:.1f}M"
    
    def __str__(self) -> str:
        return (f"{self.investor.name} → {self.investee.name}: "
                f"{self.format_amount()} ({self.stage.value})")


@dataclass
class EntrepreneurTip:
    """Actionable advice for aspiring AI entrepreneurs"""
    title: str
    description: str
    category: str  # e.g., "Funding", "Product", "Talent", "Market"
    action_items: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    # Optional grounding: sources from the investments/events that motivated this tip.
    sources: List[FactSource] = field(default_factory=list)


@dataclass
class MarketTrend:
    """Market trend analysis for the AI sector"""
    trend_name: str
    description: str
    impact_level: str  # "High", "Medium", "Low"
    relevant_sectors: List[str] = field(default_factory=list)
    opportunity_areas: List[str] = field(default_factory=list)
    # Optional grounding: sources from the underlying investments.
    sources: List[FactSource] = field(default_factory=list)

