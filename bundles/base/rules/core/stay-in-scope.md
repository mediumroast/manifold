---
id: stay-in-scope
title: Scope
severity: medium
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
Do not refactor, reformat or "fix" code outside the task. If you notice something worth changing, record it as a follow-up.

## Why
Unrelated edits enlarge the diff, hide the change under review and risk regressions.

## Instead
Note it under follow-ups in your summary, or suggest it as a new plan task.

## Enforce
- review: diffs are checked against the plan's file inventory
