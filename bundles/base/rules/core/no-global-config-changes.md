---
id: no-global-config-changes
title: User-level settings
severity: high
applies_to: coder, bug-coder, test-coder
status: active
source: incident
---
## Rule
Do not change user-level or global configuration to make a command or a test run: not `git config --global`, shell profiles, global package installs, editor or sandbox settings. If a command fails because of the environment, report the command, the error and the likely cause, and stop there.

## Why
These settings belong to the person, not to the project, and they outlive the session. In a live run an agent tried `git config --global user.email` and `user.name` with made-up values, hiding the failure with `2>/dev/null || true`, to get a test to pass; only the client's sandbox stopped it.

## Instead
Report the blocked step and let the user decide. A setting the project needs belongs in the repository (a local git config, a test fixture, the project manifest) and only when the plan says so.

## Enforce
- review: no `--global`, `--system` or profile edits in the session transcript
