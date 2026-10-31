---
id: PHASE_1
title: Add days_behind to freshness report
source_intent: INT-1 (intent/INT-1-freshness-days-behind.md)
created: 2026-10-29
status: draft
---

**Approved by:** <!-- name and YYYY-MM-DD -->
**Source intent:** INT-1 — intent/INT-1-freshness-days-behind.md

## Objective

When `wiki_freshness` runs, every stale entry in the response includes a `days_behind` integer — the number of calendar days between the wiki page's `last_updated` date and the newest raw source document — so a maintainer can sort stale components by urgency without opening files. Fresh and unknown entries are unchanged.

## Scope

**In scope:**
- Add `days_behind` (non-negative integer) to each dict in `result["stale"]`.
- Regression tests covering correct value, never-negative guarantee, and absence of the field on fresh and unknown entries.

**Out of scope:**
- Changing the structure of `result["fresh"]` (stays a list of strings).
- Changing the structure of `result["unknown"]`.
- Notifications, scheduling, or sorting logic.

**Needs from other repositories:** None.

**Provides to other repositories:** None.

## Concerns flagged

1. **"Byte-identical" vs. "every entry includes `days_behind`"** — The intent constraint says existing callers receive byte-identical responses, yet also says every component entry must include a new `days_behind` field. These conflict: adding a field to stale dicts is not byte-identical. Resolution proposed: add `days_behind` only to stale entries (where it is actionable); fresh stays as strings and unknown stays unchanged. This satisfies scenario seeds S1 and S2 and avoids breaking callers of the fresh list. **Unresolved — decision deferred.**

2. **Unknown components: null vs. omit** — Resolved: omit `days_behind` from unknown entries entirely, consistent with S1 ("Must never show a number for a component whose status is unknown").

## Prerequisites

- [~] Concern 1 (byte-identical) — unresolved; coder proceeds under the proposed resolution and must not change fresh/unknown shapes.
- [x] Concern 2 resolved: omit `days_behind` from unknown entries.

## File inventory

| Path | Action | Reason |
|------|--------|--------|
| `mcp-server/wiki_backend/freshness.py` | MODIFY | Add `days_behind` computation and field to stale entries |
| `mcp-server/tests/test_freshness.py` | MODIFY | Add tests for `days_behind` correctness and absence on fresh/unknown |

## Tasks

> **Instructions for the coder:**
> Work tasks in the order listed. For each task: read the named files first,
> implement the described change, run the verify command and the task's
> acceptance check, then update the todo marker `[ ]` → `[x]` and add a
> one-line completion note directly beneath the task header: what changed, the
> command run, the result. If a task is blocked, mark it `[~]` with a note and
> surface it immediately; do not skip ahead. When all tasks are complete, fill
> in the completion summary under the Completion checklist.

### Task 1 — Add days_behind to stale entries in wiki_freshness
**Files:** `mcp-server/wiki_backend/freshness.py`
**Action:** MODIFY
**Change:** In the loop that builds stale entries, after the existing `newer` list comprehension, compute `max_newer_date = max(file_date for _, file_date in all_raw if file_date > last_updated)` and add `"days_behind": (max_newer_date - last_updated).days` to the stale dict. The existing four fields (`component`, `wiki_page`, `last_wiki_update`, `newer_raw_docs`) must not change. No other code paths are touched.
**Acceptance:** `cd mcp-server && ../.venv/bin/python -m pytest -q tests/test_freshness.py` passes with no failures; stale entries in a manual smoke call include `days_behind` as a positive integer.
**Todo:** [ ]

---

### Task 2 — Add regression tests for days_behind
**Files:** `mcp-server/tests/test_freshness.py`
**Action:** MODIFY
**Change:** Add four new test functions following the existing `_make_component` / `_make_raw_doc` helper pattern:
- `test_stale_entry_has_days_behind` — single newer doc dated 10 days after `last_updated`; asserts `entry["days_behind"] == 10`.
- `test_days_behind_uses_newest_raw_doc` — two newer docs dated 5 and 12 days after `last_updated`; asserts `entry["days_behind"] == 12`.
- `test_days_behind_never_negative` — stale entry; asserts `entry["days_behind"] >= 0`.
- `test_fresh_entry_has_no_days_behind` — fresh component (string in result["fresh"]); asserts no dict with `days_behind` appears for that slug, and the string slug is still present.
**Acceptance:** `cd mcp-server && ../.venv/bin/python -m pytest -q tests/test_freshness.py` passes with all four new tests green and zero existing tests failing.
**Todo:** [ ]

---

## Completion checklist

- [ ] All tasks marked [x] by the coder
- [ ] `cd mcp-server && ../.venv/bin/python -m pytest -q .` passes clean (no regressions)
- [ ] No [~] blocked items outstanding
- [ ] Summary note added by the coder below this line

<!--
  coder: add your completion summary here:
  - Files changed
  - Deviations from the plan, and why ("None." if none)
  - Verification evidence: command and result for each check; anything not run, and why
  - Deferred items and follow-ups
-->
