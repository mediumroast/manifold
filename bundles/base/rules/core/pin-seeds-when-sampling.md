---
id: pin-seeds-when-sampling
title: Reproducible checks
severity: medium
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
When a check samples data or uses randomness, fix the seed and sample size and record both next to the result.

## Why
A run that cannot be repeated cannot be compared: a pass after a fix may only mean a luckier sample.

## Instead
Use the same seed and sample size for the before and after runs, and write them in the report or the plan note.

## Enforce
- review: reported results include the seed and sample size
