---
id: INT-17
title: First real run and end-to-end trial
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docker, docs, ci]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: First real run and end-to-end trial

## Problem
The server was moved to its public home and its container image is built by CI, but no person has followed the documentation on a clean machine, and the whole product has never been used the way a company would use it: an instance on GitHub, no local copy, individual credentials, an App, and agents connected. Parts that look right on their own can fail when joined. The write path is also about to change, so a check done earlier would test something that is being replaced.

## Proposed outcome
After the identity, installer, App and GitHub store exist, two runs prove the product. First, a fresh clone and the quickstart alone, on a clean machine. Second, the whole product against a real repository in a test organization: the installer creates a private repository, the server runs with no mounted folder, clients connect, components are registered, handoffs are created and closed, and every change shows up on GitHub under the App's identity. The runs include deliberate failures. What goes wrong is fixed or recorded. A note in the old private copy of the server says that edits now go to the public repository.

## Affected users and systems
- **The maintainers,** who decide whether the product is ready to be used for real.
- **The company that will use it first,** which is waiting on this evidence.
- **Everything built in the intents it depends on.**
- **The test organization,** which holds the trial repository.

## Constraints
- **Fictional data only.** The trial uses the example instance. Nothing from a company's wiki is used.
- **Public documents do not name the test organization.** They call it "a test organization".
- **Follows the documentation as written.** Every place where a step does not work as written becomes an issue, not a verbal workaround.
- **Failures are part of the test:** GitHub unreachable, a stale head, two writers at once, a revoked installation, a wrong credential.
- **Recorded results.** The outcome is saved in the repository's test results with the date and versions.
- **The gate for cutover.** Moving an existing wiki onto the public server does not start until this has passed and the owner says so.

## Scenario seeds

### S1 — The quickstart works on a clean machine
**Who:** Someone who has never seen the project.
**Wants:** To follow only the quickstart.
**So that:** The documentation is proven.
**We will know when:** Every step works as written on a clean machine, and each mismatch found is recorded as an issue.
**Must never:** Count the run as passed with an unrecorded workaround.

### S2 — The whole product on GitHub
**Who:** The maintainers.
**Wants:** The full flow against a real private repository.
**So that:** Joined parts are proven together.
**We will know when:** The installer creates the repository, the server runs with no mounted folder, agents create and close handoffs, and each change is a commit on GitHub made by the App.
**Must never:** Use a real company's data or a personal token as the final configuration.

### S3 — Failures behave
**Who:** The maintainers.
**Wants:** Known failures to be safe.
**So that:** An outage is not data loss.
**We will know when:** With GitHub blocked reads still work and writes are refused; with a stale head the second writer is refused; with an uninstalled App access stops cleanly.
**Must never:** Show a successful write that was not saved.

### S4 — The old copy is frozen
**Who:** A maintainer of the private copy.
**Wants:** A clear sign that development moved.
**So that:** Changes are not made in the wrong place.
**We will know when:** A note at the top of the old copy says edits now go to the public repository.
**Must never:** Delete the old copy before a cutover has held.

## Out of scope
- Moving any existing company's wiki onto the public server (a separate, gated step).
- Load or performance testing.
- Automated end-to-end tests in CI (this is a manual, recorded trial; automation is a later intent).

## Open questions
- Which machine and operating systems count as "a clean machine" for the first run? (the product owner)
- Who performs the first run: a maintainer, or someone who has not seen the project? (the product owner)
- Where are the results recorded, and in what form? (the product owner)
