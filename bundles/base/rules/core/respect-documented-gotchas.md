---
id: respect-documented-gotchas
title: Deliberate workarounds
severity: high
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Do not remove or "fix" a guard, workaround, odd setting or version pin that a comment or document says is deliberate until you have read why it is there.

## Why
These exist because the obvious approach broke. Removing them re-opens a failure someone already paid for.

## Instead
Read the comment and the history of the line. If you still think it is wrong, explain why and ask the user before changing it.

## Enforce
- review: diffs that delete a commented guard cite the reason
