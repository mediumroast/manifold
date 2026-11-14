---
description: List what is still open in a phase (read-only). Usage /phase-status <phase number> [--pr-body <file>]
argument-hint: <phase number> [--pr-body <file>]
allowed-tools: Bash(python3 *)
---
Phase status, read by a read-only script from the plan, test plan and review files, and from the pull request description when `--pr-body <file>` is given. It does not read intent files (an unreplaced `accepted_by` slug in an intent is found only by reading the intent):

!`python3 .manifold/phase_status.py $ARGUMENTS`

Show the output above to the user exactly as printed. Do not edit, reorder or summarise it, and do not change any file. If it printed an error, show the error and stop.
