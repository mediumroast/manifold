---
id: rule-exceptions-line
title: Rule exceptions
severity: high
applies_to: all
status: active
source: incident
---
## Rule
Every report from an agent that changed files or ran commands has a "Rule exceptions" line: `none`, or each exception with the command, the file and the reason. Never fold an exception into notes or interpretations, and never leave the line out because it would be empty.

## Why
A breach that is reported as a side note, or not reported, cannot be counted, and a rule that is never reported as broken looks like a rule that holds. Reviewers and the coordinator compare the line with the diff, the commit log and the guard log.

## Instead
If you are unsure whether something was an exception, list it. The `reviewer` and `coordinator` compare the line with the diff, the commit log and `.manifold/guard-log.jsonl`.

## Enforce
- review: compare the "Rule exceptions" line with the diff, the commit log and .manifold/guard-log.jsonl
