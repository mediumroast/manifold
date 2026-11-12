---
description: List what is still open in a phase (read-only). Usage /phase-status <phase number>
argument-hint: <phase number>
allowed-tools: Bash(python3 *)
---
Phase status, read from the plan, test plan and review files by a read-only script:

!`python3 .manifold/phase_status.py $ARGUMENTS`

Show the output above to the user exactly as printed. Do not edit, reorder or summarise it, and do not change any file. If it printed an error, show the error and stop.
