# Sprint Execution Tracker

Date baseline: **February 1, 2026**

This file is the single source of truth for what work was done, what is next, and what’s blocked.

---

## ✅ Completed (so far)

### Sprint 001 — Make it reliable (TDD)

**Goal:** newsletter generation is resilient to failures (network down, markup changes, empty feeds).

- [x] Create `sprints/` planning folder and sprint docs
- [x] Add pytest test structure: unit/integration/e2e
- [x] Add negative E2E test: “no network” still generates newsletter output
- [x] Add integration test: `RealTimeDataSource` falls back to mock data when scraping fails
- [x] Add unit tests: models + factory + cache behavior
- [x] Add `pytest.ini` to standardize test discovery
- [x] Add `scripts/setup_venv.sh` to fix local setup and `Exit Code: 127` issues
- [x] Add `scripts/run_tests.sh` for one-command test execution
- [x] Verify test suite passes locally (`10 passed`)

**Artifacts created/updated:**
- [pytest.ini](../pytest.ini)
- [tests/](../tests/)
- [scripts/setup_venv.sh](../scripts/setup_venv.sh)
- [scripts/run_tests.sh](../scripts/run_tests.sh)
- [sprints/000-backlog.md](000-backlog.md)
- [sprints/001-sprint-plan.md](001-sprint-plan.md)
- [sprints/002-sprint-plan.md](002-sprint-plan.md)
- [sprints/003-sprint-plan.md](003-sprint-plan.md)

---

## 🟡 In progress

### Sprint 002 — Improve extraction quality (TDD)

**Goal:** extracted facts are precise and stable over time.

- [x] Create `parsing/` module with pure functions (no network)
  - [x] `parse_money_usd_millions()` ($M/$B, commas, “million/billion”, edge cases)
  - [x] `infer_stage()` (seed/series variants)
  - [x] `extract_company_name_from_title()` (conservative title parsing)
  - [x] `extract_investor_names()` ("led by", "backed by", "participation")
- [ ] Add fixtures for HTML/RSS snapshots to lock parsing behavior
  - [ ] `tests/fixtures/techcrunch_article_*.html`
  - [ ] `tests/fixtures/venturebeat_article_*.html`
- [ ] Add integration tests that parse fixtures (no live web dependencies)
- [x] Improve dedupe key (e.g., company + date + amount) and cover with tests
- [ ] Add negative tests for malformed/empty HTML (return `None`, no exceptions)
- [x] Add validation layer to drop ungrounded facts (investments + events)
- [x] Render evidence + source URL in newsletter output
- [x] Add unit tests enforcing “no grounding → invalid”

---

## ⏭️ Next up

### Sprint 003 — “Get them the coffee” actions (TDD)

**Goal:** output is actionable (recommended actions) rather than just information.

- [ ] Implement deterministic “Action Engine” (rules-first) with unit tests
- [ ] Add newsletter sections: “Recommended Actions”, “People to meet”, “Build ideas”
- [ ] Add integration tests that actions generate from mock investment/event sets
- [ ] Add negative E2E: if investments empty, suggest events + signal sourcing

---

## 📓 Work log (append-only)

### 2026-02-01
- Created sprint planning docs and centralized tracker.
- Added pytest suite with unit/integration/negative-e2e coverage.
- Added setup scripts to resolve local setup errors and make running tests reproducible.
- Ran and confirmed all tests passing.
- Added a parsing/extraction module with unit tests.
- Added evidence + confidence fields to extracted investments.
- Added validators to filter ungrounded/invalid investments and events.
- Updated newsletter sections to render evidence + source URLs.
- Ran and confirmed all tests passing (`25 passed`).

---

## Rules of engagement (how we update this file)

- Every time we start a task: add it under **In progress** and keep it checked off as it completes.
- Every time we finish a task: move it to **Completed** (or mark `[x]` in place).
- Every meaningful change: append 1–3 bullets to the **Work log** with date.
