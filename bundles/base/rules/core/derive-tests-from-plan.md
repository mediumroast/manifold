---
id: derive-tests-from-plan
title: Test scope
severity: medium
applies_to: test-planner, test-coder
status: active
source: convention
---
## Rule
Test cases come from the phase plan and from the originating intent (its scenario seeds, "Must never" lines and constraints), and every case cites a source: an intent line, a "Must never", a constraint, a plan acceptance line or "owner-confirmed". Look for what the builders missed (a gap check is a local check that tests what the intent asked for), and do not copy an existing test into the plan as a case. Do not invent acceptance criteria or change a plan's scope.

## Why
A test plan derived from the plan by the agents that built it only confirms what they believed, and tests with no source pass or fail for reasons nobody can trace.

## Instead
If an acceptance line is too vague to test, or an expected result has no source, stop and ask, then write the question in the test plan. A failing check is a defect, not a reason to change the check.

## Enforce
- review: every case cites a source; a plan that cites no intent, ticks every case or asks nothing is sent back
