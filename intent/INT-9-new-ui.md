---
id: INT-9
title: A new user interface for Manifold
author: Michael Hay
created: 2026-10-31
status: draft
affects: [ui, server, docker, ci]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A new user interface for Manifold

## Problem
The only interface is a read-only wiki browser built from a documentation tool. It cannot search well, show the handoff lifecycle as a board, carry a person's identity, or host the editors planned for later. People who are not working in an AI client cannot do anything with the wiki beyond reading it.

## Proposed outcome
A new interface, built in Deno with Fresh and Preact, that replaces the browser. The first release lets a signed-in person browse, search, and see handoffs on a read-only board. It talks to the Python server through the same tools agents use. It follows the approved design (INT-8). Later releases add editors on the same base.

## Affected users and systems
- **People who read and follow the wiki,** and administrators.
- **The Python server,** which the interface calls through MCP, and the identity it relies on (INT-1).
- **The container setup and CI,** which now build and test a second toolchain.

## Constraints
- **Built to the approved design** (INT-8) and not before it exists.
- **Identity is carried properly.** The interface signs in a person and passes a short-lived, signed identity to the server. It never holds one shared credential that claims to be a user.
- **Same tools as agents.** No private back door into the wiki; types are generated from the tool list so they cannot drift.
- **Offline-clean.** No outside requests at runtime.
- **Two toolchains stay manageable:** one command to build and test everything, and CI that runs both.
- **Accessible** to the standard set in the design.

## Scenario seeds

### S1 — Browse and search
**Who:** A team member.
**Wants:** To find a page and read it.
**So that:** They do not need an AI client to see the wiki.
**We will know when:** After signing in they can open a component page and a search for a word in it finds it within a second on the example instance.
**Must never:** Show a page to someone who is not signed in.

### S2 — See the handoffs as a board
**Who:** A team lead.
**Wants:** A board of handoffs grouped by state.
**So that:** They see what is waiting on whom.
**We will know when:** The board shows open, in progress, needs review and completed handoffs matching the wiki, and a new handoff made by an agent appears after a refresh.
**Must never:** Let the board change a handoff in the first release (it is read-only).

### S3 — Acting as the signed-in person
**Who:** An auditor.
**Wants:** The history to show who did what.
**So that:** Actions through the interface are as traceable as agents' actions.
**We will know when:** A change made later through the interface appears in history under the person's identity, not a shared one.
**Must never:** Use one shared credential to act for all users.

## Out of scope
- The intent editor (INT-12), the review queue (INT-16) and any model features.
- Editing pages in the first release.
- A mobile app.

## Open questions
- Does the interface replace the old browser at once, or run beside it for a while? (the product owner)
- How is the interface served: its own port, or behind the same address as the server? (the product owner)
- Which sign-in method does the first release support? (the product owner)
