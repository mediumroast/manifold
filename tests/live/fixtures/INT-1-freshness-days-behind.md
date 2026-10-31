---
id: INT-1
title: Show how far behind a component page is
author: Live Protocol
created: 2026-10-27
status: accepted
affects: [mcp-server]
drafted_with: []
accepted_by: Live Protocol 2026-10-27
---

# Intent: Show how far behind a component page is

## Problem
`wiki_freshness` says a component is "stale" or "fresh", but a maintainer cannot tell whether a page is a day behind its newest source document or a year behind. They have to open the files and compare dates by hand.

## Proposed outcome
For every component the freshness report also says **how many days** the wiki page is behind its newest raw source document, so a maintainer can sort by urgency.

## Affected users and systems
Wiki maintainers; the freshness tool in `mcp-server`.

## Constraints
- Existing callers must receive **byte-identical responses**; nothing may change in what they get today.
- Every component entry in the response must include a new `days_behind` field.
- No new dependencies.

## Scenario seeds

### S1 — Urgency at a glance
**Who:** a wiki maintainer
**Wants:** to see how many days each stale component is behind
**So that:** they refresh the most out-of-date pages first
**We will know when:** the report shows a whole number of days for every stale component
**Must never:** show a negative number of days, or a number for a component whose status is unknown

### S2 — Fresh pages stay quiet
**Who:** a wiki maintainer
**Wants:** fresh components to be clearly fresh
**So that:** they ignore them
**We will know when:** a fresh component shows zero days behind or no number, consistently
**Must never:** flag a fresh component as behind

## Out of scope
- Notifications or scheduling.

## Open questions
- Should unknown components show `null` or omit the field?
