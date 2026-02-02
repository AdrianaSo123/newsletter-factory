from datetime import datetime

from content_generator import EntrepreneurshipContentGenerator
from models import Company, Investment, FactSource
from newsletter_factory import InvestmentStage


def _inv(sector: str, amount: float = 10.0):
    return Investment(
        investor=Company("VC", "d", "VC Firm"),
        investee=Company("Acme", "open source models", sector),
        amount=amount,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[
            FactSource(
                source_name="Example",
                url="https://example.com/story",
                retrieved_at=datetime(2026, 2, 1),
                evidence_quote=f"Acme raised ${amount}M.",
            )
        ],
        confidence=0.7,
    )


def test_generated_trends_include_sources():
    investments = [_inv("LLM", 12.0), _inv("LLM", 5.0)]
    trends = EntrepreneurshipContentGenerator.generate_market_trends(investments)
    assert trends
    assert any(getattr(t, "sources", []) for t in trends)


def test_generated_tips_include_sources():
    investments = [_inv("LLM", 12.0)]
    tips = EntrepreneurshipContentGenerator.generate_tips_from_investments(investments)
    assert tips
    assert any(getattr(t, "sources", []) for t in tips)
