# Sprint 002 — Improve extraction quality (TDD)

## Sprint goal

Increase precision of extracted facts (amount, investor, stage, company, date)
so the newsletter reads like a human analyst wrote it.

## TDD plan

- Add parsing helpers module (pure functions) and unit test it heavily:
  - currency parsing: "$12M", "$12 million", "$1.2B", "€", "£" (support later)
  - investor phrase patterns: "led by", "participation from", "backed by"
  - date parsing: ISO + "Jan 12, 2026"
  - company name extraction with stopwords and punctuation

- Integration tests
  - Given fixed HTML snapshots (stored under `tests/fixtures/`), extraction remains stable

- Negative tests
  - Given malformed HTML, parser returns None safely (no crash)

## Deliverables

- `parsing/` module (new)
- fixtures-based integration tests
- improved dedupe keys (company+date+amount)
