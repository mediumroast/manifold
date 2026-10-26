---
id: derive-tests-from-plan
title: Test scope
severity: medium
applies_to: test-planner, test-coder
status: active
source: convention
---
## Rule
Test cases come from the phase plan's objective, file inventory and acceptance lines. Do not invent acceptance criteria, add cases the test plan does not list, or change a plan's scope.

## Why
Invented criteria turn a test plan into a second, unreviewed specification, and tests that nobody asked for pass or fail for reasons nobody can trace.

## Instead
If an acceptance line is too vague to test, stop and ask. If you think a case is missing, say so and let the human or the test-planner add it.

## Enforce
- review: every case traces to a task and its acceptance line
