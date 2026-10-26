---
id: diagnose-before-fix
title: Diagnosis first
severity: high
applies_to: bug-coder
status: active
source: convention
---
## Rule
Do not change code for a bug whose root cause you have not confirmed with evidence. If you cannot reproduce or explain it, say so and ask for the missing input (trace, input, logs, environment).

## Why
Guess-fixes mask the symptom, ship regressions and leave the real defect in place.

## Instead
State the diagnosis and the evidence for it. Fix only after it is confirmed, or after the user says to go ahead.

## Enforce
- review: the bug notes record the diagnosis and its evidence before the fix
