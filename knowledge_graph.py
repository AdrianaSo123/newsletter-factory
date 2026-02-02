"""Evidence-first knowledge graph for the newsletter.

Goal: represent relationships (e.g., investor -> investee) *only* when they are
backed by grounded inputs (FactSource url/evidence_quote). This lets the
newsletter generate insights that can be cited.

The graph is intentionally lightweight (no external deps).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from hashlib import sha1
from typing import Any, Dict, Iterable, List, Optional, Tuple

from models import Company, FactSource, Investment


class NodeKind(str, Enum):
    COMPANY = "company"


class EdgeKind(str, Enum):
    INVESTED_IN = "invested_in"
    CO_INVESTED_WITH = "co_invested_with"
    # Derived relationships can be added later (e.g., CO_INVESTED_WITH), but must
    # always carry derivation info + underlying sources.


def _norm_name(name: str) -> str:
    return " ".join((name or "").strip().lower().split())


@dataclass(frozen=True)
class KGNode:
    id: str
    kind: NodeKind
    name: str
    attrs: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KGEdge:
    id: str
    kind: EdgeKind
    src: str
    dst: str
    attrs: Dict[str, Any] = field(default_factory=dict)
    sources: List[FactSource] = field(default_factory=list)
    derived_from: List[str] = field(default_factory=list)


class KnowledgeGraph:
    """A small in-memory property graph with provenance."""

    def __init__(self):
        self.nodes: Dict[str, KGNode] = {}
        self.edges: Dict[str, KGEdge] = {}
        self._company_key_to_node_id: Dict[str, str] = {}

    def upsert_company(self, company: Company) -> str:
        name = (company.name or "").strip()
        if not name:
            raise ValueError("company name required")

        key = _norm_name(name)
        existing = self._company_key_to_node_id.get(key)
        if existing:
            return existing

        node_id = f"company:{sha1(key.encode('utf-8')).hexdigest()[:12]}"
        attrs: Dict[str, Any] = {}
        # Keep these as attributes; they might be inferred upstream.
        if getattr(company, "sector", None):
            attrs["sector"] = company.sector
        if getattr(company, "website", None):
            attrs["website"] = company.website

        node = KGNode(id=node_id, kind=NodeKind.COMPANY, name=name, attrs=attrs)
        self.nodes[node_id] = node
        self._company_key_to_node_id[key] = node_id
        return node_id

    def add_investment(self, inv: Investment) -> str:
        """Add an INVESTED_IN edge with provenance.

        NOTE: This does not decide whether an investment is valid. Callers should
        validate investments (see validation.validate_investment) before adding.
        """

        investor_id = self.upsert_company(inv.investor)
        investee_id = self.upsert_company(inv.investee)

        date = getattr(inv, "date", None)
        date_iso = date.isoformat() if isinstance(date, datetime) else None

        # Edge ID: stable-ish across runs for same relationship.
        fingerprint = "|".join(
            [
                EdgeKind.INVESTED_IN.value,
                investor_id,
                investee_id,
                str(getattr(inv, "amount", "")),
                str(getattr(getattr(inv, "stage", None), "value", "")),
                date_iso or "",
            ]
        )
        edge_id = f"edge:{sha1(fingerprint.encode('utf-8')).hexdigest()[:16]}"

        attrs: Dict[str, Any] = {
            "amount_m_usd": float(inv.amount),
            "stage": getattr(getattr(inv, "stage", None), "value", None),
            "date": date_iso,
        }

        sources = list(getattr(inv, "sources", []) or [])

        if edge_id in self.edges:
            # Merge sources (dedupe by (source_name,url,evidence_quote)).
            existing = self.edges[edge_id]
            seen = {(s.source_name, s.url, s.evidence_quote) for s in existing.sources}
            for s in sources:
                key = (s.source_name, s.url, s.evidence_quote)
                if key not in seen:
                    existing.sources.append(s)
                    seen.add(key)
            return edge_id

        self.edges[edge_id] = KGEdge(
            id=edge_id,
            kind=EdgeKind.INVESTED_IN,
            src=investor_id,
            dst=investee_id,
            attrs=attrs,
            sources=sources,
        )
        return edge_id

    def build_from_investments(self, investments: Iterable[Investment]) -> "KnowledgeGraph":
        for inv in investments:
            self.add_investment(inv)
        return self

    def derive_co_investments(self, *, max_sources_per_edge: int = 4) -> int:
        """Derive CO_INVESTED_WITH edges from INVESTED_IN edges.

        Definition:
        - For each investee (dst), if >=2 distinct investors (src) invested,
          create an undirected co-investment relation between each investor pair.

        Provenance:
        - The derived edge stores `derived_from` (the underlying INVESTED_IN edge IDs)
          and merges their `FactSource` evidence into `sources`.

        Returns:
          Number of derived edges created (newly added).
        """

        # Group underlying edges by investee.
        by_investee: Dict[str, List[KGEdge]] = {}
        for e in self.edges.values():
            if e.kind != EdgeKind.INVESTED_IN:
                continue
            by_investee.setdefault(e.dst, []).append(e)

        created = 0

        def _edge_id_for_pair(a: str, b: str) -> str:
            lo, hi = (a, b) if a < b else (b, a)
            fp = "|".join([EdgeKind.CO_INVESTED_WITH.value, lo, hi])
            return f"edge:{sha1(fp.encode('utf-8')).hexdigest()[:16]}"

        for investee_id, edges in by_investee.items():
            # Distinct investors for this investee.
            investors = sorted({e.src for e in edges})
            if len(investors) < 2:
                continue

            # Build lookup to fetch underlying edges for (investor -> investee)
            underlying_by_investor: Dict[str, List[KGEdge]] = {}
            for e in edges:
                underlying_by_investor.setdefault(e.src, []).append(e)

            investee_node = self.nodes.get(investee_id)
            investee_name = investee_node.name if investee_node else investee_id

            for i in range(len(investors)):
                for j in range(i + 1, len(investors)):
                    a = investors[i]
                    b = investors[j]
                    edge_id = _edge_id_for_pair(a, b)

                    # Underlying evidence: all investment edges for these investors into this investee.
                    underlying_edges = (underlying_by_investor.get(a, []) or []) + (underlying_by_investor.get(b, []) or [])
                    derived_from = [ue.id for ue in underlying_edges]

                    sources: List[FactSource] = []
                    for ue in underlying_edges:
                        sources.extend(list(ue.sources or []))

                    # Dedupe sources.
                    seen = set()
                    deduped: List[FactSource] = []
                    for s in sources:
                        key = (s.source_name, s.url, s.evidence_quote)
                        if key in seen:
                            continue
                        seen.add(key)
                        deduped.append(s)
                        if len(deduped) >= max_sources_per_edge:
                            break

                    attrs = {
                        "shared_investee": investee_name,
                        "shared_investee_node": investee_id,
                        "shared_count": 1,
                    }

                    if edge_id in self.edges:
                        # Merge: increment count if this investee wasn't already counted.
                        existing = self.edges[edge_id]
                        if existing.kind != EdgeKind.CO_INVESTED_WITH:
                            continue

                        # Track multiple shared investees.
                        shared = existing.attrs.get("shared_investees")
                        if not isinstance(shared, list):
                            shared = []
                        if investee_name not in shared:
                            shared.append(investee_name)
                            existing.attrs["shared_investees"] = shared
                            try:
                                existing.attrs["shared_count"] = int(existing.attrs.get("shared_count", 0)) + 1
                            except Exception:
                                existing.attrs["shared_count"] = 1

                        # Merge provenance.
                        existing_df = set(existing.derived_from or [])
                        for did in derived_from:
                            if did not in existing_df:
                                existing.derived_from.append(did)
                                existing_df.add(did)

                        existing_seen = {(s.source_name, s.url, s.evidence_quote) for s in (existing.sources or [])}
                        for s in deduped:
                            key = (s.source_name, s.url, s.evidence_quote)
                            if key not in existing_seen:
                                existing.sources.append(s)
                                existing_seen.add(key)

                        continue

                    # Store as a canonical (undirected) edge: src=lo, dst=hi
                    lo, hi = (a, b) if a < b else (b, a)
                    self.edges[edge_id] = KGEdge(
                        id=edge_id,
                        kind=EdgeKind.CO_INVESTED_WITH,
                        src=lo,
                        dst=hi,
                        attrs={
                            "shared_investees": [investee_name],
                            "shared_count": 1,
                        },
                        sources=deduped,
                        derived_from=derived_from,
                    )
                    created += 1

        return created

    def top_co_investor_pairs(self, *, limit: int = 10) -> List[Tuple[str, str, KGEdge]]:
        """Return top co-investor pairs by shared_count."""
        pairs: List[Tuple[str, str, KGEdge]] = []
        for e in self.edges.values():
            if e.kind != EdgeKind.CO_INVESTED_WITH:
                continue
            a = self.nodes.get(e.src)
            b = self.nodes.get(e.dst)
            if not a or not b:
                continue
            pairs.append((a.name, b.name, e))

        def score(t: Tuple[str, str, KGEdge]) -> int:
            try:
                return int(t[2].attrs.get("shared_count", 0))
            except Exception:
                return 0

        pairs.sort(key=score, reverse=True)
        return pairs[:limit]

    def investments_for_company(self, company_name: str) -> List[KGEdge]:
        node_id = self._company_key_to_node_id.get(_norm_name(company_name))
        if not node_id:
            return []
        return [
            e
            for e in self.edges.values()
            if e.kind == EdgeKind.INVESTED_IN and (e.src == node_id or e.dst == node_id)
        ]

    def investors_of(self, company_name: str) -> List[Tuple[str, KGEdge]]:
        """Return list of (investor_company_name, edge)."""
        node_id = self._company_key_to_node_id.get(_norm_name(company_name))
        if not node_id:
            return []
        out: List[Tuple[str, KGEdge]] = []
        for e in self.edges.values():
            if e.kind != EdgeKind.INVESTED_IN:
                continue
            if e.dst != node_id:
                continue
            investor_node = self.nodes.get(e.src)
            if investor_node:
                out.append((investor_node.name, e))
        return out

    def portfolio_of(self, investor_name: str) -> List[Tuple[str, KGEdge]]:
        """Return list of (investee_company_name, edge)."""
        node_id = self._company_key_to_node_id.get(_norm_name(investor_name))
        if not node_id:
            return []
        out: List[Tuple[str, KGEdge]] = []
        for e in self.edges.values():
            if e.kind != EdgeKind.INVESTED_IN:
                continue
            if e.src != node_id:
                continue
            investee_node = self.nodes.get(e.dst)
            if investee_node:
                out.append((investee_node.name, e))
        return out

    def to_json_dict(self) -> Dict[str, Any]:
        def src_to_dict(s: FactSource) -> Dict[str, Any]:
            return {
                "source_name": s.source_name,
                "url": s.url,
                "retrieved_at": s.retrieved_at.isoformat() if getattr(s, "retrieved_at", None) else None,
                "evidence_quote": s.evidence_quote,
            }

        return {
            "nodes": [
                {"id": n.id, "kind": n.kind.value, "name": n.name, "attrs": dict(n.attrs)}
                for n in self.nodes.values()
            ],
            "edges": [
                {
                    "id": e.id,
                    "kind": e.kind.value,
                    "src": e.src,
                    "dst": e.dst,
                    "attrs": dict(e.attrs),
                    "sources": [src_to_dict(s) for s in (e.sources or [])],
                    "derived_from": list(e.derived_from or []),
                }
                for e in self.edges.values()
            ],
        }

    def to_dot(self) -> str:
        """Graphviz DOT output (simple, for quick visualization)."""
        lines = ["digraph newsletter_kg {", "  rankdir=LR;", "  node [shape=box];"]

        for n in self.nodes.values():
            safe_name = n.name.replace('"', "'")
            lines.append(f'  "{n.id}" [label="{safe_name}"];')

        for e in self.edges.values():
            label = e.kind.value
            amt = e.attrs.get("amount_m_usd")
            if amt is not None:
                try:
                    label = f"{label} (${float(amt):.1f}M)"
                except Exception:
                    pass
            lines.append(f'  "{e.src}" -> "{e.dst}" [label="{label}"];')

        lines.append("}")
        return "\n".join(lines)
