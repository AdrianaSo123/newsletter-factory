from datetime import datetime

from facts_store import FactsStore
from models import Company, Investment, FactSource
from newsletter_factory import InvestmentStage


def test_facts_store_round_trip_investments(tmp_path):
    db = tmp_path / "facts.sqlite"
    store = FactsStore(db)

    inv = Investment(
        investor=Company("Sequoia", "d", "VC Firm"),
        investee=Company("Acme AI", "d", "LLM"),
        amount=12.0,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[FactSource(source_name="Example", url="https://example.com", evidence_quote="Acme raised $12M")],
        confidence=0.7,
    )

    stats = store.upsert_investments([inv])
    assert stats["investments_inserted"] == 1
    assert stats["sources_inserted"] == 1

    loaded = store.load_investments(days_back=365)
    assert loaded
    assert any(i.investee.name == "Acme AI" for i in loaded)
    # Ensure sources come back.
    back = next(i for i in loaded if i.investee.name == "Acme AI")
    assert back.sources
    assert back.sources[0].url == "https://example.com"


def test_facts_store_dedupes_investment(tmp_path):
    db = tmp_path / "facts.sqlite"
    store = FactsStore(db)

    inv = Investment(
        investor=Company("Sequoia", "d", "VC Firm"),
        investee=Company("Acme AI", "d", "LLM"),
        amount=12.0,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[FactSource(source_name="Example", url="https://example.com", evidence_quote="Acme raised $12M")],
        confidence=0.7,
    )

    s1 = store.upsert_investments([inv])
    s2 = store.upsert_investments([inv])

    assert s1["investments_inserted"] == 1
    assert s2["investments_inserted"] == 0
