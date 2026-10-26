---
id: report-results-honestly
title: Reporting results
severity: high
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
Never say tests or checks pass unless you ran them in this session and saw them pass. Report failures together with the relevant output. Do not delete, skip or weaken a test to make a run green unless the user explicitly tells you to.

## Why
A false green hides real breakage until it is expensive to find.

## Instead
State what ran, the exact command and the result. Say "not run" when something was not run, and why.

## Enforce
- ci: the pipeline, not the agent's word, is the final authority on pass or fail
