---
id: no-generated-artifacts-in-commits
title: Generated output
severity: high
applies_to: coder, bug-coder
status: active
source: incident
---
## Rule
Do not commit generated output: test reports, traces, screenshots, videos, build output, caches, coverage data. Check `.gitignore` first. If generated paths show up as untracked and are not ignored, tell the user instead of committing them.

## Why
Test and build tools can emit hundreds of files in one run. Committing them bloats history and hides the real change.

## Instead
Stage only source changes. If the output directory should be ignored, say so and offer to add it to `.gitignore`.

## Enforce
- ci: fail when a pull request adds files under known output directories (optional, per project)
