---
id: INT-13
title: Model-assisted reconciliation of wiki pages
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, sidecar, ui]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Model-assisted reconciliation of wiki pages

## Problem
A component page should say what the component is and does now. Source documents and the repository itself change, and the page falls behind. Today the server can tell a page is older than its sources, and can stitch source documents into a page, but it cannot understand them. Updating a page means a person or an agent reading everything and rewriting it by hand, which is why pages go stale.

## Proposed outcome
A model reads a component's source documents and the state of its repository and proposes a rewritten page. The change is shown as a diff. A person accepts, edits or rejects it. Nothing is written until they accept. The way the change is recorded (a direct commit or a pull request) follows the instance's change policy.

## Affected users and systems
- **Component owners** who keep pages current.
- **The model sidecar** (INT-10) and **tool layer** (INT-11), which do the reading and drafting.
- **The server's freshness check,** which finds the pages to reconcile.
- **The interface,** where the diff is reviewed.

## Constraints
- **A person accepts.** The model proposes; it never writes a page by itself.
- **Source-bound.** Every statement in a proposal can be traced to a source; unsupported claims are flagged, not hidden.
- **Content shown before it leaves** the machine to a hosted provider, as everywhere else.
- **Core stays model-free.** The work runs in the sidecar and writes through the normal tools, with the normal etag checks.
- **Repository text is data,** never instructions.
- **Works per page,** and can be run on a schedule only if the owner turns that on.

## Scenario seeds

### S1 — Find and fix a stale page
**Who:** A component owner.
**Wants:** To bring a stale page up to date.
**So that:** The wiki is accurate without a long manual rewrite.
**We will know when:** For a page flagged stale, the owner gets a proposed page and a diff against the current one, with each changed statement linked to its source.
**Must never:** Change the page before the owner accepts.

### S2 — Unsupported claims are visible
**Who:** A reviewer.
**Wants:** To see what the model made up.
**So that:** Errors do not enter the wiki.
**We will know when:** A statement with no supporting source is marked in the diff.
**Must never:** Present an invented detail as if it came from a source.

### S3 — A conflicting edit is not lost
**Who:** A person who edited the page while the proposal was being made.
**Wants:** Their edit to survive.
**So that:** Automation does not erase human work.
**We will know when:** Accepting a proposal made on an older version fails with a conflict, and the proposal can be redone against the new version.
**Must never:** Overwrite a newer page with a proposal built on an older one.

## Out of scope
- Creating pages for components not yet registered.
- Fully automatic rewriting with no review.
- Reconciliation of code or documents outside the wiki.

## Open questions
- Does a proposal go straight to the instance, or open a pull request? (the product owner)
- How much of a repository may the model read by default? (the product owner)
- Should scheduled runs exist in the first version? (the product owner)
