---
id: INT-15
title: Turn a handoff into a GitHub issue
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Turn a handoff into a GitHub issue

## Problem
A handoff asks another component's team to do work, but the people and tools of that team often live in GitHub issues and project boards. A handoff in the wiki that nobody sees in their normal tools goes unnoticed, and someone has to copy it by hand into an issue and keep the two in step.

## Proposed outcome
A component can opt in to having each handoff addressed to it appear as an issue in its repository. The issue links back to the handoff, and the handoff's status is reflected in the issue. The wiki stays the record: changes made in the issue only propose a change to the handoff, and a person confirms them. Nothing is lost if GitHub is unreachable.

## Affected users and systems
- **Teams that work from GitHub issues** and boards.
- **The server,** which gains an optional action and a setting per component.
- **GitHub,** through the App (INT-7) and the API store's identity (INT-14).

## Constraints
- **Opt in per component:** off, manual, or automatic.
- **One-way by default:** handoff to issue. Inbound changes are proposals, never automatic edits of the handoff.
- **No private text in public places.** A handoff addressed to a component with a public repository is checked first, and private content is not copied into a public issue.
- **Nothing lost on failure.** If GitHub cannot be reached, the request is kept and retried, and the handoff is not blocked.
- **No duplicates.** A handoff has at most one issue; retries do not create more.
- **Needs the App** and does not use a person's personal token.

## Scenario seeds

### S1 — A handoff shows up as an issue
**Who:** A target component's team.
**Wants:** To see a new handoff where they already work.
**So that:** It is picked up.
**We will know when:** With the setting on, creating a handoff produces one issue in the target repository, titled for the handoff and linking to it.
**Must never:** Create two issues for one handoff.

### S2 — Status follows
**Who:** The source team.
**Wants:** The issue to show the handoff's state.
**So that:** Both sides see the same status.
**We will know when:** Claiming and completing the handoff updates the issue's labels or state to match.
**Must never:** Close the issue when the handoff is still open.

### S3 — Private text stays private
**Who:** The source team with a sensitive handoff.
**Wants:** Nothing private in a public issue.
**So that:** A leak is not caused by a convenience.
**We will know when:** For a public target repository, the action warns and blocks until the content is confirmed safe or reduced to a link.
**Must never:** Copy the full handoff into a public issue without that confirmation.

### S4 — GitHub is unreachable
**Who:** An agent creating a handoff during an outage.
**Wants:** The handoff to still be created.
**So that:** Work is not blocked by an outside service.
**We will know when:** The handoff is saved, the issue request is queued, and the issue appears once GitHub is reachable again.
**Must never:** Lose the request or fail the handoff.

## Out of scope
- Syncing comments in both directions.
- Project boards.
- Systems other than GitHub.

## Open questions
- Is the first release manual only, or manual and automatic? (the product owner)
- Which issue fields and labels should map to the handoff's type and priority? (the product owner)
