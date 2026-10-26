---
id: separate-code-and-artifact-commits
title: Commit structure
severity: medium
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Commit code changes separately from refreshed data or generated deliverables, and commit the deliverables only after the check that gates them has passed.

## Why
Mixed commits make review and revert hard, and a deliverable committed before its verification can ship wrong data.

## Instead
Make one commit for the code and a second for the artifacts, each with a message that says which check passed. If no code changed, a single artifact commit is fine.

## Enforce
- review: no commit mixes source files with refreshed data artifacts
