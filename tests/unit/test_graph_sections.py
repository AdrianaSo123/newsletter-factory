from datetime import datetime

from graph_sections import CoInvestmentNetworkSection
from knowledge_graph import KnowledgeGraph
from models import Company, Investment, FactSource
from newsletter_factory import InvestmentStage


def _inv(investor: str, investee: str, url: str):
    return Investment(
        investor=Company(investor, "d", "VC Firm"),
        investee=Company(investee, "d", "LLM"),
        amount=10.0,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[FactSource(source_name="Example", url=url, evidence_quote=f"{investee} raised $10M")],
        confidence=0.7,
    )


def test_co_investment_network_section_renders_pair_and_source():
    kg = KnowledgeGraph().build_from_investments(
        [
            _inv("Sequoia", "Acme AI", "https://example.com/a"),
            _inv("a16z", "Acme AI", "https://example.com/b"),
        ]
    )
    out = CoInvestmentNetworkSection(kg, max_pairs=3).generate()
    assert "Network Signals" in out
    assert "Sequoia" in out
    assert "a16z" in out
    assert "Source:" in out
