"""Export the evidence-first knowledge graph.

Usage:
  cd ".../newsletter factory" && ./.venv/bin/python scripts/export_knowledge_graph.py --days-back 14

Outputs:
- cache/knowledge_graph.json
- cache/knowledge_graph.dot

Notes:
- Uses cached data when available.
- If scraping fails (no network), falls back to mock investments.
- For reproducibility, you can build from the SQLite facts store.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Ensure the project root is on sys.path when executed as a file.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from knowledge_graph import KnowledgeGraph
from scrapers.real_data_source import RealTimeDataSource
from facts_store import FactsStore


def main() -> int:
    parser = argparse.ArgumentParser(description="Export investment knowledge graph")
    parser.add_argument("--days-back", type=int, default=7)
    parser.add_argument("--db", type=str, default="cache/facts.sqlite")
    parser.add_argument(
        "--ingest",
        action="store_true",
        help="Fetch/validate investments and ingest into SQLite before exporting",
    )
    parser.add_argument(
        "--from-db",
        action="store_true",
        help="Build the KG from SQLite instead of the live scrape result",
    )
    parser.add_argument("--json-path", type=str, default="cache/knowledge_graph.json")
    parser.add_argument("--dot-path", type=str, default="cache/knowledge_graph.dot")
    args = parser.parse_args()

    store = FactsStore(args.db)

    if args.ingest:
        from validation import validate_investment

        scraped = RealTimeDataSource(use_cache=True).fetch_investments(days_back=args.days_back)
        valid = [inv for inv in scraped if validate_investment(inv).ok]
        store.upsert_investments(valid)

    if args.from_db:
        investments = store.load_investments(days_back=args.days_back)
    else:
        investments = RealTimeDataSource(use_cache=True).fetch_investments(days_back=args.days_back)

    kg = KnowledgeGraph().build_from_investments(investments)
    # Add derived relationships (safe to call even if there are no pairs).
    kg.derive_co_investments()

    json_path = Path(args.json_path)
    dot_path = Path(args.dot_path)
    json_path.parent.mkdir(parents=True, exist_ok=True)

    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(kg.to_json_dict(), f, indent=2)

    with open(dot_path, "w", encoding="utf-8") as f:
        f.write(kg.to_dot())

    print(f"Wrote {json_path}")
    print(f"Wrote {dot_path}")
    print(f"Nodes: {len(kg.nodes)}")
    print(f"Edges: {len(kg.edges)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
