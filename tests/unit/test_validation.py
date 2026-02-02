from datetime import datetime, timedelta

import pytest

from models import Company, Investment, FactSource
from newsletter_factory import InvestmentStage
from validation import validate_investment, validate_event
from scrapers.event_scrapers import AIEvent


def test_validate_investment_rejects_missing_grounding():
    inv = Investment(
        investor=Company("VC", "d", "VC Firm"),
        investee=Company("Startup", "d", "LLM"),
        amount=10.0,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[],
        confidence=0.7,
    )

    res = validate_investment(inv, now=datetime(2026, 2, 1))
    assert res.ok is False
    assert any("grounding" in r for r in res.reasons)


def test_validate_investment_accepts_grounded_item():
    inv = Investment(
        investor=Company("VC", "d", "VC Firm"),
        investee=Company("Startup", "d", "LLM"),
        amount=10.0,
        stage=InvestmentStage.SEED,
        date=datetime(2026, 2, 1),
        sources=[
            FactSource(
                source_name="Example",
                url="https://example.com/story",
                retrieved_at=datetime(2026, 2, 1),
                evidence_quote="Startup raised $10M seed round.",
            )
        ],
        confidence=0.7,
    )

    res = validate_investment(inv, now=datetime(2026, 2, 1))
    assert res.ok is True


def test_validate_event_rejects_missing_grounding():
    ev = AIEvent(
        name="AI Meetup",
        event_type="Meetup",
        date=datetime(2026, 2, 15),
        location="Virtual",
        description="Talks and networking",
        url="https://example.com/event",
        sources=[],
        confidence=0.8,
    )

    res = validate_event(ev, now=datetime(2026, 2, 1))
    assert res.ok is False


def test_validate_event_accepts_grounded_upcoming():
    ev = AIEvent(
        name="AI Meetup",
        event_type="Meetup",
        date=datetime(2026, 2, 15),
        location="Virtual",
        description="Talks and networking",
        url="https://example.com/event",
        sources=[
            FactSource(
                source_name="Example Events",
                url="https://example.com/event",
                retrieved_at=datetime(2026, 2, 1),
                evidence_quote="AI Meetup — Feb 15",
            )
        ],
        confidence=0.8,
    )

    res = validate_event(ev, now=datetime(2026, 2, 1))
    assert res.ok is True


@pytest.mark.parametrize("days_past", [4, 30])
def test_validate_event_rejects_past_events(days_past: int):
    now = datetime(2026, 2, 1)
    ev = AIEvent(
        name="Old Event",
        event_type="Conference",
        date=now - timedelta(days=days_past),
        location="Somewhere",
        description="Old",
        url="https://example.com/old",
        sources=[FactSource(source_name="Example", url="https://example.com/old")],
        confidence=0.8,
    )

    res = validate_event(ev, now=now)
    assert res.ok is False
    assert any("past" in r for r in res.reasons)
