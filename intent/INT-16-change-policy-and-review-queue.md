---
id: INT-16
title: Change policy, pull-request lifecycle and review queue
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, ui, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Change policy, pull-request lifecycle and review queue

## Problem
Every change to the wiki is committed straight away. That suits low-risk changes such as a log line, but it is wrong for changes that people want to look at first: a new component, a rewritten page, a model's proposal. When the instance lives on GitHub, there is already a good way to review a change, the pull request, but the server has no notion of using it. There is also no single place where a person can see what is waiting for them.

## Proposed outcome
Each kind of change has a policy chosen by the instance's owner: commit directly, open a pull request that merges by itself when checks pass, or open a pull request that waits for a person. The server follows the policy, names branches and records lineage so a change can be traced from intent to handoff to pull request. The interface shows a review queue of what is waiting.

## Affected users and systems
- **Instance owners,** who choose policies.
- **Reviewers,** who work from a queue.
- **The server,** the GitHub store (INT-14) and the App (INT-7).
- **GitHub,** with its branch rules and required checks.

## Constraints
- **Defaults are conservative:** direct commit for the operations that are safe today, a waiting pull request for anything a model proposed.
- **Respect GitHub's rules.** Required reviews and required checks on the instance repository are honored, not bypassed.
- **A person approves what needs a person.** The server never approves its own pull request.
- **Traceable.** Branch names and commit trailers link a change to its intent and handoff.
- **Needs the GitHub store;** local-only instances keep direct commits.
- **No silent merge conflicts:** conflicts surface to a person.

## Scenario seeds

### S1 — A change waits for review
**Who:** An instance owner.
**Wants:** Model proposals to wait for a person.
**So that:** Nothing automated changes the wiki unseen.
**We will know when:** With the policy set, an accepted proposal appears as an open pull request and the main branch is unchanged until a person merges it.
**Must never:** Merge a pull request that is configured to wait.

### S2 — Safe changes go straight in
**Who:** An agent appending a log entry.
**Wants:** No friction for routine changes.
**So that:** Work is not slowed.
**We will know when:** With the direct policy for logs, a log entry is committed at once with no pull request.
**Must never:** Open a pull request for each log line.

### S3 — See what is waiting
**Who:** A reviewer.
**Wants:** One list of what needs them.
**So that:** Nothing sits unnoticed.
**We will know when:** The queue lists pending pull requests with who proposed them, what changed and the linked intent or handoff.
**Must never:** Show items the viewer is not allowed to see.

### S4 — Required checks are respected
**Who:** A repository administrator.
**Wants:** The server to obey the repository's required checks.
**So that:** Protection rules mean something.
**We will know when:** A pull request whose required check fails is not merged, and the queue shows why.
**Must never:** Use an admin bypass to merge on the App's behalf.

## Out of scope
- Reviewing code in component repositories.
- Changing GitHub's own protection settings.
- Systems other than GitHub.

## Open questions
- Which operations are direct by default, and which wait? (the product owner)
- How does the policy get configured: in the instance settings, or per request? (the product owner)
- Does a merged pull request tag a snapshot of the wiki? (the product owner)
