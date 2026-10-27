---
id: quality-side-is-black-box
title: Black-box scenarios
severity: high
applies_to: test-planner, test-coder, scenario-writer
status: active
source: convention
---
## Rule
When you write or automate behavior scenarios (scenario mode, or as the scenario-writer), work only from the intent, its scenario seeds, the product's public documentation and its observable behavior. Do not read the product's source code, plans or tests.

## Why
Scenarios derived from the implementation test what the code does, not what the user wanted, and they inherit its mistakes.

## Instead
Ask the human, read the public documentation, or observe the running system. In local-check mode in a product repository you may read the code; this rule is about behavior scenarios.

## Enforce
- review: scenarios and automation mention no internal names, fields or functions
