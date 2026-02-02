from datetime import datetime, timedelta

from validation import validate_event


class DummyEvent:
    def __init__(self, name: str, description: str, topics=None):
        self.name = name
        self.description = description
        self.topics = topics or []
        self.date = datetime.now() + timedelta(days=10)
        self.sources = [type("S", (), {"source_name": "X", "url": "https://example.com", "evidence_quote": "AI event"})()]
        self.confidence = 0.7


def test_validate_event_rejects_non_ai_event():
    ev = DummyEvent(name="Skin Care Is a Billion-Dollar Industry", description="Legacy building for pharmacists")
    res = validate_event(ev)
    assert not res.ok
    assert "event does not appear AI-related" in res.reasons


def test_validate_event_accepts_ai_keyword_in_name():
    ev = DummyEvent(name="Intro to AI for Beginners", description="Learn artificial intelligence")
    res = validate_event(ev)
    assert res.ok


def test_validate_event_accepts_ai_topic_even_if_name_generic():
    ev = DummyEvent(name="Foundations", description="", topics=["GenAI"])
    res = validate_event(ev)
    assert res.ok
