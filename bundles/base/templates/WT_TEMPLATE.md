---
# Walkthrough notes template
# Copy this file and rename it WT_<NNN>_<short-slug>.md before filling in.
# Example: WT_001_interactions-list.md, WT_002_filter-behavior.md
---
 
# WT_<NNN> — <short descriptive title>
 
## Session metadata
**Date:** YYYY-MM-DD  
**Tester:** <name>  
**App version / branch:** <branch name or commit SHA>  
**Environment:** local dev | staging | other  
**Related phase plan:** PHASE_<N>_PLAN.md (if applicable)  
 
## Reference documents
List any documents the bug agent should read for context before triaging.
Remove this section if none apply.
 
- `PHASE_<N>_PLAN.md` — implementation plan this walkthrough is certifying
- `PHASE_<N>_TEST_PLAN.md` — test plan for this phase
- `docs/<filename>.md` — <one-line description of relevance>
## Scope of this walkthrough
One short paragraph. What area of the app was walked through, what was
being looked for, and any known constraints (e.g. "only tested on Chrome
desktop, mobile not covered").
 
## Observations
 
Each observation is one discrete issue. Use one block per issue.
Be as specific as possible — route, element, action taken, what you
expected, what actually happened. Screenshots or console output can be
pasted below an observation.
 
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
Optional. Freeform notes on overall feel, flow, or anything that felt
off but doesn't fit a discrete observation — the bug agent will treat
these as low-priority UX Issues unless you flag otherwise.