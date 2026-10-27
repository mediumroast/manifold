---
id: dont-edit-the-test-to-pass
title: Tests under fix
severity: high
applies_to: coder, bug-coder, reviewer, test-coder
status: active
source: convention
---
## Rule
When fixing a defect, do not edit, skip, weaken or delete an existing test to make a run pass. The test that exposes the bug stays exactly as written until the fix makes it pass.

## Why
A test that can be rewritten to match the code proves nothing. Rewriting it hides the bug, and the next change reintroduces it.

## Instead
Fix the code. If you believe the test itself is wrong, stop, say why, and agree the change with the user before touching it; record the change in the plan or triage row.

## Enforce
- hook: block edits to test files during a fix task (Claude Code, optional)
- review: any diff that changes an existing test in a bug-fix change is flagged
