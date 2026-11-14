---
name: phase-status
description: List what is still open in a phase (read-only). Usage /phase-status <phase number> [--pr-body <file>]
argument-hint: <phase number> [--pr-body <file>]
---
Run this command in the terminal and paste its output unedited:

`python3 .manifold/phase_status.py ${input:phase}`

The script only reads the plan, test plan and review files, and the pull request description when `--pr-body <file>` is given, and writes nothing. It does not read intent files (an unreplaced `accepted_by` slug in an intent is found only by reading the intent). Do not edit, reorder or summarise its output, and do not change any file. If it printed an error, show the error and stop.

Limit: this prompt asks you to run the script, so the run is your act and not a read the client performs by itself. Prompt files run only in the Local harness of GitHub Copilot in VS Code, which is deprecated and planned for removal in February 2027. The VS Code documentation of prompt files describes no way for a prompt file to run a command itself. Whether `${input:phase}` can carry `4 --pr-body <file>` (a phase number and the option in one input) is unverified: confirm with the VS Code prompt-file documentation (https://code.visualstudio.com/docs/copilot/customization/prompt-files). That page shows the `${input:variableName}` syntax under "Reference files" and says only that most language models understand it and will prompt for these inputs; it does not say whether one input can hold several words. If it does not, run the script by hand with `--pr-body`.
