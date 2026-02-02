"""Preview what we *actually* extract from real websites.

This script is meant for interactive debugging and validation.
It prints (or emits JSON for) the extracted investments/events including:
- source URL
- evidence quote
- validation status + reasons for rejects

It does not generate a newsletter; it only previews the raw/normalized data.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict, is_dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Ensure the project root is on sys.path when executed as a file.
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scrapers.investment_scrapers import InvestmentDataAggregator
from scrapers.event_scrapers import EventAggregator, EventbriteScraper, AIConferenceTracker
from validation import validate_investment, validate_event


def _truncate(text: Optional[str], n: int = 180) -> Optional[str]:
    if text is None:
        return None
    t = " ".join(text.split())
    if len(t) <= n:
        return t
    return t[: n - 1] + "…"


def _fact_source_to_dict(src: Any) -> Dict[str, Any]:
    if is_dataclass(src):
        d = asdict(src)
    else:
        d = {
            "source_name": getattr(src, "source_name", None),
            "url": getattr(src, "url", None),
            "retrieved_at": getattr(src, "retrieved_at", None),
            "evidence_quote": getattr(src, "evidence_quote", None),
        }

    ra = d.get("retrieved_at")
    if isinstance(ra, datetime):
        d["retrieved_at"] = ra.isoformat()

    if d.get("evidence_quote"):
        d["evidence_quote"] = _truncate(d["evidence_quote"], 240)

    return d


def _investment_to_dict(inv: Any) -> Dict[str, Any]:
    return {
        "investor": getattr(getattr(inv, "investor", None), "name", None),
        "investee": getattr(getattr(inv, "investee", None), "name", None),
        "amount_m_usd": getattr(inv, "amount", None),
        "stage": getattr(getattr(inv, "stage", None), "value", None),
        "date": getattr(inv, "date", None).isoformat() if getattr(inv, "date", None) else None,
        "details": _truncate(getattr(inv, "details", None), 220),
        "confidence": getattr(inv, "confidence", None),
        "sources": [_fact_source_to_dict(s) for s in (getattr(inv, "sources", []) or [])],
    }


def _event_to_dict(ev: Any) -> Dict[str, Any]:
    return {
        "name": getattr(ev, "name", None),
        "event_type": getattr(ev, "event_type", None),
        "date": getattr(ev, "date", None).isoformat() if getattr(ev, "date", None) else None,
        "location": getattr(ev, "location", None),
        "url": getattr(ev, "url", None),
        "registration_url": getattr(ev, "registration_url", None),
        "organizer": getattr(ev, "organizer", None),
        "topics": list(getattr(ev, "topics", []) or []),
        "target_audience": getattr(ev, "target_audience", None),
        "cost": getattr(ev, "cost", None),
        "description": _truncate(getattr(ev, "description", None), 240),
        "confidence": getattr(ev, "confidence", None),
        "sources": [_fact_source_to_dict(s) for s in (getattr(ev, "sources", []) or [])],
    }


def _print_header(title: str) -> None:
    print("\n" + "=" * 80)
    print(title)
    print("=" * 80)


def _print_kv(key: str, value: Any) -> None:
    print(f"- {key}: {value}")


def _preview_investments(
    *,
    days_back: int,
    max_items: int,
    show_invalid: bool,
) -> Dict[str, Any]:
    agg = InvestmentDataAggregator()

    per_source: List[Dict[str, Any]] = []
    all_valid: List[Any] = []
    all_invalid: List[Dict[str, Any]] = []

    for scraper in agg.scrapers:
        source_name = scraper.__class__.__name__
        raw_items: List[Dict[str, Any]] = []
        converted = 0
        valid = 0
        invalid = 0
        dropped = 0

        try:
            raw_items = scraper.scrape(days_back=days_back)  # type: ignore[arg-type]
        except Exception as e:
            per_source.append(
                {
                    "source": source_name,
                    "error": str(e),
                    "raw": 0,
                    "converted": 0,
                    "valid": 0,
                    "invalid": 0,
                    "dropped": 0,
                }
            )
            continue

        for item in raw_items:
            inv = None
            try:
                inv = agg._convert_to_investment(item)  # intentionally using internal helper
            except Exception:
                inv = None

            if not inv:
                dropped += 1
                continue

            converted += 1
            res = validate_investment(inv)
            if res.ok:
                valid += 1
                all_valid.append(inv)
            else:
                invalid += 1
                all_invalid.append(
                    {
                        "source": item.get("source"),
                        "url": item.get("url"),
                        "title": item.get("title"),
                        "amount": item.get("amount"),
                        "evidence_quote": _truncate(item.get("evidence_quote") or item.get("summary"), 220),
                        "reasons": res.reasons,
                    }
                )

        per_source.append(
            {
                "source": source_name,
                "raw": len(raw_items),
                "converted": converted,
                "valid": valid,
                "invalid": invalid,
                "dropped": dropped,
            }
        )

    # Deduplicate and sort like the aggregator
    deduped = agg._deduplicate(all_valid)
    deduped.sort(key=lambda x: x.date, reverse=True)

    result = {
        "summary": {
            "days_back": days_back,
            "raw_sources": per_source,
            "valid_total": len(all_valid),
            "valid_deduped": len(deduped),
            "invalid_total": len(all_invalid),
        },
        "valid": [_investment_to_dict(i) for i in deduped[:max_items]],
    }

    if show_invalid:
        result["invalid"] = all_invalid[:max_items]

    return result


def _preview_events(
    *,
    days_ahead: int,
    max_items: int,
    show_invalid: bool,
) -> Dict[str, Any]:
    agg = EventAggregator()

    sources: List[Tuple[str, List[Any]]] = []
    per_source: List[Dict[str, Any]] = []

    # Dynamic sources
    for scraper in agg.scrapers:
        name = scraper.__class__.__name__
        try:
            events = scraper.scrape(days_ahead=days_ahead)  # type: ignore[arg-type]
            sources.append((name, events))
        except Exception as e:
            per_source.append({"source": name, "error": str(e), "raw": 0, "valid": 0, "invalid": 0})

    # Curated sources
    curated = AIConferenceTracker.get_major_conferences(days_ahead)
    sources.append(("AIConferenceTracker", curated))

    all_events: List[Any] = []
    all_invalid: List[Dict[str, Any]] = []

    for name, events in sources:
        valid = 0
        invalid = 0
        for ev in events:
            res = validate_event(ev)
            if res.ok:
                valid += 1
                all_events.append(ev)
            else:
                invalid += 1
                all_invalid.append(
                    {
                        "source": name,
                        "url": getattr(ev, "url", None),
                        "name": getattr(ev, "name", None),
                        "date": getattr(ev, "date", None).isoformat() if getattr(ev, "date", None) else None,
                        "reasons": res.reasons,
                    }
                )

        per_source.append({"source": name, "raw": len(events), "valid": valid, "invalid": invalid})

    deduped = agg._deduplicate(all_events)
    deduped.sort(key=lambda x: x.date)

    # Upcoming filter (match EventAggregator behavior)
    upcoming = [e for e in deduped if getattr(e, "is_upcoming", lambda: True)()]

    result = {
        "summary": {
            "days_ahead": days_ahead,
            "raw_sources": per_source,
            "valid_total": len(all_events),
            "valid_deduped_upcoming": len(upcoming),
            "invalid_total": len(all_invalid),
        },
        "valid": [_event_to_dict(e) for e in upcoming[:max_items]],
    }

    if show_invalid:
        result["invalid"] = all_invalid[:max_items]

    return result


def _render_text(preview: Dict[str, Any]) -> None:
    if "investments" in preview:
        _print_header("INVESTMENTS (preview)")
        s = preview["investments"]["summary"]
        _print_kv("days_back", s["days_back"])
        _print_kv("valid_total", s["valid_total"])
        _print_kv("valid_deduped", s["valid_deduped"])
        _print_kv("invalid_total", s["invalid_total"])
        print("\nPer source:")
        for row in s["raw_sources"]:
            if row.get("error"):
                print(f"- {row['source']}: ERROR: {row['error']}")
            else:
                print(
                    f"- {row['source']}: raw={row['raw']}, converted={row['converted']}, "
                    f"valid={row['valid']}, invalid={row['invalid']}, dropped={row['dropped']}"
                )

        print("\nTop valid items:")
        for i, inv in enumerate(preview["investments"]["valid"], start=1):
            srcs = inv.get("sources") or []
            best = srcs[0] if srcs else {}
            print(
                f"{i}. {inv.get('investor')} → {inv.get('investee')} | ${inv.get('amount_m_usd')}M | "
                f"{inv.get('stage')} | {inv.get('date')} | conf={inv.get('confidence')}"
            )
            if best.get("url"):
                print(f"   url: {best.get('url')}")
            if best.get("evidence_quote"):
                print(f"   evidence: {best.get('evidence_quote')}")

        if "invalid" in preview["investments"]:
            print("\nInvalid examples:")
            for row in preview["investments"]["invalid"]:
                print(f"- {row.get('title') or '(no title)'}")
                if row.get("url"):
                    print(f"  url: {row.get('url')}")
                if row.get("evidence_quote"):
                    print(f"  evidence: {row.get('evidence_quote')}")
                print(f"  reasons: {', '.join(row.get('reasons') or [])}")

    if "events" in preview:
        _print_header("EVENTS (preview)")
        s = preview["events"]["summary"]
        _print_kv("days_ahead", s["days_ahead"])
        _print_kv("valid_total", s["valid_total"])
        _print_kv("valid_deduped_upcoming", s["valid_deduped_upcoming"])
        _print_kv("invalid_total", s["invalid_total"])
        print("\nPer source:")
        for row in s["raw_sources"]:
            if row.get("error"):
                print(f"- {row['source']}: ERROR: {row['error']}")
            else:
                print(f"- {row['source']}: raw={row['raw']}, valid={row['valid']}, invalid={row['invalid']}")

        print("\nTop valid items:")
        for i, ev in enumerate(preview["events"]["valid"], start=1):
            srcs = ev.get("sources") or []
            best = srcs[0] if srcs else {}
            print(f"{i}. {ev.get('name')} | {ev.get('event_type')} | {ev.get('date')} | {ev.get('location')} | conf={ev.get('confidence')}")
            if ev.get("url"):
                print(f"   url: {ev.get('url')}")
            if best.get("evidence_quote"):
                print(f"   evidence: {best.get('evidence_quote')}")

        if "invalid" in preview["events"]:
            print("\nInvalid examples:")
            for row in preview["events"]["invalid"]:
                print(f"- {row.get('name') or '(no name)'} | {row.get('date')}")
                if row.get("url"):
                    print(f"  url: {row.get('url')}")
                print(f"  reasons: {', '.join(row.get('reasons') or [])}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Preview extracted data from real websites")
    parser.add_argument("--investments", action="store_true", help="Fetch/preview investment sources")
    parser.add_argument("--events", action="store_true", help="Fetch/preview event sources")
    parser.add_argument("--days-back", type=int, default=7, help="Investments: how many days back")
    parser.add_argument("--days-ahead", type=int, default=90, help="Events: how many days ahead")
    parser.add_argument("--max-items", type=int, default=10, help="Max items to print per category")
    parser.add_argument("--show-invalid", action="store_true", help="Include invalid items + reasons")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--out", type=str, default=None, help="Write output to a file")

    args = parser.parse_args()

    if not args.investments and not args.events:
        args.investments = True
        args.events = True

    preview: Dict[str, Any] = {
        "generated_at": datetime.now().isoformat(),
        "workspace_note": "This output reflects best-effort scraping and strict grounding validation.",
    }

    if args.investments:
        preview["investments"] = _preview_investments(
            days_back=args.days_back,
            max_items=args.max_items,
            show_invalid=args.show_invalid,
        )

    if args.events:
        preview["events"] = _preview_events(
            days_ahead=args.days_ahead,
            max_items=args.max_items,
            show_invalid=args.show_invalid,
        )

    if args.format == "json":
        out = json.dumps(preview, indent=2, sort_keys=False)
        if args.out:
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(out)
            print(f"Wrote {args.out}")
        else:
            print(out)
    else:
        if args.out:
            # render to a string by temporarily capturing print is overkill; just write JSON
            with open(args.out, "w", encoding="utf-8") as f:
                f.write(json.dumps(preview, indent=2, sort_keys=False))
            print(f"Wrote {args.out} (JSON)")
        _render_text(preview)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
