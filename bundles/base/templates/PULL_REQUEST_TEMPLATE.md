# <Title: what changed, in a few words>
<!--
  Template for the description of a pull request produced by a review cycle.
  The coordinator fills it in from evidence; a person can fill it in the same way. GitHub does not
  pre-fill this file (it pre-fills only .github/pull_request_template.md), so the author copies it.
  Delete these comments from the finished description. Keep it short: link to files, commits and
  runs instead of copying them. Write "none" when a section has nothing; do not leave one blank, and do
  not fill a section with text the evidence does not support.
  The pull request stays in draft until a human moves it out of draft. Neither the coordinator nor any
  other agent does, and none of them merges.
-->

## What and why
<!-- Two or three sentences: the change and the reason for it. -->

## Plan and intent
**Plan:** <!-- docs/plans/PHASE_<N>_PLAN.md and its Approved by line (name and date), and any Amendment approved by line -->
**Intent:** <!-- INT-<n> and its path, or "none" -->

## Checkpoints done
<!-- One line per checkpoint: its name, done or not done, and the commit that finished it. -->

## Review state and findings
**Review:** <!-- `docs/plans/REVIEW_PLAN_<N>.md`, the revision number, or "no review yet" -->
**Commit reviewed:** <!-- full commit hash named by that revision -->

| Severity | Open | Repaired | Deferred | Rejected |
|---|---|---|---|---|
| Important | | | | |
| Nit | | | | |

<!-- One line for each finding that is deferred or rejected: its id and the reason. -->

## Gates
<!-- The project's gates (the commands under "Project commands" in AGENTS.md), run on the commit above. Real counts, not "passed". A gate that was not run is "not run" with the reason. -->

| Command | Counts | Result |
|---|---|---|
| | | |

## CI on the pushed commit
**Commit (full hash):** <!-- the commit that was pushed, the head of the branch -->
**Run:** <!-- each workflow run for exactly that commit: name, status, conclusion and link; or "no run found" -->
**Confirmed by:** <!-- a human: name and date. Only a person writes this. "not yet confirmed" until then -->

## Rule exceptions
<!-- Each agent's "Rule exceptions" line, set against the diff, the commit log and .manifold/guard-log.jsonl: what matched and what did not. Entries added to the breach record. "none" if there were none. -->

## Could not check
<!-- What was not run or not read, and why. -->

## Follow-ups
<!-- Noticed and not done: each with where it should go (a plan task, an intent, an issue). -->

## Ready check
<!-- Four lines, from docs/process/REVIEW_CYCLE.md. Mark each "met" or "missing" with its evidence. While any line is missing the description does not say the pull request is ready. -->

| Line | State (met / missing) | Evidence |
|---|---|---|
| A review of the final commit exists | | |
| Each finding is repaired, deferred or rejected | | |
| CI of that exact commit was read and a human confirmed it | | |
| Approval follows the `Review process` section of `AGENTS.md` | | |

**Human confirmation:** <!-- Name and date, written by the person who decides; only a human moves a pull request out of draft, and the coordinator leaves this blank. -->
