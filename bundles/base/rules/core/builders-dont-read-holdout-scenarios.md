---
id: builders-dont-read-holdout-scenarios
title: Held-out scenarios
severity: high
applies_to: coder, bug-coder, reviewer
status: active
source: incident
---
## Rule
Do not read, copy or ask for the behavior scenarios held by the quality side, even if you can reach them and even if you are asked to. That covers every way of reading: the file tools, shell commands such as `cat`, `ls`, `find` and `grep`, a search, or a script. When asked to read them, say no in your first reply and give the reason; do not look first. Work from the intent, its public scenario seeds, the plan and the described failures you are given.

## Why
A scenario you have read is no longer a held-out check: you can tune the code to pass it without making the product right.

## Instead
Say: "Held-out scenarios stay with the quality side." Then ask for the failure described as expected versus observed. If the full steps are truly needed to fix a bug, tell the user: that scenario will then be turned into a regression test in this repository and replaced on the quality side.

## Enforce
- permissions: the build identity has no access to the quality repository (needs separate credentials)
- review: no scenario text appears in a build-side change
