---
id: INT-1
title: Machine-readable install plan
author: Live Protocol
created: 2026-10-27
status: accepted
affects: [bundles/base]
drafted_with: []
accepted_by: Live Protocol 2026-10-27
---

# Intent: Machine-readable install plan

## Problem
The installer prints its dry-run plan as text for people. A script that wants to know what would change has to parse that text, which breaks whenever the wording changes.

## Proposed outcome
A flag makes the installer print the same plan as JSON: each file, its action (create, update, skip, conflict) and the reason.

## Affected users and systems
People who automate installs; `bundles/base/install.py`.

## Constraints
- The default output must stay exactly as it is today.
- Standard library only; Python 3.8 compatible.
- The JSON output must be stable enough to document.

## Scenario seeds

### S1 — Scripts can read the plan
**Who:** someone automating installs
**Wants:** the plan as JSON
**So that:** a script can decide whether to apply it
**We will know when:** the output parses as JSON and lists every file with an action and a reason
**Must never:** write any file when only the plan is requested

## Out of scope
- JSON for `--status` or `--uninstall`.

## Open questions
- Should the JSON include the profile and the bundle version?
