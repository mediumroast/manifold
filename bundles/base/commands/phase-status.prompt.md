---
name: phase-status
description: List what is still open in a phase (read-only). Usage /phase-status <phase number>
argument-hint: <phase number> [--pr-body <file>]
---
Run this command in the terminal and paste its output unedited:

`python3 .manifold/phase_status.py ${input:phase}`

The script only reads the plan, test plan and review files and writes nothing. Do not edit, reorder or summarise its output, and do not change any file. If it printed an error, show the error and stop.

Limit: this prompt asks you to run the script, so the run is your act and not a read the client performs by itself. Prompt files run only in the Local harness of GitHub Copilot in VS Code, which is deprecated and planned for removal in February 2027. The VS Code documentation of prompt files describes no way for a prompt file to run a command itself.
