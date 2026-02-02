# Sprint 003 — "Get them the coffee" actions (TDD)

## Sprint goal

Make the newsletter output actionable:
- who should I talk to
- what should I build
- what event should I attend this week

## Approach

Treat the system like an automated operator:
Inputs: investments + events
Outputs: a set of recommended actions

## TDD plan

- Unit tests for a new Action Engine
  - scoring relevance by sector + stage + geography + event type
  - generating "next steps" checklists
  - negative cases: missing fields, empty inputs

- Integration tests
  - actions generated from mock investment/event sets

- Negative E2E
  - if investments empty, actions suggest sourcing signals and attending events

## Deliverables

- `actions.py` with deterministic rules-first engine (LLM optional later)
- new newsletter sections: "Recommended Actions" + "People to meet" + "Build ideas"
