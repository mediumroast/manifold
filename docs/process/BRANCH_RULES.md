# Branch and merge rules

This file records the rules that GitHub enforces on `main`, read from the repository's settings. It is not shipped with the bundle. The ruleset itself is the owner's to change; nothing here changes it. The `coordinator` compares the required check names below with the job names in `.github/workflows/` and reports a mismatch.

## How this was read

Read on 2026-11-12, read only (GET requests), with the GitHub CLI `gh` 2.86.0, signed in already (`gh auth status`):

- `gh api --method GET repos/{owner}/{repo}/rulesets` lists the rulesets. Source for the command form: `gh api --help` (the default method is GET unless parameters are added; `--method GET` was given explicitly).
- `gh api --method GET repos/{owner}/{repo}/rulesets/26275761` reads the ruleset `protect-main`.
- `gh api --method GET repos/{owner}/{repo}/rules/branches/main` reads the rules that apply to `main`; it returned the same five rules as the ruleset.
- The three endpoints are the ones named on the GitHub REST page "Rules" (https://docs.github.com/en/rest/repos/rules, read 2026-11-12).

Two rulesets exist: `protect-main` (target branch, enforcement `active`) and `protect-release-tags` (target tag, `active`). Only `protect-main` was read in detail; the tag ruleset is listed here and its rules are unverified: confirm with `gh api --method GET repos/{owner}/{repo}/rulesets/26285742`.

Re-read the ruleset before relying on this file: it records one moment. `protect-main` was last updated 2026-11-11T05:57:53.911-08:00.

## Rules on `main` (ruleset `protect-main`, applies to the default branch)

Each row came from the `rulesets/26275761` read above.

| Rule | Value read |
| ---- | ---------- |
| Required status checks | `test (3.10)` and `test (3.12)` (both from GitHub Actions, `integration_id` 15368) |
| Branch must be up to date before merging | yes (`strict_required_status_checks_policy: true`) |
| Merge method | squash only (`allowed_merge_methods: ["squash"]`) |
| Linear history | required (`required_linear_history`) |
| Approving reviews | 1 required (`required_approving_review_count: 1`) |
| Stale reviews | dismissed on a new push (`dismiss_stale_reviews_on_push: true`) |
| Review conversations | must be resolved (`required_review_thread_resolution: true`) |
| Code owner review | not required; last-push approval not required |
| Extra approval for unattributed changes | required (`require_extra_approval_for_unattributed_changes: true`) |
| Deletion of `main` | blocked (`deletion`) |
| Force push to `main` | blocked (`non_fast_forward`) |
| Bypass | `OrganizationAdmin` and `RepositoryRole` with `actor_id` 5, both with `bypass_mode: pull_request` (they may bypass only through a pull request) |

What "role 5" is: unverified: confirm with the GitHub documentation on repository roles in rulesets, or the ruleset page `https://github.com/mediumroast/manifold/rules/26275761`.

What `require_extra_approval_for_unattributed_changes` means: unverified: confirm with the GitHub REST page "Rules" (https://docs.github.com/en/rest/repos/rules) or the ruleset page.

The review count of 1 and the solo repository (`AGENTS.md`, "Review process") are both facts; how the owner's approval is met under it is not stated by the ruleset and is not recorded here.

### Check names against the workflows

The required names `test (3.10)` and `test (3.12)` match the job `test` of `.github/workflows/ci.yml` with its matrix `python-version: ["3.10", "3.12"]` (name form `<job> (<matrix value>)`; the match is by the read of both files, not by a documented rule). The jobs of `server.yml` (`server tests (...)`, `image`, `vendored web files`) are not required checks. When the matrix of `ci.yml` changes, the required list must change with it, or no pull request can merge.

## Stacked pull requests under squash only

A squash merge writes one new commit on `main` and the base branch's own commits do not become ancestors of it. A pull request stacked on that base branch therefore still carries the old commits and conflicts or repeats them. After the base pull request is squash-merged:

1. Fetch: `git fetch origin`.
2. Move the dependent branch onto `main`, dropping the commits of the base branch: `git rebase --onto origin/main <old-base-tip> <dependent-branch>`, where `<old-base-tip>` is the last commit of the base branch as it was before the squash (the commit the dependent branch was started from). Source for the form: `git rebase --help` (the `--onto <newbase> <upstream> <branch>` form, "rebase part of a branch").
3. Change the dependent pull request's base to `main` on GitHub if it is not changed yet.
4. Push the rewritten branch: `git push --force-with-lease`. This rewrites a branch that only you use; it is not allowed on `main` or any shared branch (`AGENTS.md`, "Shared history"), and it needs the owner's go-ahead like any push.
5. The branch must be up to date with `main` and its checks re-run, because the ruleset requires it (see the table).

Allowing rebase-merge instead would avoid this, but it is a change of the ruleset and the owner's to make; this file only documents the steps.

## Editing agent definitions from another worktree

The guard protects the agent definitions (`.claude/agents/`, `.github/agents/`) from edits made from a different worktree. This is deliberate (see the docstring of `bundles/base/hooks/guard.py`, rule `protected-file`), and the rule is not worked around. The route: delegate the edit to a session whose working directory is the worktree that owns the files (start a session there and give it the change), or make the edit in the bundle source (`bundles/base/agents/`) and refresh the installed copy from the build.

## CI for docs-only changes

Question: can CI be skipped for a change that touches only documents, without a loss of assurance?

What was found:

1. Both workflows that run on pull requests, `.github/workflows/ci.yml` and `.github/workflows/server.yml`, have `on: pull_request` with no `paths` or `paths-ignore` filter (read from the files). A docs-only pull request therefore already runs every check, including the two required ones. Nothing is skipped today.
2. Path filters: `paths` runs a workflow when at least one changed file matches; `paths-ignore` skips it only when every changed file matches an ignore pattern; the two cannot be combined for the same event (GitHub docs, "Workflow syntax for GitHub Actions", `https://docs.github.com/en/actions/writing-workflows/workflow-syntax-for-github-actions`, read 2026-11-12).
3. When path filtering skips a workflow, its checks "will remain in a 'Pending' state", and a pull request that requires them is blocked from merging (same page, same date). Applied here: a path filter on `ci.yml` would leave `test (3.10)` and `test (3.12)` pending on a docs-only pull request, and the ruleset above would block the merge.
4. How a required check behaves when a job (not the workflow) is skipped by an `if:` condition: unverified: confirm with the GitHub documentation page "Troubleshooting required status checks"; its address was not found at the URL tried (HTTP 404), so no statement is made here.
5. In this repository the checks are also the only place the bundle lint and the bundle tests run, and documents under `bundles/base/` are part of the shipped build and are pinned by tests (for example `test_deferred_text_fixes_f1_f4_f5`). A "docs-only" change to those paths is not free of risk; a filter would have to be by path (for example only `docs/plans/`), not by file type.

Recommendation (not done; the owner decides; nothing in `.github/workflows/` was changed):

- Do not add a path filter to `ci.yml`: it provides the required checks, and a skipped required check blocks the merge (item 3).
- If CI time matters, the safer saving is to filter `server.yml` only (it is not required) for changes under `docs/plans/` and `docs/process/`, using `paths-ignore`; this changes no required check. Whether the saving is worth it is not measured here.
- Otherwise leave CI as it is: a docs-only pull request already costs one normal run.
