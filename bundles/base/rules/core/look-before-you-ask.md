---
id: look-before-you-ask
title: Look before you ask
severity: medium
applies_to: all
status: active
source: incident
---
## Rule
Before you ask the user about a file, folder, command or setting, look for the answer in the repository: list the folder, read the manifest, `AGENTS.md`, the README and the task runner. Never guess a file name. Ask only what the repository cannot tell you.

## Why
Questions the repository answers cost the user a turn and make the agent look as if it had not read anything. In a live run an agent guessed two test file names that did not exist and asked which was right, when listing the folder would have shown the file.

## Instead
Look first. If you ask, say what you looked at and what is still unknown.

## Enforce
- review: none (judgment call)
