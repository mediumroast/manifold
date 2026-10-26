---
id: dont-assume-gnu-tools
title: Portable commands
severity: low
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
Do not assume GNU tools or flags exist (for example `timeout`, `sed -i` without a backup suffix, `grep -P`, `readlink -f`). Check that the command exists, or use a portable form.

## Why
The same project is run on macOS, Linux and CI. A command that exists on one fails with a confusing error on another.

## Instead
Check with `command -v`, use the project's own scripts, or install the tool through the project's documented route (for example coreutils on macOS) and say so.

## Enforce
- review: commands in scripts run on both macOS and Linux
