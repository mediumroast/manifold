---
id: builders-dont-write-acceptance-tests
title: Acceptance tests
severity: high
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Do not write the behavior scenarios or end-to-end acceptance tests that judge your own work. You write local checks (unit and integration tests) in this repository; behavior is judged separately on the quality side.

## Why
An AI that builds the code and also writes the tests that judge it can make them agree with each other instead of with what the user wanted.

## Instead
Write local checks beside the code. If behavior needs independent verification, say so; the scenarios come from the intent's scenario seeds and are written in the quality repository by someone else.

## Enforce
- review: no behavior scenarios or end-to-end acceptance suites in a build-side change
