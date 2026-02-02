from datetime import datetime

from models import EntrepreneurTip, MarketTrend, FactSource
from sections import EntrepreneurGuidanceSection, MarketTrendsSection


def test_market_trends_section_renders_evidence_when_present():
    trend = MarketTrend(
        trend_name="T",
        description="D",
        impact_level="High",
        sources=[FactSource(source_name="Example", url="https://example.com", evidence_quote="Evidence line")],
    )

    out = MarketTrendsSection([trend]).generate()
    assert "Evidence:" in out
    assert "https://example.com" in out


def test_entrepreneur_guidance_section_renders_evidence_when_present():
    tip = EntrepreneurTip(
        title="Tip",
        description="Desc",
        category="Funding",
        sources=[FactSource(source_name="Example", url="https://example.com", evidence_quote="Evidence line")],
    )

    out = EntrepreneurGuidanceSection([tip]).generate()
    assert "*Evidence:*" in out
    assert "https://example.com" in out
