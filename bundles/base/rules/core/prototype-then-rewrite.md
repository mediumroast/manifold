---
id: prototype-then-rewrite
title: Prototypes
severity: medium
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Prototype new work in a scratch area (for example `experiments/<name>/`) and never copy the prototype into production code. Rewrite it to fit the project's established patterns, and start each experiment from a clean state.

## Why
Experimental code carries shortcuts, dead branches and assumptions that nobody reviewed. Copied into production, they become permanent.

## Instead
Validate the idea in the scratch area, have the user accept the result, then implement it in the production modules following their existing structure. Do not import production modules from an experiment, and do not import experiments from production.

## Enforce
- review: production diffs contain no files or paths from the scratch area
