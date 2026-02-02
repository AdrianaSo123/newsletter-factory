from __future__ import annotations

import re
from typing import Optional, List

from newsletter_factory import InvestmentStage


_MONEY_RE = re.compile(
    r"\$(?P<num>\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+(?:\.\d+)?)\s*(?P<unit>billion|million|bn|m|b)\b",
    re.IGNORECASE,
)


def parse_money_usd_millions(text: str) -> Optional[float]:
    """Parse a USD amount and return value in USD millions.

    Examples:
      "$12M" -> 12.0
      "$1.2B" -> 1200.0
      "$450 million" -> 450.0
      "$10,000M" -> 10000.0

    Returns None if no USD amount is found.
    """
    if not text:
        return None

    match = _MONEY_RE.search(text)
    if not match:
        return None

    raw_num = match.group("num").replace(",", "")
    unit = match.group("unit").lower()

    try:
        value = float(raw_num)
    except ValueError:
        return None

    if unit in {"billion", "b", "bn"}:
        return value * 1000.0
    return value


def infer_stage(text: str) -> InvestmentStage:
    """Infer an InvestmentStage from free text.

    Defaults to SERIES_A if unknown.
    """
    if not text:
        return InvestmentStage.SERIES_A

    t = text.lower()
    if "seed" in t:
        return InvestmentStage.SEED

    series_map = {
        "series a": InvestmentStage.SERIES_A,
        "series b": InvestmentStage.SERIES_B,
        "series c": InvestmentStage.SERIES_C,
        "series d": InvestmentStage.SERIES_D_PLUS,
        "series e": InvestmentStage.SERIES_D_PLUS,
        "series f": InvestmentStage.SERIES_D_PLUS,
        "series g": InvestmentStage.SERIES_D_PLUS,
    }
    for key, stage in series_map.items():
        if key in t:
            return stage

    if "acquir" in t:
        return InvestmentStage.ACQUISITION
    if "ipo" in t:
        return InvestmentStage.IPO

    return InvestmentStage.SERIES_A


def extract_company_name_from_title(title: str) -> Optional[str]:
    """Extract a company name from a headline.

    This is intentionally conservative to avoid making things up.
    Returns None if we cannot extract confidently.
    """
    if not title:
        return None

    # Strip common editorial prefixes that would otherwise be mistaken as a company name.
    # Keep this list short and deterministic.
    cleaned = re.sub(r"^\s*(?:Exclusive|Report|Analysis|Opinion)\s*[:\-—]\s+", "", title).strip()
    if not cleaned:
        return None

    patterns = [
        r"^([A-Z][A-Za-z0-9\.\-\s]+?)\s+(?:raises|secures|closes|gets|lands|scores)\b",
        r"^([A-Z][A-Za-z0-9\.\-\s]+?)\s+(?:announces|launches|unveils)\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            candidate = match.group(1).strip()
            if 2 <= len(candidate) <= 60:
                return candidate

    # Fallback: first token if it looks like a proper noun.
    first = cleaned.strip().split()[0] if cleaned.strip() else ""
    if first and first[0].isupper() and len(first) > 1:
        return first

    return None


def extract_investor_names(text: str, max_names: int = 5) -> List[str]:
    """Extract likely investor names from text.

    Uses conservative patterns ("led by", "backed by", "participation from").
    Returns an empty list if none found.
    """
    if not text:
        return []

    patterns = [
        r"led by\s+([A-Z][A-Za-z0-9&\.\s]+?)(?:,|\.|;|\n)",
        r"backed by\s+([A-Z][A-Za-z0-9&\.\s]+?)(?:,|\.|;|\n)",
        r"participation from\s+([A-Z][A-Za-z0-9&\.\s]+?)(?:,|\.|;|\n)",
    ]

    names: List[str] = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            candidate = " ".join(match.group(1).split()).strip()
            if candidate and candidate not in names:
                names.append(candidate)
            if len(names) >= max_names:
                return names

    return names
