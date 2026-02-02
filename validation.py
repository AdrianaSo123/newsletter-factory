"""Validation helpers for keeping outputs grounded and non-hallucinatory.

Principle: if we can't back a claim with a source + evidence, we either
- drop the item, or
- mark it low-confidence and render it as such.

This module is intentionally rules-first and deterministic.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from models import Investment, FactSource


@dataclass(frozen=True)
class ValidationResult:
    ok: bool
    reasons: List[str]


def _has_grounding(sources: List[FactSource]) -> bool:
    if not sources:
        return False
    for s in sources:
        if s.source_name and (s.url or s.evidence_quote):
            return True
    return False


def validate_investment(inv: Investment, *, now: Optional[datetime] = None) -> ValidationResult:
    """Validate a scraped Investment.

    Requirements (for "no hallucinations"):
    - has grounding (source + url or evidence quote)
    - amount > 0
    - date not unreasonably in the future
    - company/investor names present
    """

    now = now or datetime.now()
    reasons: List[str] = []

    if not inv.investee or not inv.investee.name:
        reasons.append("missing investee name")
    if not inv.investor or not inv.investor.name:
        reasons.append("missing investor name")

    try:
        amount = float(inv.amount)
        if amount <= 0:
            reasons.append("amount must be > 0")
    except Exception:
        reasons.append("amount is not numeric")

    if not getattr(inv, "date", None):
        reasons.append("missing date")
    else:
        # Allow small clock skew; block far-future dates.
        if inv.date > now + timedelta(days=2):
            reasons.append("date is in the future")

    if not _has_grounding(getattr(inv, "sources", [])):
        reasons.append("missing grounding (source url or evidence quote)")

    # Confidence is advisory but should be sane.
    conf = getattr(inv, "confidence", 0.0)
    if conf < 0 or conf > 1:
        reasons.append("confidence must be within [0,1]")

    return ValidationResult(ok=len(reasons) == 0, reasons=reasons)


def validate_event(event: object, *, now: Optional[datetime] = None) -> ValidationResult:
    """Validate an event object using duck-typed attributes.

    Requirements:
    - name present
    - date present and not far in the past
    - appears AI-related (keywords/topics)
    - has grounding (sources with url or evidence quote)
    """

    now = now or datetime.now()
    reasons: List[str] = []

    name = getattr(event, "name", None)
    if not name:
        reasons.append("missing event name")

    # AI relevance gate: avoid publishing unrelated events.
    ai_keywords = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "ml",
        "deep learning",
        "llm",
        "large language model",
        "generative ai",
        "genai",
        "gpt",
        "agents",
        "agentic",
    ]

    topics = getattr(event, "topics", []) or []
    description = getattr(event, "description", "") or ""
    combined = f"{name or ''} {description}".lower()
    topic_text = " ".join([str(t).lower() for t in topics])
    if not any(k in combined for k in ai_keywords) and not any(k in topic_text for k in ["ai", "genai", "llm", "nlp", "computer vision", "robotics", "ai safety"]):
        reasons.append("event does not appear AI-related")

    date = getattr(event, "date", None)
    if not date:
        reasons.append("missing event date")
    else:
        # Allow small staleness; but we should not publish long-past events.
        if date < now - timedelta(days=3):
            reasons.append("event date is in the past")

    sources = getattr(event, "sources", [])
    if not _has_grounding(sources):
        reasons.append("missing grounding (source url or evidence quote)")

    conf = getattr(event, "confidence", 0.5)
    if conf < 0 or conf > 1:
        reasons.append("confidence must be within [0,1]")

    return ValidationResult(ok=len(reasons) == 0, reasons=reasons)


def filter_valid_investments(investments: List[Investment]) -> Tuple[List[Investment], List[Tuple[Investment, ValidationResult]]]:
    """Return (valid, invalid_with_reasons)."""
    valid: List[Investment] = []
    invalid: List[Tuple[Investment, ValidationResult]] = []

    for inv in investments:
        res = validate_investment(inv)
        if res.ok:
            valid.append(inv)
        else:
            invalid.append((inv, res))

    return valid, invalid
