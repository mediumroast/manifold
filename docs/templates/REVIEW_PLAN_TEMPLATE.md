# REVIEW_PLAN_<N>.md
<!--
  Template for the reviewer agent.
  Copy this file to docs/plans/REVIEW_PLAN_<N>.md (the same <N> as the plan), fill it in, and delete
  these comments. It is the only file the reviewer writes. A re-review updates this same file in place:
  raise the Revision number, add a row to the revision log, and change the State of each earlier
  finding with its evidence; new findings get the next ids. Never delete an earlier finding.
  The reviewer does not approve or block a change and never fills in an approval line.
  Keep it short: link to files and lines instead of copying them.
-->

**Phase:** <!-- PHASE_<N>_PLAN.md and the checkpoint reviewed, or "whole plan" -->
**Intent:** <!-- INT-<n> and its path, or "none" -->
**Commit reviewed:** <!-- full commit hash and branch -->
**Plan version:** <!-- the plan's last commit hash, or its Approved by line and any Amendment approved by line -->
**Policy used:** <!-- `REVIEW.md`, or "built-in defaults"; and whether the Review process approval rule applies / does not apply to this change -->
**Revision:** <!-- number (1 for the first review) and the timestamp, YYYY-MM-DD HH:MM -->

## Revision log

| Revision | Timestamp | Commit reviewed | What this revision did |
|---|---|---|---|
| 1 | | | First review |

## Counts by severity

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | | | | |
| Nit | | | | |

## Findings

Order by pass, then by severity. One block per finding, ids never reused (`F1`, `F2`, ...).

### Bugs
### Security
### Compliance
### Tests
### Context files

<!-- Each finding, under its pass:

**F1 (Important | Nit) — one-line title**
- **Location:** `path:line`, or the plan line it contradicts
- **Evidence:** how you know (the command and its output, or the lines compared)
- **Direction:** what to change, as a direction and not a patch
- **State:** `open`, `repaired`, `deferred` or `rejected`; the reason, and the evidence for it (the repair task and the command that shows it). A finding ends `repaired`, `deferred` or `rejected`; it is never closed without evidence.
-->

## Rule exceptions compared

The agent's "Rule exceptions" line against the diff, the commit log and `.manifold/guard-log.jsonl`: what matched, what did not, or "not compared" and why.

## Gates run

| Command | Counts | Result |
|---|---|---|
| | | |

A gate you did not run is written "not run" with the reason.

## CI on the pushed commit

The workflow runs and their results for the commit reviewed, or "not checked" and why.

## Tests run and changed

The failing-first evidence for each bug fix (command, failing result, passing result), and every existing test that was changed, with the recorded approval for the change. "None changed" if none.

## Could not check

What you could not check and why.

## A human decides

This review does not approve or block the change. A human approves, informed by the findings above.
