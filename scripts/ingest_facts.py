"""Ingest grounded facts into SQLite.

Usage:
  cd ".../newsletter factory" && ./.venv/bin/python scripts/ingest_facts.py --days-back 14 --days-ahead 90

What it does:
- Fetches investments/events (web when possible, cached when available).
- Validates grounding rules.
- Writes deduped facts + sources to cache/facts.sqlite.
"""

from __future__ import annotations

import argparse
import os
import sys

# Ensure the project root is on sys.path when executed as a file.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from facts_store import FactsStore
from scrapers.real_data_source import RealTimeDataSource
from scrapers.event_scrapers import EventAggregator
from validation import validate_investment, validate_event


def main() -> int:
    parser = argparse.ArgumentParser(description="Ingest grounded facts into SQLite")
    parser.add_argument("--days-back", type=int, default=14)
    parser.add_argument("--days-ahead", type=int, default=90)
    parser.add_argument("--db", type=str, default="cache/facts.sqlite")
    args = parser.parse_args()

    store = FactsStore(args.db)

    investments = RealTimeDataSource(use_cache=True).fetch_investments(days_back=args.days_back)
    investments_valid = [inv for inv in investments if validate_investment(inv).ok]

    events = EventAggregator().fetch_upcoming_events(days_ahead=args.days_ahead)
    events_valid = [ev for ev in events if validate_event(ev).ok]

    inv_stats = store.upsert_investments(investments_valid)
    ev_stats = store.upsert_events(events_valid)

    print(f"DB: {args.db}")
    print(f"Investments fetched: {len(investments)} | stored new: {inv_stats['investments_inserted']} | sources new: {inv_stats['sources_inserted']}")
    print(f"Events fetched: {len(events)} | stored new: {ev_stats['events_inserted']} | sources new: {ev_stats['sources_inserted']}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
