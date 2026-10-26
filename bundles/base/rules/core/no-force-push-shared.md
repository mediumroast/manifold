---
id: no-force-push-shared
title: Shared history
severity: high
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Do not force-push, run `git reset --hard`, rebase published commits, or delete branches you did not create, on shared branches (the default branch, release branches) or anywhere else, without the user's explicit instruction. Before any command that can discard work, run `git status` and keep uncommitted changes safe.

## Why
Rewriting shared history destroys other people's work and is hard or impossible to undo.

## Instead
Add a new commit that reverts or fixes the problem. Ask before any destructive git operation.

## Enforce
- server: protect the default branch against force-pushes and deletions
