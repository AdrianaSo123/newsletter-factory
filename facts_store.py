"""SQLite-backed facts store for grounded items.

Purpose
- Persist *validated, grounded* investments/events across runs.
- Make KG + newsletters reproducible even if scraping changes.

Design
- Use stdlib `sqlite3` only.
- Store fact rows + attached FactSource rows.
- Dedupe via deterministic IDs + unique constraints.

This is intentionally minimal; we can evolve it into a richer ETL later.
"""

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from hashlib import sha1
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from models import Company, FactSource, Investment
from newsletter_factory import InvestmentStage


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _norm(s: Optional[str]) -> str:
    return " ".join((s or "").strip().lower().split())


def investment_fact_id(inv: Investment) -> str:
    """Stable ID for an investment fact (best-effort)."""
    investor = _norm(getattr(getattr(inv, "investor", None), "name", ""))
    investee = _norm(getattr(getattr(inv, "investee", None), "name", ""))
    stage = getattr(getattr(inv, "stage", None), "value", "") or ""
    amount = ""
    try:
        amount = f"{float(inv.amount):.3f}"
    except Exception:
        amount = str(getattr(inv, "amount", ""))

    date = getattr(inv, "date", None)
    date_key = ""
    try:
        # Day precision is usually enough for news items.
        date_key = date.date().isoformat() if date else ""
    except Exception:
        date_key = str(date) if date else ""

    fp = "|".join([investor, investee, amount, stage, date_key])
    return "inv:" + sha1(fp.encode("utf-8")).hexdigest()[:20]


def event_fact_id(event: Any) -> str:
    """Stable ID for an event fact (duck-typed)."""
    name = _norm(getattr(event, "name", ""))
    url = _norm(getattr(event, "url", ""))
    date = getattr(event, "date", None)
    date_key = ""
    try:
        date_key = date.date().isoformat() if date else ""
    except Exception:
        date_key = str(date) if date else ""

    fp = "|".join([name, url, date_key])
    return "evt:" + sha1(fp.encode("utf-8")).hexdigest()[:20]


class FactsStore:
    def __init__(self, db_path: str | Path = "cache/facts.sqlite"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS investments (
                  id TEXT PRIMARY KEY,
                  investor_name TEXT NOT NULL,
                  investee_name TEXT NOT NULL,
                  amount_m_usd REAL NOT NULL,
                  stage TEXT,
                  date TEXT,
                  investee_sector TEXT,
                  investee_description TEXT,
                  investor_sector TEXT,
                  details TEXT,
                  confidence REAL,
                  ingested_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS events (
                  id TEXT PRIMARY KEY,
                  name TEXT NOT NULL,
                  event_type TEXT,
                  date TEXT,
                  location TEXT,
                  description TEXT,
                  url TEXT,
                  organizer TEXT,
                  topics_json TEXT,
                  target_audience TEXT,
                  cost TEXT,
                  registration_url TEXT,
                  confidence REAL,
                  ingested_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS sources (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  parent_type TEXT NOT NULL CHECK(parent_type IN ('investment','event')),
                  parent_id TEXT NOT NULL,
                  source_name TEXT NOT NULL,
                  url TEXT,
                  retrieved_at TEXT,
                  evidence_quote TEXT,
                  UNIQUE(parent_type, parent_id, source_name, url, evidence_quote)
                );

                CREATE INDEX IF NOT EXISTS idx_sources_parent ON sources(parent_type, parent_id);
                CREATE INDEX IF NOT EXISTS idx_investments_date ON investments(date);
                CREATE INDEX IF NOT EXISTS idx_events_date ON events(date);
                """
            )

    def upsert_investments(self, investments: Iterable[Investment]) -> Dict[str, int]:
        inserted = 0
        sources_inserted = 0

        with self._connect() as conn:
            for inv in investments:
                inv_id = investment_fact_id(inv)

                investor = getattr(inv, "investor", None)
                investee = getattr(inv, "investee", None)

                stage = getattr(getattr(inv, "stage", None), "value", None)
                date = getattr(inv, "date", None)
                date_iso = date.isoformat() if isinstance(date, datetime) else None

                try:
                    amount = float(inv.amount)
                except Exception:
                    # Skip unparseable amounts (should already be filtered by validation).
                    continue

                row = (
                    inv_id,
                    getattr(investor, "name", "") or "",
                    getattr(investee, "name", "") or "",
                    amount,
                    stage,
                    date_iso,
                    getattr(investee, "sector", None),
                    getattr(investee, "description", None),
                    getattr(investor, "sector", None),
                    getattr(inv, "details", None),
                    getattr(inv, "confidence", None),
                    _utc_now_iso(),
                )

                # Insert if new, otherwise keep the existing row (don’t overwrite history).
                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO investments(
                      id, investor_name, investee_name, amount_m_usd, stage, date,
                      investee_sector, investee_description, investor_sector, details,
                      confidence, ingested_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    row,
                )
                if cur.rowcount:
                    inserted += 1

                # Insert sources (deduped by UNIQUE constraint)
                for s in list(getattr(inv, "sources", []) or []):
                    cur2 = conn.execute(
                        """
                        INSERT OR IGNORE INTO sources(parent_type, parent_id, source_name, url, retrieved_at, evidence_quote)
                        VALUES ('investment',?,?,?,?,?)
                        """,
                        (
                            inv_id,
                            getattr(s, "source_name", "") or "",
                            getattr(s, "url", None),
                            getattr(s, "retrieved_at", None).isoformat() if getattr(s, "retrieved_at", None) else None,
                            getattr(s, "evidence_quote", None),
                        ),
                    )
                    if cur2.rowcount:
                        sources_inserted += 1

            conn.commit()

        return {"investments_inserted": inserted, "sources_inserted": sources_inserted}

    def upsert_events(self, events: Iterable[Any]) -> Dict[str, int]:
        inserted = 0
        sources_inserted = 0

        with self._connect() as conn:
            for ev in events:
                ev_id = event_fact_id(ev)

                date = getattr(ev, "date", None)
                date_iso = date.isoformat() if isinstance(date, datetime) else None

                topics = list(getattr(ev, "topics", []) or [])

                row = (
                    ev_id,
                    getattr(ev, "name", "") or "",
                    getattr(ev, "event_type", None),
                    date_iso,
                    getattr(ev, "location", None),
                    getattr(ev, "description", None),
                    getattr(ev, "url", None),
                    getattr(ev, "organizer", None),
                    json.dumps(topics),
                    getattr(ev, "target_audience", None),
                    getattr(ev, "cost", None),
                    getattr(ev, "registration_url", None),
                    getattr(ev, "confidence", None),
                    _utc_now_iso(),
                )

                cur = conn.execute(
                    """
                    INSERT OR IGNORE INTO events(
                      id, name, event_type, date, location, description, url, organizer,
                      topics_json, target_audience, cost, registration_url, confidence, ingested_at
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                    """,
                    row,
                )
                if cur.rowcount:
                    inserted += 1

                for s in list(getattr(ev, "sources", []) or []):
                    cur2 = conn.execute(
                        """
                        INSERT OR IGNORE INTO sources(parent_type, parent_id, source_name, url, retrieved_at, evidence_quote)
                        VALUES ('event',?,?,?,?,?)
                        """,
                        (
                            ev_id,
                            getattr(s, "source_name", "") or "",
                            getattr(s, "url", None),
                            getattr(s, "retrieved_at", None).isoformat() if getattr(s, "retrieved_at", None) else None,
                            getattr(s, "evidence_quote", None),
                        ),
                    )
                    if cur2.rowcount:
                        sources_inserted += 1

            conn.commit()

        return {"events_inserted": inserted, "sources_inserted": sources_inserted}

    def load_investments(self, *, days_back: int = 30) -> List[Investment]:
        """Load investments from DB for a date window (best-effort)."""
        cutoff = None
        try:
            cutoff = (datetime.utcnow().replace(microsecond=0) - __import__("datetime").timedelta(days=days_back)).isoformat()
        except Exception:
            cutoff = None

        with self._connect() as conn:
            if cutoff:
                rows = conn.execute(
                    """
                    SELECT * FROM investments
                    WHERE date IS NULL OR date >= ?
                    ORDER BY date DESC
                    """,
                    (cutoff,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM investments ORDER BY date DESC").fetchall()

            investments: List[Investment] = []
            for r in rows:
                inv_id = r["id"]

                # Load sources
                srows = conn.execute(
                    """
                    SELECT source_name, url, retrieved_at, evidence_quote
                    FROM sources
                    WHERE parent_type='investment' AND parent_id=?
                    """,
                    (inv_id,),
                ).fetchall()

                sources: List[FactSource] = []
                for sr in srows:
                    ra = sr["retrieved_at"]
                    dt = None
                    if ra:
                        try:
                            dt = datetime.fromisoformat(ra.replace("Z", ""))
                        except Exception:
                            dt = None
                    sources.append(
                        FactSource(
                            source_name=sr["source_name"],
                            url=sr["url"],
                            retrieved_at=dt,
                            evidence_quote=sr["evidence_quote"],
                        )
                    )

                # Parse stage
                stage_val = r["stage"]
                stage = InvestmentStage.SERIES_A
                if stage_val:
                    try:
                        stage = InvestmentStage(stage_val)
                    except Exception:
                        stage = InvestmentStage.SERIES_A

                # Parse date
                date_iso = r["date"]
                dt_date = datetime.utcnow()
                if date_iso:
                    try:
                        dt_date = datetime.fromisoformat(str(date_iso).replace("Z", ""))
                    except Exception:
                        dt_date = datetime.utcnow()

                investor = Company(
                    name=r["investor_name"],
                    description=f"Investor in {r['investee_name']}",
                    sector=r["investor_sector"] or "VC Firm",
                )
                investee = Company(
                    name=r["investee_name"],
                    description=r["investee_description"] or "",
                    sector=r["investee_sector"] or "AI",
                )

                investments.append(
                    Investment(
                        investor=investor,
                        investee=investee,
                        amount=float(r["amount_m_usd"]),
                        stage=stage,
                        date=dt_date,
                        details=r["details"],
                        sources=sources,
                        confidence=float(r["confidence"]) if r["confidence"] is not None else 0.5,
                    )
                )

            return investments

    def load_events(self, *, days_ahead: int = 90) -> List[Any]:
        """Load events from DB for a date window (best-effort)."""
        # Import lazily to avoid hard dependency outside event use.
        from scrapers.event_scrapers import AIEvent

        cutoff = None
        try:
            cutoff = (datetime.utcnow().replace(microsecond=0) + __import__("datetime").timedelta(days=days_ahead)).isoformat()
        except Exception:
            cutoff = None

        with self._connect() as conn:
            if cutoff:
                rows = conn.execute(
                    """
                    SELECT * FROM events
                    WHERE date IS NULL OR date <= ?
                    ORDER BY date ASC
                    """,
                    (cutoff,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM events ORDER BY date ASC").fetchall()

            events: List[AIEvent] = []
            for r in rows:
                ev_id = r["id"]

                srows = conn.execute(
                    """
                    SELECT source_name, url, retrieved_at, evidence_quote
                    FROM sources
                    WHERE parent_type='event' AND parent_id=?
                    """,
                    (ev_id,),
                ).fetchall()

                sources: List[FactSource] = []
                for sr in srows:
                    ra = sr["retrieved_at"]
                    dt = None
                    if ra:
                        try:
                            dt = datetime.fromisoformat(ra.replace("Z", ""))
                        except Exception:
                            dt = None
                    sources.append(
                        FactSource(
                            source_name=sr["source_name"],
                            url=sr["url"],
                            retrieved_at=dt,
                            evidence_quote=sr["evidence_quote"],
                        )
                    )

                date_iso = r["date"]
                dt_date = datetime.utcnow()
                if date_iso:
                    try:
                        dt_date = datetime.fromisoformat(str(date_iso).replace("Z", ""))
                    except Exception:
                        dt_date = datetime.utcnow()

                topics = []
                if r["topics_json"]:
                    try:
                        topics = json.loads(r["topics_json"]) or []
                    except Exception:
                        topics = []

                events.append(
                    AIEvent(
                        name=r["name"],
                        event_type=r["event_type"] or "Event",
                        date=dt_date,
                        location=r["location"] or "",
                        description=r["description"] or "",
                        url=r["url"],
                        organizer=r["organizer"],
                        topics=topics,
                        target_audience=r["target_audience"] or "All",
                        cost=r["cost"] or "",
                        registration_url=r["registration_url"],
                        sources=sources,
                        confidence=float(r["confidence"]) if r["confidence"] is not None else 0.5,
                    )
                )

            return events
