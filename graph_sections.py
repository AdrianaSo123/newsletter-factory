"""Newsletter sections powered by the evidence-first knowledge graph."""

from __future__ import annotations

from newsletter_factory import NewsletterSection
from knowledge_graph import KnowledgeGraph


class CoInvestmentNetworkSection(NewsletterSection):
    """Shows co-investor network signals, grounded by underlying sources."""

    def __init__(self, kg: KnowledgeGraph, *, max_pairs: int = 8):
        self.kg = kg
        self.max_pairs = max_pairs

    def generate(self) -> str:
        # Ensure derived edges exist.
        try:
            self.kg.derive_co_investments()
        except Exception:
            # If derivation fails for any reason, keep newsletter generation resilient.
            pass

        pairs = self.kg.top_co_investor_pairs(limit=self.max_pairs)

        content = ["## 🕸️ Network Signals", ""]
        content.append("*Co-investor relationships inferred from grounded funding items*\n")

        if not pairs:
            content.append("No co-investment relationships found in the current window.\n")
            return "\n".join(content)

        for a_name, b_name, edge in pairs:
            shared = edge.attrs.get("shared_investees", []) or []
            shared_txt = ", ".join(shared[:3])
            if len(shared) > 3:
                shared_txt += f" (+{len(shared) - 3} more)"

            try:
                shared_count = int(edge.attrs.get("shared_count", len(shared)))
            except Exception:
                shared_count = len(shared)

            content.append(f"### {a_name} ↔ {b_name}")
            if shared_txt:
                content.append(f"- **Shared investments:** {shared_count} ({shared_txt})")
            else:
                content.append(f"- **Shared investments:** {shared_count}")

            # Evidence: show one concrete citation
            sources = list(getattr(edge, "sources", []) or [])
            if sources:
                src = sources[0]
                if getattr(src, "evidence_quote", None):
                    content.append(f"- **Evidence:** \"{src.evidence_quote}\"")
                if getattr(src, "url", None):
                    content.append(f"- **Source:** {src.source_name} — {src.url}")
                else:
                    content.append(f"- **Source:** {src.source_name}")

            content.append("")

        return "\n".join(content)
