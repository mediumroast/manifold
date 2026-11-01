---
id: INT-4
title: Refactor the server around a content store
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Refactor the server around a content store

## Problem
The server reads and writes files in a local folder and commits with git, and that assumption runs through every module. A single operation makes several separate commits. The sidebar, the home page and the log are written by hand on every operation, so they can drift from the pages they describe. The module name `wiki_backend` was kept during the move only to keep the diff readable. Putting the instance anywhere other than a local checkout (such as straight on GitHub) means changing every module.

## Proposed outcome
All access to an instance goes through one interface, a content store, with a local-git implementation that behaves exactly as today. One operation is one commit. The sidebar, home page and log are derived, not hand-written in many places. The module has a name that fits the product. A second store can be added without touching the tools.

## Affected users and systems
- **Maintainers** of the server and anyone writing another store.
- **Every caller of the tools,** who must see no change in behavior.
- **Existing instances,** whose files and history must keep working.

## Constraints
- **No change in what callers see.** The contract tests (INT-2) pass unchanged before and after.
- **Existing instances keep working** with no migration step for the user.
- **Stages, not one big change.** Rename, then the interface, then one commit per operation, then derived pages; each stage lands separately and passes the tests.
- **No new runtime dependency.**
- **Etag-checked writes stay** and keep their meaning.

## Scenario seeds

### S1 — Behavior is unchanged
**Who:** A client author.
**Wants:** Their client to keep working through the refactor.
**So that:** They do not have to follow internal changes.
**We will know when:** The contract tests recorded before the refactor pass after each stage without being edited.
**Must never:** Change a tool name, argument, result or error code as a side effect.

### S2 — One operation, one commit
**Who:** A reviewer reading the instance's history.
**Wants:** One commit for one handoff step.
**So that:** The history reads as the story of the work and a step can be undone as a unit.
**We will know when:** Creating a handoff produces a single commit holding the page, the sidebar entry and the log line.
**Must never:** Leave an operation half-committed if it fails.

### S3 — A different store can be plugged in
**Who:** A developer adding another store.
**Wants:** To implement the interface and run the existing tests against it.
**So that:** A new store is proven by the same tests.
**We will know when:** A simple in-memory store passes the same store tests as the git store.
**Must never:** Require a change in a tool to support a store.

## Out of scope
- The GitHub store itself (INT-14).
- New tools or changed tool behavior.
- Changing the instance's file layout.

## Open questions
- What should the module be called? (the product owner)
- Should the derived pages be generated on write, or on read? (the product owner)
- How strict should the interface be about concurrent writers in the first version? (the product owner)
