---
id: no-workaround-after-refusal
title: A refusal is final
severity: high
applies_to: all
status: active
source: incident
---
## Rule
When the user or the client refuses a read, a command or a tool, or a tool is not available, do not get the same result another way: not with a different tool, a shell command, a script or another path. Stop, say what you could not do and why it matters, and ask.

## Why
A refusal is a decision. In live runs, agents whose read of a protected folder was refused tried the same read again through a shell `find`, `ls` and `cat`. A boundary the agent routes around is not a boundary.

## Instead
Report the blocked step in one line, say what you need, and continue with the parts of the task that do not depend on it.

## Enforce
- review: no command in the session transcript repeats a refused action by another route
