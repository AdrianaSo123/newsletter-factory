# Sprint 001 — Make it reliable (TDD)

## Sprint goal

Ship a pipeline that reliably produces a newsletter even when:
- the network is down
- a site changes markup
- feeds are empty

## User story

As a founder/aspiring AI entrepreneur,
I want a weekly digest of "who invested in whom" + "events to attend" + "what to do next",
so I can act without doing manual research.

## Scope

- Hardening: caching, freshness checks, fallback paths
- Testing: unit + integration + negative e2e
- Setup: one-command local setup so you can run it

## TDD plan (high level)

1) Unit tests first
- Amount parsing: $M/$B, commas, edge cases
- Stage inference: seed/series variants/unknown
- Company name extraction patterns

2) Integration tests
- Aggregator returns deduped Investment list
- RealTimeDataSource falls back to mock on scraper failure
- DataFreshnessMonitor staleness decisions

3) Negative E2E tests (must pass)
- Network disabled: newsletter still generates with fallback
- Empty events: events section renders safely
- Cache expired: refresh runs without exceptions

## Deliverables

- `tests/` suite (pytest)
- `scripts/setup_venv.sh` and `scripts/run_tests.sh`
- Minimal fixes required to make tests pass

## Acceptance criteria

- `./scripts/setup_venv.sh` succeeds on macOS
- `./scripts/run_tests.sh` passes
- Newsletter generation works without internet (fallback)
