<!-- SPDX-License-Identifier: Apache-2.0 -->
# Development plan

**Status:** Active. Companion to the [roadmap](../../../ROADMAP.md), which says *what* is planned; this says *how* the work is done.

## 1. Principles

1. **In the open.** Plans, decisions and test results are committed here. Private working notes are not part of the project's record.
2. **Small releases that work.** Each milestone leaves something usable. Formats freeze once, before the server is public; after that, changes are additive.
3. **Humans at the gates.** Agents draft; people accept intents, approve plans and confirm fixes.
4. **Claims need evidence.** A guardrail is not "working" until it has been seen working in a real client, with a named model. Failures are recorded and fixed, not smoothed over.
5. **Rules are advice.** Where a behavior must always hold, a deterministic control (branch protection, required review, separate credentials, a client permission) backs it.

## 2. Where we are

Released bundle contents (v0.1.0): seven agents, a rules library, templates, install profiles, quality settings and an installer, for Claude Code and GitHub Copilot, plus an experimental Agent Skills rendering. It was run end to end in both clients; results are in [`tests/results/`](../../../tests/results/README.md). The run found real gaps (an unapproved plan executed, a test edited to fit a bug, hold-out data read through the shell by smaller models), which were fixed in the bundle and recorded in the findings.

## 3. Order of work

| Step | Work | Done when |
|---|---|---|
| 1 | **Start using the agents on this repository** (section 4) | The first change to this repository goes through intent, plan, review and test plan, and its results are committed |
| 2 | **Re-test the hardened bundle**: the model matrix in [testing-protocol.md](testing-protocol.md) | Results for the hardened agents on Sonnet, Haiku and MAI are in `tests/results/`, and `bundles/base/MODELS.md` is updated from them |
| 3 | **Close protocol and bundle findings** that are still open | The findings list shows each as fixed, deferred with a reason, or not a bug |
| 4 | **Next bundle release**: verifier and researcher roles, an optional hooks pack for Claude Code, evals in CI, organization rule packs | Each is proposed as a plan, approved, built with tests, and run in a live client |
| 5 | **Server and interface**, with the intent editor, authentication and frozen formats | As described in the roadmap and [repository-family-and-stack.md](repository-family-and-stack.md) |

Steps 4 and 5 are intentionally not scheduled. Each starts as an intent and a plan like any other change.

## 4. Using the agents on this repository

The bundle's `build` profile is installed into this repository, so changes to Manifold are made the way Manifold asks users to make them:

1. **Intent.** A person writes `intent/INT-<n>-<slug>.md` from the intent template (the problem, the outcome, constraints, scenario seeds) and sets `status: accepted`.
2. **Plan.** The `planner` writes `docs/plans/PHASE_<N>_PLAN.md`. A person fills in **Approved by**.
3. **Build.** The `coder` executes the plan task by task and ticks each off with the command and its result.
4. **Review.** The `reviewer` reports findings against the plan. A person decides.
5. **Tests.** The `test-planner` and `test-coder` add checks under `bundles/base/tests`. Bug fixes go through the `bug-coder`: a failing test first, then the fix, and the test stays.
6. **Release.** A pull request, a green test run and lint, and a person who merges.

The repository's own rules apply to the agents, with a few additions for this project: American English; no dates in public material; and the installer, the agent text and the rules are changed only together with a test.

**Two things are not yet in place.** The scenario side (a separate quality repository whose scenarios the builders do not read) has no home for this project yet, so verification here is not independent in the sense of [independent-verification.md](independent-verification.md). We say so in the pull request template until it does. And the Claude Code hooks pack does not exist, so the rules above are advice.

## 5. Gates for every change

- The unit and integration tests and `build.py --check` pass.
- Agent and rule changes come with a test, and, when they target a behavior seen in a live run, a note in the findings.
- Public text is checked for dates, internal names and British spellings before it is merged.
- Published artifacts (the release zip) are built from the tagged commit and checked against the manifest.

## 6. Risks

| Risk | Mitigation |
|---|---|
| Smaller models skip rules the bundle depends on | Recommend Sonnet ([`MODELS.md`](../../../bundles/base/MODELS.md)); document the controls to add; re-test after every hardening |
| The project's own agents hide their mistakes | Evidence per task, a reviewer pass, and a person who approves each plan |
| Scope grows before the first server release | Anything not on the roadmap starts as an intent, not as code |
| Single-account verification is not independent | Keep the quality repository on another account or machine where it matters; say plainly when it is not |
