from datetime import datetime

from knowledge_graph import KnowledgeGraph
from models import Company, Investment, FactSource
from newsletter_factory import InvestmentStage


def _inv(investor: str, investee: str, amount: float = 10.0, url: str = "https://example.com"):
    return Investment(
        investor=Company(investor, "d", "VC Firm"),
        investee=Company(investee, "d", "LLM"),
        amount=amount,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[
            FactSource(
                source_name="Example",
                url=url,
                retrieved_at=datetime(2026, 2, 1),
                evidence_quote=f"{investor} invested ${amount}M in {investee}.",
            )
        ],
        confidence=0.7,
    )


def test_knowledge_graph_builds_nodes_and_edges():
    kg = KnowledgeGraph().build_from_investments([
        _inv("Sequoia", "Acme AI", 12.0),
        _inv("Sequoia", "Beta AI", 5.0),
    ])

    assert len(kg.nodes) >= 3
    assert len(kg.edges) == 2

    portfolio = kg.portfolio_of("Sequoia")
    names = [n for (n, _e) in portfolio]
    assert "Acme AI" in names
    assert "Beta AI" in names


def test_knowledge_graph_to_json_has_sources():
    kg = KnowledgeGraph().build_from_investments([
        _inv("Sequoia", "Acme AI", 12.0, url="https://example.com/story"),
    ])

    d = kg.to_json_dict()
    assert "nodes" in d and "edges" in d
    assert len(d["edges"]) == 1
    edge = d["edges"][0]
    assert edge["kind"] == "invested_in"
    assert edge["sources"]
    assert edge["sources"][0]["url"] == "https://example.com/story"


def test_derive_co_investments_creates_pair_edge_with_provenance():
    # Two different investors into the same investee => a CO_INVESTED_WITH edge.
    kg = KnowledgeGraph().build_from_investments(
        [
            _inv("Sequoia", "Acme AI", 12.0, url="https://example.com/a"),
            _inv("a16z", "Acme AI", 8.0, url="https://example.com/b"),
        ]
    )

    created = kg.derive_co_investments()
    assert created >= 1

    pairs = kg.top_co_investor_pairs(limit=5)
    assert pairs
    a, b, e = pairs[0]
    assert {a, b} == {"Sequoia", "a16z"}
    assert e.kind.value == "co_invested_with"
    assert e.derived_from
    assert e.sources
