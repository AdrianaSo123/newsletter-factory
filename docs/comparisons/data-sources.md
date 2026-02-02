# Data sources comparison (events + investments)

Date: 2026-02-01

Goal of this project:
- Produce a newsletter about **who invested in whom** + **relevant AI events**.
- Stay **fact-rooted**: every published item must have a source URL and/or evidence quote.
- Prefer **$0** solutions unless paid APIs are truly required.

---

## Summary recommendation (if you want $0)

**Investments**
- Use **TechCrunch RSS + article parsing** (already implemented).
- Add a **free news discovery feed** (GDELT) to expand coverage.
- Treat all “deal facts” as *claims extracted from articles*, not an authoritative deal database.

**Events**
- Use **Eventbrite scraping** (already implemented).
- Add **Meetup best-effort scraping** (may be unreliable without an API key).
- Always keep a curated fallback list (already implemented via major conferences).

Why this works: it keeps your pipeline grounded by **evidence-first extraction + strict validation** (publish only if grounded).

---

## Decision criteria (what matters most)

1. **Grounding**: can we attach a URL + evidence quote?
2. **Stability**: will this break when HTML changes?
3. **Coverage**: how much of the world does it see?
4. **Cost**: free vs paid.
5. **Terms / compliance**: scraping and re-publication restrictions.
6. **Offline mode**: can we snapshot inputs so runs are repeatable?

---

## Investments: options

### Option A — Scraping / RSS (current approach)
Examples: TechCrunch RSS, VentureBeat site scrape, Crunchbase News RSS

- Cost: **$0**
- Data type: **articles** (unstructured)
- Strengths:
  - Easy to start.
  - Strong grounding story: every item naturally has a URL.
- Weaknesses:
  - Brittle (markup changes).
  - Extracting exact amounts/investors is noisy.
  - Coverage depends on editorial reporting.
- Best practice:
  - Store the article URL + a short evidence quote.
  - Add fixture-based tests from saved HTML snapshots.

### Option B — Crunchbase (Deal database API)
- Cost: **Paid** for meaningful usage.
- Data type: **structured funding rounds**
- Strengths:
  - Much easier “who invested in whom” queries.
  - More consistent data fields.
- Weaknesses:
  - Subscription cost.
  - Redistribution / usage restrictions can matter for newsletters.

### Option C — PitchBook / CB Insights (Deal databases)
- Cost: **expensive**.
- Data type: **structured and comprehensive**
- Strengths:
  - Best coverage + structure.
- Weaknesses:
  - Cost/access typically out of scope for student projects.

### Option D — GDELT (free news + metadata)
- Cost: **$0**
- Data type: **news discovery/search**
- Strengths:
  - Broad coverage across many sites.
  - Good at answering “find articles that mention funding” at scale.
- Weaknesses:
  - Still articles; you still need extraction.
  - Requires more filtering/dedup.
- Best use:
  - Use GDELT to find candidate URLs.
  - Then run your existing extraction + validation pipeline.

### Option E — NewsAPI (paid-ish)
- Cost: free tier is limited; full usefulness often paid.
- Data type: news discovery.
- Similar role to GDELT.

---

## Events: options

### Option A — Eventbrite scraping (current)
- Cost: **$0**
- Strengths:
  - No signup required.
  - Natural grounding (event URL).
- Weaknesses:
  - HTML structure changes.
  - Pagination/filtering can be inconsistent.

### Option B — Eventbrite API
- Cost: depends on access/policy.
- Strengths:
  - More stable than scraping.
- Weaknesses:
  - Token management + policy constraints.

### Option C — Meetup without API (scraping)
- Cost: **$0**
- Reality check:
  - Often unreliable: login walls, heavy JS, bot mitigation.
- When it’s still worth doing:
  - Best-effort extraction + fallback to curated lists.

### Option D — Meetup API (OAuth)
- Cost: usually **$0**, but requires an app + auth.
- Strengths:
  - Most reliable way to get Meetup events.
- Weaknesses:
  - More engineering (OAuth, user consent).
  - Not always available depending on Meetup’s current developer policies.

---

## How “fact-rooted validation” changes the choice

If your rule is:
- *No source URL or evidence quote → do not publish*

Then scraping/RSS becomes much more acceptable for a $0 project, because:
- it naturally provides citations,
- your validators can drop uncertain items safely.

But you must accept:
- some weeks will have fewer items (because invalid items get filtered),
- extraction quality work (fixtures/tests) is essential.

---

## Suggested roadmap (still $0)

1. Add fixture-based parsing tests for TechCrunch/VentureBeat/Eventbrite.
2. Add GDELT ingestion for broader investment coverage.
3. Add best-effort Meetup ingestion; keep curated fallbacks.
4. Add an offline “snapshot store” so daily runs are reproducible.

---

## What we have already in codebase (so far)

- Evidence model: `FactSource` on investments/events.
- Validation gate: items must be grounded.
- Rendering: newsletter prints evidence + source.
- Scrapers:
  - Investments: TechCrunch, VentureBeat, Crunchbase News.
  - Events: Eventbrite + curated major conferences.

(See sprint tracker for detailed status.)
