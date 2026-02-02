# Backlog (TDD-first)

## Product direction ("replace the human")

We are not building a newsletter editor.
We are building an automated operator that:
- Collects signals (investments + events + founder opportunities)
- Converts signals → structured facts
- Converts facts → decisions + recommended actions ("get them the coffee")
- Ships the output reliably

## Core problems to solve

1. Real data is fragile (site changes, rate limits, ToS constraints)
2. Data gets stale and can silently degrade
3. Extraction quality (amounts, investors, stage, dates) is noisy
4. Events need their own pipeline (dedupe, categorization, relevance)
5. We need confidence via tests: unit + integration + negative e2e

## Testing targets

- Unit: parsing helpers, normalization, amount parsing, stage inference
- Integration: aggregator + fallback behavior, cache freshness
- Negative E2E: "no internet" / "source layout changed" / "empty feed" still produces a safe newsletter

## Definition of Done for this project

- `python -m pytest` green
- `python example_real_data.py` runs and produces a newsletter OR falls back cleanly
- Data freshness report works and is test-covered
- Scraper failures never crash newsletter generation
