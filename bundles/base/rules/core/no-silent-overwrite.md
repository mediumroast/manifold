---
id: no-silent-overwrite
title: User edits
severity: high
applies_to: all
status: active
source: convention
---
## Rule
Do not overwrite or delete a file the user may have modified without showing the difference and getting confirmation. Prefer archiving to deleting.

## Why
Silent replacement loses local customizations that cannot be recovered.

## Instead
Show the diff, ask, and move the old version aside (for example to an archive or `.bak` path) before replacing it.

## Enforce
- tooling: installers and generators compare content hashes and refuse to overwrite modified files
