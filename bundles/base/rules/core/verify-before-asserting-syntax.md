---
id: verify-before-asserting-syntax
title: Unverified syntax
severity: high
applies_to: all
status: active
source: incident
---
## Rule
Do not state, document or rely on a command, flag, API, configuration key or file format you have not verified. Check `--help`, the official documentation or the source. If you cannot verify it, say so plainly and mark it unverified.

## Why
Plausible-looking but invented syntax gets copied into docs and scripts, then fails for the next person.

## Instead
Run `<tool> --help`, read the documentation or source, or write "unverified: confirm with <source>".

## Enforce
- review: ask for the source of any new command or flag introduced in documentation
