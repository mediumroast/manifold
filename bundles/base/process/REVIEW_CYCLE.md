# Review cycle

How a change is reviewed and repaired. This file ships in every install (installed at `docs/process/REVIEW_CYCLE.md`, created by a later task) and is read by the `reviewer` and the `coordinator`. It is not `REVIEW.md`: that file is optional and per repository, so the standard below cannot live there.

## Reviewing documents and agent instructions

The change is mostly documents and agent instructions, so a review of it, and of any similar change, means:

(a) traceability: every "we will know when" line maps to a named file and section (table under Completion checklist);
(b) consistency: no two documents, rules, agent definitions or templates contradict each other, including the rendered `AGENTS.md` against the rule sources;
(c) verified claims: every command, flag, path, key or file format a document states was run or read, or is marked "unverified: confirm with <source>", and every link and path resolves;
(d) behavior: a document that prescribes behavior is checked in real use on Manifold work, by agents and reviewers that did not write it, and the evidence is recorded (guard log, breach records, review documents, PR summaries, `tests/results/` records); until that use has happened the scenario is reported as "no evidence yet" (reworded 2026-11-06 because the owner replaced the toy walk-throughs with real use; reconfirmed by the owner on 2026-11-06 with the `tests/results/` records added to the evidence list);
(e) code gets normal tests plus the bundle build and lint;
(f) an independent reviewer, not the author, using the review policy in force;
(g) owner approval of any text that changes agent behavior.

Severity for prose: **Important** if an agent could behave differently or be misled by it; otherwise Nit.

Confirmed by the owner (Michael Hay), 2026-11-03.

Paths named above and not yet present when this section was written: `docs/process/REVIEW_CYCLE.md` (the installed copy of this file, task 29), `docs/plans/REVIEW_PLAN_<N>.md` (the review document, tasks 19 and 21), `AGENTS.md` "Review process" and the optional `REVIEW.md` are written per repository (tasks 16 and 23). Present now: `tests/results/`, `docs/templates/REVIEW_TEMPLATE.md` (installed from the bundle's `templates/REVIEW_TEMPLATE.md`).
