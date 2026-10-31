# WT_001 — Freshness ignores dates in some raw filenames

## Session metadata
**Date:** 2026-10-27
**Tester:** Live Protocol
**App version / branch:** live-protocol
**Environment:** local dev
**Related phase plan:** none

## Reference documents
- `mcp-server/wiki_backend/freshness.py`

## Scope of this walkthrough
Checked how `wiki_freshness` decides whether a raw document is newer than a component page.

## Observations

---

### WT_001_001 — A raw document named only with its date is dated by when the file was touched, not by its name
**Route/screen:** `wiki_freshness` for a component whose raw folder contains `2026-05-09.md`
**Steps to reproduce:**
1. Create `raw/<component>/2026-05-09.md`.
2. Touch the file so its modification time is today.
3. Run the freshness report for that component.

**Expected:** the document counts as dated 2026-05-09, so a page last updated on 2026-06-01 is fresh.
**Actual:** the document counts as dated today and the component is reported stale. A file named `2026-05-09-notes.md` behaves correctly.
**Severity guess:** P2
**Screenshot / console output:** none

---

## General impressions
Only date-only filenames seem affected.
