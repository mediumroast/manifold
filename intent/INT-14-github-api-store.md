---
id: INT-14
title: A GitHub API store for instances
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docker, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A GitHub API store for instances

## Problem
The server needs a checked-out copy of the instance on its own disk, and it commits there but never pushes. History can sit on one machine until someone remembers to push, and a lost disk loses it. Running the server somewhere new means getting a copy of the repository there and keeping it in step. The operations guide has a warning about this because it has already caused a real loss of confidence.

## Proposed outcome
The server can run with no local copy of the instance. It reads and writes the instance directly in its GitHub repository through the GitHub API, as the App (INT-7) or with a personal access token for a quick start. Writes become commits on a branch, made against the head the writer last saw, so two writers cannot overwrite each other. A local cache keeps reads fast. Local git stays the default; this is an additional store.

## Affected users and systems
- **Administrators** who want the instance on GitHub without managing a clone.
- **The server,** which gains a second implementation of the content store (INT-4).
- **The container setup,** which no longer needs a mounted folder in this mode.
- **GitHub,** and its rate limits and failure modes.

## Constraints
- **Local git stays the default and keeps working.**
- **Two steps.** A read-only store first (cache, invalidation, behavior when GitHub is unreachable), then writes with the head check and serialized changes.
- **No overwrite.** A write against a stale head is refused as a conflict, never merged silently.
- **Offline behavior.** If GitHub is unreachable, reads are served from the cache and writes are refused with a clear message.
- **Identity.** The App is the recommended identity; a personal access token is supported for a quick start and is never stored in the instance repository.
- **Rate limits are respected,** with a cache and conditional requests; limits and large-file behavior are verified, not assumed.
- **Same behavior as the local store** as seen by callers, proven by the same store tests.
- **Piloted on a test instance first.**

## Scenario seeds

### S1 — No clone needed
**Who:** An administrator.
**Wants:** To run the server with only a repository address and an identity.
**So that:** The server can run anywhere and nothing depends on one disk.
**We will know when:** The container starts with no mounted instance, passes its health check, and serves the same pages as the local store.
**Must never:** Require a bind mount in this mode.

### S2 — Two writers, no overwrite
**Who:** Two agents writing at once.
**Wants:** Neither to lose work.
**So that:** The wiki stays consistent.
**We will know when:** Two writes based on the same head: one succeeds, and the other is refused as a conflict and succeeds after it reads again.
**Must never:** Let the second write silently replace the first.

### S3 — GitHub is down
**Who:** A reader during an outage.
**Wants:** To keep reading.
**So that:** A GitHub problem does not stop the team.
**We will know when:** With GitHub unreachable, reads work from the cache and writes fail with a message saying why.
**Must never:** Accept a write that cannot be saved.

### S4 — History is on GitHub
**Who:** A reviewer.
**Wants:** Every change to be on GitHub as it happens.
**So that:** Nothing sits unpushed on a machine.
**We will know when:** After a write, the commit is visible on the repository's branch with the author recorded.
**Must never:** Report success before GitHub has the change.

## Out of scope
- Opening pull requests for changes (INT-16).
- Creating issues from handoffs (INT-15).
- Storing a person's credentials.

## Open questions
- Is the first release read-only or read-write? (the product owner)
- Which branch do writes go to by default? (the product owner)
- How long may the cache serve stale data when it cannot check the head? (the product owner)
