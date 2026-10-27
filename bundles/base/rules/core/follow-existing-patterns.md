---
id: follow-existing-patterns
title: Existing patterns
severity: medium
applies_to: planner, coder, bug-coder, reviewer, test-planner, test-coder, scenario-writer
status: active
source: convention
---
## Rule
Before adding something of a kind the project already has (a module, an endpoint, an extractor, a test), read the closest existing one and any cookbook, onboarding or contributing document, and follow its structure.

## Why
A second way of doing the same thing doubles the maintenance and hides which one is correct.

## Instead
Name the example you followed. If the existing pattern is wrong or does not fit, say so and ask before departing from it.

## Enforce
- review: new code names the existing module it mirrors
