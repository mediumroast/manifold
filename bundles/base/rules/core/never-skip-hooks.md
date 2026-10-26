---
id: never-skip-hooks
title: Commit hooks
severity: high
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Do not bypass commit or push hooks or commit signing (`--no-verify`, `--no-gpg-sign`, disabling hooks) unless the user asks you to. If a hook fails, the commit did not happen: fix the cause and create a new commit rather than amending the previous one.

## Why
Hooks encode the project's own safety checks. Amending after a failed hook rewrites the wrong commit.

## Instead
Read the failure, fix the underlying problem, re-stage the specific files, and commit again.

## Enforce
- server: branch protection and required status checks on the default branch
