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
The coordinator writes the evidence below and leaves the slug on the last line for a human.

**Commit (full hash):** <!-- the commit that was pushed, the head of the branch -->

1. Ran: <!-- how the runs were read, for exactly this commit -->
   1. <workflow name>, run <run id>, <status>, <conclusion>, <link> <!-- one numbered sub-line per run; or "no run found" -->

**Instructions:**
1. Open each link in the numbered runs above and check that the run finished successfully.
2. If every run is `completed` with the conclusion `success`, write your name and the date on the **Confirmed by** line below, replacing the whole slug, and then tick the box "CI of commit <full hash> is green" under "What remains for you". Both acts are yours: the line and the tick.
3. If a run failed, is not `completed`, or is missing, do not write your name and do not tick. Tell the coordinator.

**Confirmed by:** <Insert Name of confirmer on Date of confirmation, ex. M. Kusanagi on Jan-01-2027>

## Rule exceptions
<!-- Each agent's "Rule exceptions" line, set against the diff, the commit log and .manifold/guard-log.jsonl: what matched and what did not. Entries added to the breach record. "none" if there were none. -->

## Could not check
<!-- What was not run or not read, and why. -->

## Follow-ups
<!-- Noticed and not done: each with where it should go (a plan task, an intent, an issue). -->

## What remains for you
<!-- Checkboxes for the human; a tick is a human act. One line per changed file: what to check and what the tick means. Then the CI line and the findings line. Levels of done: "Definition of done" in docs/process/REVIEW_CYCLE.md. -->

**Instructions:**
1. Changed files (one line each): open the pull request's Files changed tab, read that file's diff, and look for what the line says to check. Tick the box only if you read it and accept it. If you do not accept it, leave it unticked and say why in a comment.
2. CI line: follow the **Instructions** under "CI on the pushed commit" (two acts: the line and the tick). There is no second copy here.
3. Findings line: read the "Decisions for you" table below, then write "accept all" or name the exceptions.
4. GitHub's Approve review: a separate act from every tick and row in this description, and nothing written here satisfies it. It is needed when the repository's rules require an approving review (see the `Review process` section of `AGENTS.md` and the branch rules). To give it, open the Files changed tab, click "Review changes", choose Approve and submit (GitHub's steps: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/reviewing-proposed-changes-in-a-pull-request). If the control is missing or disabled for you, do not write a name or tick a box here instead; ask the owner how approval is met in this repository.

- [ ] `<path>`: <what to check; ticking means you read the diff and accept it>
- [ ] CI of commit <full hash> is green (read by the coordinator)
- [ ] Findings: decisions below

## Decisions for you
<!-- One batch. Plain words, no bare IDs (never "F2" or "task 7" alone). Replying "accept all" settles every default; name any exception. Write "none" if nothing is open. -->

| What | Why | Consequence | Default |
|---|---|---|---|
| | | | |

## Ready check
<!-- Four lines, from docs/process/REVIEW_CYCLE.md. While any line is missing the description does not say the pull request is ready. Where each fact is recorded: see "Where each fact is recorded" in docs/process/REVIEW_CYCLE.md; link to it, do not restate it. -->

**Instructions:**
1. The coordinator replaces each State cell with exactly `met` or `missing`. A cell left as `missing` is the safe value.
2. `met` needs evidence in the Evidence cell. A line with no evidence stays `missing`.
3. A human does not edit State cells. If one looks wrong, tell the coordinator.

| Line | State | Evidence |
|---|---|---|
| A review of the final commit exists | missing | |
| Each finding has a decision recorded in the pull request | missing | |
| CI of that exact commit was read and a human ticked it | missing | |
| Approval follows the `Review process` section of `AGENTS.md` | missing | |

**Instructions:**
1. Read this description, the review file it names and the changed files.
2. When every line above is `met` and you are satisfied, write your name and the date on the next line, replacing the whole slug. Only the person who decides writes it; only a human moves a pull request out of draft or merges, and the coordinator leaves the slug as it is.
3. If a line above is `missing`, do not write your name. Ask the coordinator what is missing.

**Human confirmation:** <Insert Name of decider on Date of decision, ex. M. Kusanagi on Jan-01-2027>
