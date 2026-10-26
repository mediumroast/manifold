---
id: human-confirms-closure
title: Closing bugs
severity: high
applies_to: bug-coder
status: active
source: convention
---
## Rule
Do not mark a bug fixed on your own word. Describe the fix, ask the person who reported it to confirm the behavior, and close it only after they do.

## Why
Passing tests show the code does what the tests say, not that the reported behavior is gone. Bugs closed on assertion come back as repeat reports.

## Instead
If the person cannot check right away, mark the bug `[~] Pending human confirmation` and move on to the next one.

## Enforce
- review: every closed bug in the triage list has a recorded confirmation
