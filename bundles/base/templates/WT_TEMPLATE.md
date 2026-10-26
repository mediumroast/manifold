# WT_<NNN> — <short descriptive title>
<!--
  Walkthrough notes template.
  Copy this file to docs/walkthroughs/WT_<NNN>_<short-slug>.md, for example
  WT_001_interactions-list.md. Fill in everything above "Triage"; the
  bug-coder fills in the Triage section. Delete these comments first.
-->

## Session metadata
**Date:** YYYY-MM-DD
**Tester:** <name>
**App version / branch:** <branch name or commit SHA>
**Environment:** local dev | staging | other
**Related phase plan:** PHASE_<N>_PLAN.md (if applicable)

## Reference documents
<!-- Documents the bug-coder must read before triaging. Remove this section if none apply. -->
- `PHASE_<N>_PLAN.md` — implementation plan this walkthrough is certifying
- `PHASE_<N>_TEST_PLAN.md` — test plan for this phase
- `docs/<filename>.md` — <one-line description of relevance>

## Scope of this walkthrough
One short paragraph. What area of the app was walked through, what was being
looked for, and any known constraints (for example "only tested on Chrome
desktop, mobile not covered").

## Observations

Each observation is one discrete issue. Use one block per issue. Be as specific
as possible: route, element, action taken, what you expected, what actually
happened. Paste screenshots or console output below an observation.

---

### WT_<NNN>_001 — <short title>
**Route/screen:** <e.g. /interactions or the filter panel on /dashboard>
**Steps to reproduce:**
1.
2.
3.

**Expected:** <what should have happened>
**Actual:** <what actually happened>
**Severity guess:** P1 | P2 | P3
**Screenshot / console output:** (paste or attach if available)

---

### WT_<NNN>_002 — <short title>
**Route/screen:**
**Steps to reproduce:**
1.
2.

**Expected:**
**Actual:**
**Severity guess:** P1 | P2 | P3
**Screenshot / console output:**

---

<!-- Copy the block above for each additional observation -->

## General impressions
Optional. Freeform notes on overall feel, flow, or anything that felt off but
does not fit a discrete observation. The bug-coder treats these as low-priority
UX issues unless you flag otherwise.

---

## Triage (filled in by the bug-coder; the tester does not edit below this line)
<!--
  P1 broken or unusable; P2 significantly degrades the experience or risks data
  integrity; P3 minor or cosmetic.
  Classification: Bug | Regression | Data issue | Configuration or environment | Feature gap.
  Status: [ ] Open | [x] Fixed | [ ] Deferred | [~] Pending human confirmation.
  Do not close an item without the tester's confirmation.
-->

**Session date:** YYYY-MM-DD
**Branch:** <branch>
**Reference docs read:** <list each one>

| ID | Title | Priority | Classification | Status | Fix summary (file, what changed) |
|----|-------|----------|----------------|--------|----------------------------------|
| WT_<NNN>_001 | | P1 | Bug | [ ] Open | |

### Feature gaps recorded
<!-- Each deferred feature gap is also appended to FEATURE_GAPS.md in the project root: ID, source file, date, one-paragraph description, status "[ ] Pending, not yet picked up by the planner". -->
-
