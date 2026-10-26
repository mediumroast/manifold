---
id: scope-stage-only-changed-files
title: Staging
severity: high
applies_to: coder, bug-coder, test-coder
status: active
source: incident
---
## Rule
Stage explicit paths only. Never run `git add -A`, `git add .` or `git commit -a` without first listing exactly what would be included. Before committing, read `git status --short` and `git diff --cached --stat`; if anything unexpected is staged, unstage it.

## Why
Broad staging sweeps in generated files, local configuration and other people's work. One such commit can bury a small change under hundreds of unrelated files.

## Instead
`git add <path> <path>`, then check `git diff --cached --stat`, and commit only what the task touched.

## Enforce
- hook: a pre-commit check that rejects commits touching paths outside the declared change set (optional, per project)
