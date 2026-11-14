# PHASE_4_PLAN.md

**Approved by:**
**Source intent:** INT-27 `intent/INT-27-clear-human-instructions-in-the-pr.md`, INT-2 `intent/INT-2-test-hardening-and-contracts.md`, INT-3 `intent/INT-3-test-data-sets.md` (all three `status: accepted`, `accepted_by: Michael Hay on Nov 14, 2026`; see "Intent review"). INT-7 `intent/INT-7-github-app.md` was considered and kept out (Open question 15).

## Objective

A person who has never read the process documents can finish every human step of a coordinator-written pull request from the text in the pull request alone (INT-27). The server's tool behavior is pinned by recorded contract tests, the write and error paths that are not yet tested are tested, and the import rule is enforced by a test (INT-2). A curated messy and a curated hostile instance are committed, a real-data rule and scan exist, and an external test organization (Megaroast, four repositories) is set up as the real-shaped testbed (INT-3). The bundle is then released as v0.3.1 (INT-27 owner answer). Phase 5 server work (the content store refactor, INT-4, and later) then has a safety net.

## Intent review

The owner accepted the three intents on Nov 14, 2026 and wrote answers inline on each one. The plan is approved only by the owner's own name on **Approved by** above; no agent fills it.

### INT-27 Tell the human exactly what to do, and where to write, in the pull request
**Asks:** Put visible, numbered **Instructions** next to every human step of the pull request (CI line, ready-check table, ticks, GitHub's Approve review), and one replaceable `<Insert ...>` slug in every place a human writes a name and date, so an unfilled field is found by a script. It never lets an agent fill a human's part.
**Owner's answers (in the intent file):** one slug shape, an unreplaced slug counts as missing, the plan, test-plan and intent human lines are covered, instructions are visible text, they ship in the bundle for every repository, and the work is released as v0.3.1. The self-approval question is not answered (Open question 3).
**Plan changes:** (1) Its scenario S6 asks `/phase-status` to list unreplaced slugs, but that script reads only files in the repository and the pull request description is not one; the plan adds an optional `--pr-body <file>` input (Open question 6). (2) Task 1 reads GitHub's documentation on self-approval first. (3) A `<...>` slug may be hidden by GitHub's Markdown rendering; Task 1 checks (unverified until then).
Intent accepted by: Michael Hay on Nov 14, 2026 (recorded in the intent file's `accepted_by`)

### INT-2 Test hardening and contract tests for the server
**Asks:** Pin what every MCP tool promises its callers as recorded request/response tests that change only by a reviewed edit, run the official MCP conformance checks, close gaps in write and error paths, and enforce by test that only the entry module imports the web framework.
**Owner's answers (in the intent file):** all three questions (recording format and place, conformance required or advisory, coverage gate) are answered "survey the repository first; the implementation has moved on; planning must find how much work is needed; I believe some rules may exist". The survey was done for this plan; its findings and the decision per question are below.
**Survey (read on 2026-11-14; 678 test functions in 60 files under `server/tests/`):**

| Question | Found | Decision (owner may overrule) |
|----------|-------|-------------------------------|
| Recorded contracts | No recording, snapshot or golden file in `server/tests` (searched for those words). Every tool is exercised by behavior tests (`test_tool_policy.py` lists valid arguments for each of the 16 tools, `test_tool_authz.py`, `test_handoff_*.py`, `test_onboarding.py`, `test_example_acme.py`), but `wiki_export_helper_tool` and `wiki_list_helpers_tool` appear only in `test_tool_policy.py` (who may call them, not what they return). Reusable: `ToolWorld.call` in `server/tests/conftest.py`, the `acme` fixture in `test_example_acme.py`, the tool set equality in `test_tool_policy.py`. | The harness and recordings are needed (S1); the work stays, built on those three patterns (Open question 7). |
| Import rule | Only `server/server.py` imports `fastmcp` or `starlette` (searched `server/`). No test enforces it; `test_offline_clean.py` has the AST scan to copy but covers only HTTP clients. | A small test is needed (S4), Task 15. |
| Failed-write tests | Stale etag (`test_pickup_stale_etag_rejected`) and bad frontmatter (`test_write_validation.py`) are tested for refusal. No test injects a full disk or a git refusal, or checks that the tree, sidebar and log are unchanged afterwards. | Task 20 stays, narrowed to the missing cases. |
| HTTP errors | Host, origin and 401, 403, 421 refusals are covered (`test_request_guard.py`, `test_auth*.py`, `test_docs_route_policy.py`); `/ingest` traversal returns 400 (`test_server_smoke.py`). Nothing for malformed JSON, an unknown tool, a missing or wrong-typed argument, `GET /mcp` or an oversized body. | Task 21 stays, only for those cases. |
| Conformance suite | No conformance run anywhere. `server.yml` job `image` checks only an `initialize` call by `curl`. Not read yet: whether the official suite can run offline (unverified until Task 14). | Advisory, and only if Task 14 shows it runs offline (Open question 8). |
| Coverage gate | No coverage tool or percentage anywhere: not in `server/requirements-dev.txt`, `.github/workflows/*`, `REVIEW.md`, `CONTRIBUTING.md`. The only coverage text is the template section "Coverage judgement" (a judgement of cases, not a number), and the rule `no-generated-artifacts-in-commits` (do not commit coverage data). The "thresholds" in `SATISFACTION_REPORT_TEMPLATE.md` belong to the quality side. | No percentage gate. The gates are "every registered tool has a recording" and the import rule (Open question 9). |
| What blocks a merge today | Required checks are only `test (3.10)` and `test (3.12)` of `ci.yml`, the bundle tests (`docs/process/BRANCH_RULES.md`). The `server.yml` jobs are not required, so a failing server test does not block a merge. | Concerns 6 and Open question 19; the ruleset is the owner's act. |

**Plan changes:** (1) Its scenario S3 ("a failed write leaves the instance clean", including "git refuses") conflicts with what the code documents today: `git_commit` is deliberately non-fatal and the file stays on disk after a refused commit (`server/wiki_backend/write.py`, `git.py`); also `write_page_of_kinds` creates the parent folder before the etag and frontmatter checks. The plan writes the tests, and any test that fails is reported as a defect, not fixed here (Concerns 1). (2) The conformance suite is not read yet (unverified); Task 14 reads it before any CI change. (3) "Python versions the server supports" means 3.11 and 3.12 (`server/requirements.txt`, `.github/workflows/server.yml`).
Intent accepted by: Michael Hay on Nov 14, 2026 (recorded in the intent file's `accepted_by`)

### INT-3 Test data sets, real and synthetic
**Asks:** A seeded generator for instances of any size, a small set of committed curated instances for awkward and hostile content, and a written rule for when real data may be used and how it is scrubbed.
**Owner's answers (in the intent file):** use the external test organization Megaroast as the testbed, with four repositories: (1) a fork of the company's `company_dns`, (2) a new repository that pulls the GUI out of `company_dns` as a standalone, (3) a holdout QA repository, (4) an example manifold repository; consider a simple GitHub App; sizes and committed-versus-generated are "start with Megaroast, see above".
**Plan changes:** (1) The sized generator is deferred (Open question 17); the curated messy and hostile instances stay because S2 and the awkward-case constraint do not depend on size. (2) The Megaroast repositories derive from the owner's company repository, so the real-data rule is now used, not only written: nothing from them enters this repository, and the permission and visibility are the owner's decisions (Open question 16). (3) The only forbidden-terms scan today is for the bundle (`FORBIDDEN_TERMS` in `bundles/base/tools/build.py`); the data sets need their own scan, and a list of real names cannot itself be committed in a public repository (Open question 12). (4) The GitHub App is not pulled in (Open question 15).
Intent accepted by: Michael Hay on Nov 14, 2026 (recorded in the intent file's `accepted_by`)

### INT-7 (considered, not accepted into this phase)
See Open question 15, "Decision recorded by the coordinator and planner on the owner's delegation". INT-7 stays `accepted` and unplanned.

## Scope

**In scope:**

- CP1 (INT-27): visible **Instructions** and one slug shape in the pull request template, the plan, test-plan and intent templates, `REVIEW_CYCLE.md`, the coordinator and the rule/agent text that reads a blank approval; `/phase-status` reports unreplaced slugs. Both flavors from one source.
- CP2 (INT-2): import-rule test, contract-test harness and recordings for every tool, the missing write-failure and HTTP-error tests, the conformance run (if the owner agrees).
- CP3 (INT-3): curated messy and hostile instances with a loader and tests, the real-data rule, scan and sign-off record, and the Megaroast testbed (four repositories created by the owner, checked from a scratch clone).
- CP4 (release): the bundle version becomes 0.3.1 and the owner tags it.

**Out of scope:**

- The content store refactor (INT-4) and the GitHub-API store (INT-14): they change the server this phase protects, so they follow it.
- INT-7 (the GitHub App) and the GitHub part of INT-6 (creating the instance repository through the App): the server makes no GitHub call today and no feature of this phase uses an App. The reasoning and the alternatives are in Open question 15; the owner may overrule.
- The work inside the Megaroast repositories (extracting the GUI from `company_dns`, the holdout scenarios, the example instance's content): it belongs in those repositories under their own plans. This plan only needs the four repositories to exist.
- The sized synthetic generator of INT-3 S1 (small, medium, large): deferred, owner to confirm (Open question 17). Its tasks are in this file at commit `f939205` (old Tasks 23, 25 and 26).
- INT-24 (review and answer in the UX): needs a UI; INT-27 stays plain text.
- INT-5 (agent harvest) and the rest of the backlog: not needed by the safety net and not started.
- Changing the GitHub ruleset, `.github/workflows/` (except the one optional job in Task 22, with the owner's go-ahead), and making the server tests a required check (Concerns 6).
- Fixing any defect that Tasks 20 and 21 expose: recorded and handed to `bug-coder` after the owner decides (Concerns 1).
- Performance and load tests, a UI, language-model-generated content (INT-2 and INT-3 Out of scope).
- Noticed, not done: `docs/process/BRANCH_RULES.md` records `RepositoryRole` 5 and `require_extra_approval_for_unattributed_changes` as unverified; Task 12 adds only what Task 1 reads.

**Needs from other repositories:** The four Megaroast repositories (CP3, Tasks 29 to 32) must exist before Task 33. They are created by the owner in the external organization, not by this plan's code changes.

**Provides to other repositories:** Repositories that install the bundle receive the new template, process and agent text and the extended `/phase-status`, as release 0.3.1. Megaroast becomes the first test organization that INT-7 names in its "Affected users and systems", so a later INT-7 plan starts with an organization that exists.

**Constraints:**
INT-27: a human keeps the final say (instructions tell, never do; the coordinator never approves, moves out of draft, merges, ticks or fills a human field); instructions are in the pull request itself, not a link; ready still means reviewed (no ready-check line dropped or loosened); approval follows `AGENTS.md` "Review process" (solo is not made to look like a team); facts are not duplicated (point to `REVIEW_CYCLE.md` "Where each fact is recorded"); shipped text stays generic (`M. Kusanagi` is a neutral placeholder); both flavors from one source, deterministic build, standard library only for any script; concise, numbered, plain words, no bare internal IDs; no outward action without the owner (editing a live pull request, the ruleset, the workflow); no unverified claim about GitHub.
INT-2: no network and no real git remote in tests, finishing in a laptop-tolerable time; recorded responses contain no real data (the fictional example instance only); a change to a recording is a visible, reviewed decision, never automatic; only the entry module imports the web framework, enforced by a test; no flaky tests; tests run on the Python versions the server supports.
INT-3: nothing real enters a public repository without the owner's written permission and a checked scrub (until then only synthetic data); deterministic, same seed gives the same instance byte for byte (applies if the generator is kept); small enough to commit, or generated on demand when large; covers dotted and similar slugs, a page with no frontmatter, duplicates, stale pages, very long pages, non-English text and text aimed at an AI; no personal data, not even fake data that looks like a real person's.
INT-7 (applies to the interim route and to any later App): least privilege; private first; no long-lived secret in the instance repository, the private key outside it; short-lived tokens only; the name `manifold` available or a fallback chosen; what an App cannot do is verified before any plan relies on it; one App per company, created by the company. This plan creates no App and writes no key, token or secret anywhere.

## Concerns flagged

1. **INT-2 S3 versus documented behavior.** `git_commit` is non-fatal by design (the file stays when git refuses), and `write_page_of_kinds` runs `file_path.parent.mkdir(...)` before the conflict and frontmatter checks, so a refused write may leave an empty folder. S3 says a refused write leaves "no partial files". Owner decides: (a) keep the code, and narrow S3 to the cases the code already supports, or (b) treat the differences as defects for `bug-coder`. Default: the tests are written to S3 as the intent states it, any failure is recorded and not fixed in this phase, and the owner chooses (a) or (b) per failure.
2. **Split (settled).** INT-27 and INT-2/INT-3 touch different surfaces. The owner chose one plan (Open question 1); CP1 is delivered as its own pull request first, and CP2 and CP3 follow in later pull requests.
3. **`<Insert ...>` may not render in GitHub Markdown.** An unknown tag may be hidden in the rendered description (unverified: confirm with GitHub's Markdown documentation or a comment preview, Task 1). If hidden, the slug goes inside a code span and the detector accepts the span; the owner decides at Task 1.
4. **A slug in a plan's Approved by line must still count as blank** for `coder` and `test-coder` and for `/phase-status` (it already treats a `<...>` value as blank). Tasks 8 and 11 make that explicit; if it is missed, a slug would read as an approval.
5. **The conformance suite and CI.** Whether it runs offline against a locally started server, and what runtime it needs, is unread (unverified: confirm with the MCP project documentation, Task 14). Making it a required check is a ruleset change, the owner's act.
6. **The server tests do not block a merge today.** The required checks are only `test (3.10)` and `test (3.12)` from `ci.yml` (the bundle tests); the `server.yml` jobs are not required (`docs/process/BRANCH_RULES.md`). INT-2 S2 says a conformance failure "blocks the merge", and the contract tests of CP2 would not block one either. Making them required is the owner's act on GitHub, out of scope here (Open question 19).
7. **Real data in the Megaroast repositories.** They derive from the owner's company repository. INT-3 forbids real content in a public repository without the owner's written permission and a checked scrub. Whether the Megaroast repositories are public, and whether the company permits the derivation at all, is not stated anywhere I read (Open question 16). Until the owner answers, nothing from those repositories is committed here, no test reads them, and Tasks 29 to 33 do not start.
8. **The holdout QA repository.** `AGENTS.md` "Held-out scenarios": builders do not read, copy or ask for the quality side's scenarios. Task 31 therefore creates repository 3 empty and no builder agent session in this repository clones or reads it.
9. **INT-7 not pulled in** (Open question 15): the owner's idea to accelerate it is respected as a decision the owner can overrule; the cost of overruling is stated there.

## Prerequisites

- [x] Phase 3 merged (`4516792`); release 0.3.0 (`4f8b448`); `bundles/base/VERSION` reads `0.3.0`.
- [x] Project commands known: `AGENTS.md` "Project commands" (read; `pytest` here means the server tests command).
- [ ] The `.venv` exists (`python3 -m venv .venv`, then the install line in `AGENTS.md`; none exists in this worktree).
- [ ] The owner answered the Open questions still empty: 3 and 6 before CP1; 10 before Task 20 (CP2); 12, 16, 17 and 18 before CP3.
- [ ] For Task 1: the owner's go-ahead to read GitHub's documentation and the repository's settings with `gh` (GET only).
- [ ] For Task 22 only: the owner's go-ahead to edit `.github/workflows/server.yml`.
- [ ] For Tasks 28 to 33 (outward actions in the Megaroast organization, using the owner's own GitHub login): the owner's go-ahead for each task. No agent reads, prints or stores a token; `gh auth token` is not run; no key or token is written to the repository or to chat.
- [ ] CP1 is its own pull request and is merged before CP2 starts (Open question 1).

## File inventory

| Path | Action | Reason |
|------|--------|--------|
| `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `docs/templates/PULL_REQUEST_TEMPLATE.md` | MODIFY | instructions, slugs, state values (the two copies stay identical) |
| `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`, `PHASE_TEST_PLAN_TEMPLATE.md`, `INTENT_TEMPLATE.md` and their `docs/templates/` copies | MODIFY | slug and instructions on the human lines (if Open question 4 is yes) |
| `bundles/base/process/REVIEW_CYCLE.md` and `docs/process/REVIEW_CYCLE.md` | MODIFY | slug rule, Approve review, ready check |
| `bundles/base/agents/coordinator.agent.md`, `coder.agent.md`, `test-coder.agent.md`, `bundles/base/rules/core/approved-plan-before-execution.md` | MODIFY | CI line shape, never fill a slug, a slug is blank |
| `bundles/base/scripts/phase_status.py`, `bundles/base/commands/phase-status.md`, `phase-status.prompt.md` | MODIFY | report unreplaced slugs, `--pr-body` |
| `bundles/base/tests/test_bundle.py`, `bundles/base/tests/test_phase_status.py` | MODIFY | tests next to each change |
| `docs/process/BRANCH_RULES.md` | MODIFY | the Approve review facts read in Task 1 (not shipped) |
| `.claude/agents/*`, `.claude/commands/phase-status.md`, `.manifold/*`, `docs/process/*`, `docs/templates/*`, `AGENTS.md` managed block | MODIFY | refresh of this repository's own install (generated by `install.py`) |
| `server/tests/test_import_rule.py` | CREATE | INT-2 S4 |
| `server/tests/contracts/` (`harness.py`, `record.py`, `test_tool_contracts.py`, `test_harness.py`, `<tool>.json` files) | CREATE | INT-2 S1 |
| `server/tests/test_write_failures.py`, `server/tests/test_http_errors.py` | CREATE | INT-2 S3 and the HTTP layer |
| `.github/workflows/server.yml` | MODIFY | optional advisory conformance job (Task 22) |
| `server/tests/datasets/` (`curated/`, `loader.py`, `scan.py`, `README.md`, `SIGNOFFS.md`, `test_datasets.py`) | CREATE | INT-3 (no generator: Open question 17) |
| `bundles/base/VERSION`, `.manifold/manifest.json` | MODIFY | release 0.3.1 (Tasks 34, 35), as in `4f8b448` |
| Megaroast repositories 1 to 4 (outside this repository) | CREATE by the owner | INT-3 testbed; nothing from them is committed here |

## Tasks

> **Instructions for the coder:**
> Work one checkpoint at a time, tasks in the order listed. For each task: read
> the named files first, implement the described change, run the verify command
> and the task's acceptance check, then update the todo marker `[ ]` → `[x]` and
> add a one-line completion note directly beneath the task header: what changed,
> the command run, the result. At the end of a checkpoint run its Verification,
> report the gates with command and real counts, and stop until told to
> continue. If a task is blocked, mark it `[~]` with a note and surface it
> immediately; do not skip ahead. When all tasks are complete, fill in the
> completion summary under the Completion checklist.

### CP1 — Clear instructions in the pull request (INT-27)

### Task 1 — Read what GitHub says about approving and about the slug
**Source:** INT-27 S5 Must never; Open questions on self-approval and slug format
**Files:** none changed; the note goes here
**Action:** none (read)
**Change:** With the owner's go-ahead, read (a) GitHub's documentation on approving a pull request and on required approving reviews, for whether the author may approve and what the "Review changes" control shows when it cannot be used; (b) the ruleset with `gh api --method GET repos/{owner}/{repo}/rulesets/26275761` (read-only; the form is already used in `docs/process/BRANCH_RULES.md`); (c) whether GitHub's Markdown description renders `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>` visibly (read the Markdown documentation, or the owner pastes it into a comment preview without posting it). Record each fact with its source, or "unverified: confirm with <source>".
**Acceptance:** the note lists, per question (a), (b), (c), the fact and its source or "unverified". The owner then answers Open question 3 (Question 5 is already answered).
**Todo:** [ ]

---

### Task 2 — Add the slug rule and the Approve review to the review cycle
**Source:** INT-27 S3, S5, S6, S7; "Facts are not duplicated"
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** Add a section "Human fields and slugs" before "The ready check": the one slug shape `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>` (written out with the real example `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>`; the detection pattern is `<Insert [^<>]*>`); the human replaces the whole slug, brackets included; an agent never replaces one; a human field still holding a slug is missing, never met. Add a row "GitHub's Approve review" to "Where each fact is recorded" (a separate act in GitHub's "Review changes" control, not a row or tick of the description; who writes it: a human). In "The ready check" item 4 add one sentence that the Approve review is separate from the description's ticks and that nothing in the description satisfies it. Do not drop or loosen any ready-check line.
**Acceptance:** `grep -n "Human fields and slugs\|Approve review" bundles/base/process/REVIEW_CYCLE.md` finds the section and the row; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 3 — Split the CI section of the pull request template and add its instructions
**Source:** INT-27 S1, S2, S3, S7 (the owner's worked example)
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** Rewrite "CI on the pushed commit" to the shape of INT-27's "After" example: **Commit (full hash)**; "1. Ran:" with one numbered sub-line per workflow run (name, run id, status, conclusion, link, or "no run found"); an **Instructions:** block as visible text (not a comment) with the pass step (open each link; if every run is `completed` with `success`, write your name below), the fail step (if a run failed, is not `completed`, or is missing, tell the coordinator and do not write your name) ; then `**Confirmed by:** <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>` (label changed to "confirmer" and "confirmation" for this field). Keep the full hash. Replace the template's HTML-comment hints for this section with one line that the coordinator writes the evidence and leaves the slug.
**Acceptance:** `grep -c "<Insert " bundles/base/templates/PULL_REQUEST_TEMPLATE.md` is at least 1 for this field; the section has no HTML comment holding instructions; the hash line still says "full hash".
**Todo:** [ ]

---

### Task 4 — Make the ready-check State cell and the confirmation line say what to write
**Source:** INT-27 S3, S4
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** In "Ready check" change the header `State (met / missing)` to `State` and put into each State cell the placeholder `missing` (the safe value); add an **Instructions:** block above the table: the coordinator replaces the cell with exactly `met` or `missing`, `met` needs evidence in the Evidence cell, a human does not edit State cells. Replace the **Human confirmation** comment with the slug `<Insert Name of decider on Date of decision, ex. M. Kusanagi on Jan-01-2027>` plus numbered instructions (what to review, where, when to write the line, what not to write if a line is missing).
**Acceptance:** `grep -n "met / missing" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` prints nothing; both words `met` and `missing` appear in the instructions.
**Todo:** [ ]

---

### Task 5 — Add instructions to each tickable line and a step for the Approve review
**Source:** INT-27 S1, S5; Problem items 2 and 4
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** Under "What remains for you" add an **Instructions:** block per kind of line: (a) per changed file: open the diff on the Files changed tab, what to look for, a tick means you read it and accept it, and if you do not accept it, leave it unticked and say why in a comment; (b) the CI line: points to the instructions under "CI on the pushed commit" (no second copy); (c) findings: read the "Decisions for you" table, write "accept all" or name the exceptions. Add a numbered step "GitHub's Approve review": separate from every tick and row here; needed when the repository's rules require an approving review (see its `Review process` and branch rules); where to click ("Review changes" on the Files changed tab, then Approve); if the control is missing or disabled for you, do not write a name or tick here instead, and ask the owner how approval is met in this repository. Add the fact Task 1 found, if it was read (otherwise no claim about GitHub). Keep each block to numbered short lines.
**Acceptance:** `grep -n "Approve review\|Review changes" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` finds the step; it makes no claim about self-approval (read the diff).
**Todo:** [ ]

---

### Task 6 — Add tests for the pull request template
**Source:** INT-27 S1, S3, S4, S7
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_pr_template_has_visible_instructions_and_one_slug_shape` (every human-written line, `Confirmed by` and `Human confirmation`, holds exactly one match of the pattern `<Insert [^<>]*>`; no instructions sit only inside an HTML comment; the pattern finds no text in the rest of the template), `test_pr_template_state_cells_name_both_values` (no `met / missing`; both words in the instructions), `test_pr_template_names_the_approve_review_and_claims_nothing_about_self_approval` (contains "Approve" and "Review changes"; contains none of "own pull request", "self-approv", "cannot approve"), and `test_pr_template_is_generic` (no "Michael Hay", no repository name). Follow the style of the existing `test_pr_template_has_remaining_steps_and_decisions_table`. Failing first: run them before Tasks 3 to 5 are applied to the source and record the counts.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "pr_template"` passes (counts reported); the note records the failing-first run.
**Todo:** [ ]

---

### Task 7 — Put the slug and instructions on the plan, test-plan and intent human lines
**Source:** INT-27 Open question on the other human lines (apply if answered yes)
**Files:** `bundles/base/templates/PHASE_PLAN_TEMPLATE.md` (**Approved by**, **Amendment approved by**), `PHASE_TEST_PLAN_TEMPLATE.md` (**Approved by**), `INTENT_TEMPLATE.md` (`accepted_by`)
**Action:** MODIFY
**Change:** On each line put the slug and one visible **Instructions:** line under it (what to read, then replace the whole slug; an agent leaves it). In `INTENT_TEMPLATE.md` the slug is a quoted YAML string (`accepted_by: "<Insert ...>"`) so the frontmatter still parses; the first line stays `---`. The reviewer's text "A blank **Approved by** is the right state of a new test plan" stays true and now also names a slug.
**Acceptance:** `grep -c "<Insert " bundles/base/templates/PHASE_PLAN_TEMPLATE.md` is 2; `.venv/bin/python -c "import yaml,sys; t=open('bundles/base/templates/INTENT_TEMPLATE.md').read().split('---')[1]; print(yaml.safe_load(t)['accepted_by'])"` prints the slug (PyYAML is in `server/requirements.txt`).
**Todo:** [ ]

---

### Task 8 — State that an unreplaced slug counts as a blank approval
**Source:** INT-27 S6, S7; Concerns 4
**Files:** `bundles/base/rules/core/approved-plan-before-execution.md`, `bundles/base/agents/coder.agent.md` (line 24 and 34), `bundles/base/agents/test-coder.agent.md` (line 33)
**Action:** MODIFY
**Change:** Where each says "If it is blank", add "or still holds an `<Insert ...>` slug" (same words in all three). No other word changes.
**Acceptance:** `grep -rn "Insert" bundles/base/rules/core/approved-plan-before-execution.md bundles/base/agents/coder.agent.md bundles/base/agents/test-coder.agent.md` finds all three; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 9 — Teach the coordinator the new CI line, the slugs and the rule that it never fills one
**Source:** INT-27 S2, S6, S7
**Files:** `bundles/base/agents/coordinator.agent.md` ("CI of the exact commit", "Ready check", "What you do not do")
**Action:** MODIFY
**Change:** In "CI of the exact commit" write the result as the numbered shape of Task 3 (one line per run with link; the **Instructions:** block; the slug left as is) and never tell the human to confirm when a run is not `completed` with `success`. In "Ready check" treat any `<Insert` text left in a human field as missing and name each such field in the report. Add to "What you do not do": replace a slug, write a name or date in a human field, tick a box, or write "approved" for a human. Do not weaken any existing line.
**Acceptance:** `grep -n "Insert\|never replace" bundles/base/agents/coordinator.agent.md` finds each; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 10 — Add tests for Tasks 2, 7, 8 and 9
**Source:** INT-27 S6, S7
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_review_cycle_defines_slug_rule_and_approve_review`, `test_plan_and_intent_templates_carry_a_slug` (and the intent frontmatter parses), `test_blank_approval_text_counts_a_slug_as_blank` (rule, coder, test-coder), `test_coordinator_never_fills_a_slug_and_treats_one_as_missing`. If an existing test pins text these tasks changed, stop, name the test and the assertion and ask the owner before editing it. Failing first, counts recorded.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "slug or approve_review or blank_approval"` passes with the counts reported.
**Todo:** [ ]

---

### Task 11 — Report unreplaced slugs in `/phase-status`
**Source:** INT-27 S6
**Files:** `bundles/base/scripts/phase_status.py`, `bundles/base/commands/phase-status.md`, `bundles/base/commands/phase-status.prompt.md`, `bundles/base/tests/test_phase_status.py`
**Action:** MODIFY
**Change:** Add `SLUG_RE = re.compile(r"<Insert [^<>]*>")` and a function `slugs(lines, label)` that returns, for each match on a line, the field name taken from the text before the first colon on that line with asterisks removed (for example `Approved by`, `Confirmed by`, `Human confirmation`, `Intent accepted by`). In `report`, add a section "Unreplaced slugs" over the plan and test plan, listing `file:line field`; add each to `reasons` so the level reads below mergeable. Add an optional `--pr-body <file>` (parsed like `--root` in `main`) that scans a saved copy of the description the same way and prints the same list; with the option absent the output states that the pull request description was not read. Standard library only, read-only, sorted output. Update `argument-hint` in both command files to `<phase number> [--pr-body <file>]`. Add tests: a plan with a slug reports it and level below mergeable; a plan with the slug replaced lists none; `--pr-body` with two slugs lists both by field name; output is identical on two runs.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` passes (counts reported); `.venv/bin/python bundles/base/scripts/phase_status.py 4` run on this plan lists no unreplaced slug (the three "Intent accepted by" lines now hold the owner's recorded value, and the plan's own **Approved by** line is blank, not a slug), and run on a copy of the plan in the scratchpad where one "Intent accepted by" line holds the slug it lists exactly that line; it is read-only (`git status --short` unchanged).
**Todo:** [ ]

---

### Task 12 — Record the Approve review facts in the branch rules
**Source:** INT-27 Affected files (`docs/process/BRANCH_RULES.md`); Open question on self-approval
**Files:** `docs/process/BRANCH_RULES.md` (not shipped)
**Action:** MODIFY
**Change:** In the "Approving reviews" row and the sentence "how the owner's approval is met ... is not recorded here", record only what Task 1 read, with its source, and the route the owner chose in answer 3 (document an existing route, a second account, or a ruleset change, which stays the owner's act). Write "unverified: confirm with <source>" for anything not read.
**Acceptance:** each new statement shows its source or "unverified"; `git diff --stat -- .github` is empty.
**Todo:** [ ]

---

### Task 13 — Refresh this repository's own install from the build
**Source:** INT-27 Affected files (installed copies); Phase 3 Task 18 route
**Files:** `docs/templates/*`, `docs/process/REVIEW_CYCLE.md`, `.claude/agents/*`, `.claude/commands/phase-status.md`, `.manifold/*`, `AGENTS.md` managed block (all generated)
**Action:** MODIFY
**Change:** Build into the scratchpad (`python3 bundles/base/tools/build.py --out <scratchpad>/dist`), unzip, read `install.py --help`, run the install over this repository as in Phase 3 Task 6 (dry run first, then `--apply` without `--force`); stage explicit paths only. Do not hand-edit the managed block.
**Acceptance:** `cmp bundles/base/templates/PULL_REQUEST_TEMPLATE.md docs/templates/PULL_REQUEST_TEMPLATE.md` prints nothing; `install.py --status` from the unzipped bundle reports no modified file.
**Todo:** [ ]

---

**Verification:** `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported); two `build.py --out` runs give zips that `cmp` equal; the built zip contains the new template text once for both flavors (`build.py` has no flavor flag, per Phase 3). Observe: a copy of the PR template with every slug replaced makes `phase_status.py 4 --pr-body <copy>` list none. The owner reads the rendered template in a GitHub comment preview (not posted) and answers whether a first-time reader could act on it.

### CP2 — Contract tests and hardening for the server (INT-2)

### Task 14 — Read the MCP conformance suite
**Source:** INT-2 S2; Open question on required versus advisory
**Files:** none changed; the note goes here
**Action:** none (read)
**Change:** Read the MCP project's documentation for its official conformance checks: the command, the runtime it needs, whether it runs against a locally started HTTP server without internet access, and how it passes a bearer token (the server refuses unauthenticated requests, `/mcp` returns 401). Record each fact with its source, or "unverified: confirm with <source>". Settle with the owner whether Task 22 is possible.
**Acceptance:** the note lists command, runtime, offline behavior, auth handling, each with source or "unverified".
**Todo:** [ ]

---

### Task 15 — Enforce by test that only the entry module imports the web framework
**Source:** INT-2 S4 and Constraints
**Files:** `server/tests/test_import_rule.py` (CREATE)
**Action:** CREATE
**Change:** Follow `server/tests/test_offline_clean.py` (`imported_names` over `ast`). Scan `server.py`, `wiki_backend/`, `manifold_security/` and `manifold_cli/`. Define `FRAMEWORK = {"fastmcp", "starlette", "uvicorn", "mcp"}` and `ENTRY_MODULES = {"server.py"}`. `test_only_the_entry_module_imports_the_framework` fails for any other module whose top-level import name is in `FRAMEWORK`; `test_the_entry_module_list_has_one_member` asserts `len(ENTRY_MODULES) == 1` so the exception list cannot grow unnoticed. Failing first: a test copy of a module with `import starlette` is flagged by the scan function.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/test_import_rule.py -q` passes (counts reported); today's code passes (grep found `server.py` only).
**Todo:** [ ]

---

### Task 16 — Create the contract harness and the explicit recorder
**Source:** INT-2 S1, Constraints (reviewed change, fictional instance, offline)
**Files:** `server/tests/contracts/harness.py`, `server/tests/contracts/record.py` (CREATE)
**Action:** CREATE
**Change:** Format (Open question 7 default): one JSON file per tool and case, `server/tests/contracts/<tool>.<case>.json`, holding `{"tool", "arguments", "caller": {"kind", "roles"}, "result"}`. `harness.py`: `normalise(value)` replaces volatile values (commit hashes, timestamps, generated ids) by fixed tokens; `compare(tool, recorded, actual)` walks both and raises an `AssertionError` that names the tool and the dotted field path (`wiki_read_tool: result.etag: expected str, got missing`); `run_case(tool_world, case)` calls the tool with `ToolWorld.call` from `server/tests/conftest.py` against a private copy of `examples/acme` (the `acme` fixture of `test_example_acme.py` is the pattern). `record.py` writes recordings only when run by hand as `python server/tests/contracts/record.py --write`, and exits with code 2 when the environment variable `CI` or `PYTEST_CURRENT_TEST` is set; no test module imports it.
**Acceptance:** `python3 server/tests/contracts/record.py` without `--write` prints usage and writes nothing; `CI=1 python3 server/tests/contracts/record.py --write` exits 2 (run in a scratch copy, not the repository).
**Todo:** [ ]

---

### Task 17 — Record and test the contracts of the read tools
**Source:** INT-2 S1
**Files:** `server/tests/contracts/test_tool_contracts.py`, the `<tool>.<case>.json` files for `wiki_ping_tool`, `wiki_read_tool`, `wiki_inventory_tool`, `wiki_freshness_tool`, `wiki_onboarding_tool`, `wiki_reconcile_plan_tool`, `wiki_bundle_info_tool`, `wiki_list_helpers_tool`, `wiki_export_helper_tool`, `wiki_export_component_helpers_tool` (CREATE)
**Action:** CREATE
**Change:** One success case per read tool and one error case where the tool has one (`wiki_read_tool` on a missing path and on a path outside the wiki). `test_tool_contracts.py` parametrises over the recording files and calls `harness.compare`. Record with the explicit command of Task 16 and commit the files as a reviewed diff; the coder reads each file for real data before staging (the fictional instance only).
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/contracts -q` passes (counts reported); `grep -rIl "mediumroast" server/tests/contracts` prints nothing.
**Todo:** [ ]

---

### Task 18 — Record and test the contracts of the write, handoff and component tools
**Source:** INT-2 S1, Problem (write paths thin)
**Files:** `server/tests/contracts/*.json` for `wiki_write_page_tool` (create, update, stale etag, protected-field change, invalid frontmatter), `wiki_log_append_tool`, `wiki_agent_catalog_tool`, `wiki_handoff_tool` (each of the seven actions in `TOOL_POLICY`: create, claim, request-review, confirm, reject, close, list), `wiki_register_component_tool`, `wiki_component_manage_tool` (update, archive, restore) (CREATE)
**Action:** CREATE
**Change:** One recording per case, same format and recorder. Each case lists the principal and roles it ran as (the policy lists of `server/tests/test_tool_policy.py` give valid arguments).
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/contracts -q` passes (counts reported).
**Todo:** [ ]

---

### Task 19 — Add the harness self-tests and the coverage test
**Source:** INT-2 S1 (We will know when; Must never)
**Files:** `server/tests/contracts/test_harness.py` (CREATE)
**Action:** CREATE
**Change:** `test_a_renamed_field_names_the_tool_and_the_field` (rename one field of an in-memory copy of one recording; `compare` fails with a message containing the tool name and the field path; no other tool's test is involved); `test_every_registered_tool_has_a_contract` (set of tools in `server.app.list_tools()` equals the set that has at least one recording, as `test_tool_policy.py` does for the policy); `test_nothing_regenerates_a_recording_during_a_test_run` (no test module imports `record`, and `record.py` refuses under `PYTEST_CURRENT_TEST`).
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/contracts -q` passes (counts reported); failing first: delete one recording locally and see `test_every_registered_tool_has_a_contract` fail, then restore it.
**Todo:** [ ]

---

### Task 20 — Test that a failed write leaves the instance as it was
**Source:** INT-2 S3 and Must never; Concerns 1
**Files:** `server/tests/test_write_failures.py` (CREATE)
**Action:** CREATE
**Change:** Read `write_page_of_kinds` and `handoff_create` first to name each failure point. The refusals of a stale etag and bad frontmatter are already tested (`test_pickup_stale_etag_rejected`, `test_write_validation.py`); do not repeat them, only add the unchanged-tree assertion for them. Using `ToolWorld` and monkeypatch, inject: a stale etag; invalid frontmatter; a write refused (`OSError` with `errno.ENOSPC` from `Path.write_text`); git refusing the commit (`git_commit` returning `committed=False`); a failure part-way through `handoff_create`. After each, assert that the tree (relative paths, empty folders and sha256 of every file outside `.git`), `wiki/_sidebar.md` and `wiki/log.md` equal their snapshot from before the call, and that `wiki_health` reports healthy. Where the existing code fails the assertion (Concerns 1), mark the case `pytest.mark.xfail(strict=True, reason="defect: <one line>")` with the reason, so the suite stays green and the defect is listed, and stop to ask the owner; do not edit the code.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/test_write_failures.py -q` passes (counts reported, including the number of xfail cases, each named in the note).
**Todo:** [ ]

---

### Task 21 — Test the HTTP layer's refusals and errors
**Source:** INT-2 Problem (HTTP layer thin)
**Files:** `server/tests/test_http_errors.py` (CREATE)
**Action:** CREATE
**Change:** Use `TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")` as `test_request_guard.py` does. Do not repeat the host, origin, 401, 403 and 421 cases that `test_request_guard.py`, `test_auth.py` and `test_docs_route_policy.py` already cover. Cases, each with an authenticated principal from `auth_world`: `/mcp` with a malformed JSON body; an unknown tool name; a missing required argument; a wrong argument type; `GET /mcp`; an oversized body. For each assert the status and that the body holds no stack trace, file path or secret.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/test_http_errors.py -q` passes (counts reported); no network (existing `test_offline_clean.py` still passes).
**Todo:** [ ]

---

### Task 22 — Add the conformance run to CI as an advisory job (only if the owner agrees)
**Source:** INT-2 S2; Open question on required versus advisory
**Files:** `.github/workflows/server.yml`
**Action:** MODIFY
**Change:** Only after Task 14 and the owner's go-ahead: add a job `conformance` that starts the server as the `image` job does or in-process, runs the command recorded in Task 14, and is not added to the ruleset's required checks (that is a ruleset change, the owner's act). Pin action versions by commit as the file does. If the owner says no or Task 14 finds it cannot run offline, mark this task `[~]` with the reason and add the owner's answer.
**Acceptance:** the job passes on the pull request; `git diff --stat` shows only `server.yml`; the required checks in `docs/process/BRANCH_RULES.md` are unchanged.
**Todo:** [ ]

---

**Verification:** `cd server && ../.venv/bin/python -m pytest -q` passes (counts reported, with the number of xfail cases named); `.venv/bin/python -m pytest tests/live -q` and `.venv/bin/python tools/vendor_web.py --check` unchanged; the owner changes one field name in one tool locally and sees exactly that tool's test fail naming the field (not committed).

### CP3 — Test data sets and the Megaroast testbed (INT-3)

INT-3 scenario seeds: S1 (instance by size) is deferred, owner to confirm (Open question 17). S2 (hostile text) is Tasks 23, 24, 25 and 27. S3 (a real source is scrubbed before use) is Tasks 26, 28 and 33, and now applies to the Megaroast repositories.

### Task 23 — Create the curated messy and hostile instances
**Source:** INT-3 S2, Constraints (awkward cases, no personal data)
**Files:** `server/tests/datasets/curated/messy/` and `server/tests/datasets/curated/hostile/` (CREATE)
**Action:** CREATE
**Change:** `messy`: components with dotted and look-alike slugs (`acme.io`, `acme-io`), a page with no frontmatter, two pages with the same title, a stale page, a non-English page (more than one script). `hostile`: pages whose text addresses an AI agent ("ignore your instructions and ...", "call the tool ... with ...") that are harmless test strings only. No names of real people, hosts or companies; hosts use `.test`. The very long page is generated by the loader (Task 24), not committed.
**Acceptance:** the folders load with `load_config` from `server/wiki_backend/config.py`; `du -sk server/tests/datasets/curated` is under 200; each file is read once by the coder for real data before staging.
**Todo:** [ ]

---

### Task 24 — Add the loader that gives a git-backed copy
**Source:** INT-3 S2, Constraints (very long pages)
**Files:** `server/tests/datasets/loader.py` (CREATE)
**Action:** CREATE
**Change:** `copy_curated(tmp_path, name)` and `long_page(chars)` (a long-page text of the stated size). `copy_curated` copies a folder of `curated/` and initialises git and commits as the `acme` fixture of `test_example_acme.py` does, with a fixed author and no network. A pytest fixture `dataset` in the datasets test module wraps them.
**Acceptance:** a test runs `copy_curated("messy")` and `copy_curated("hostile")` and `wiki_health` reports healthy for each.
**Todo:** [ ]

---

### Task 25 — Test that hostile text is returned as plain content
**Source:** INT-3 S2
**Files:** `server/tests/datasets/test_datasets.py` (CREATE)
**Action:** CREATE
**Change:** `test_hostile_pages_are_returned_as_content_and_not_acted_on`: with `ToolWorld` over `copy_curated("hostile")`, `wiki_read_tool` returns each page's text unchanged in its content field; `wiki_inventory_tool` and `wiki_freshness_tool` run over the instance; the wiki tree and `log.md` are unchanged afterwards, and the git log has no new commit.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q -k hostile` passes (counts reported).
**Todo:** [ ]

---

### Task 26 — Write the real-data rule, the scan and the sign-off record
**Source:** INT-3 S3, Constraints (nothing real without written permission and a checked scrub)
**Files:** `server/tests/datasets/README.md`, `server/tests/datasets/SIGNOFFS.md`, `server/tests/datasets/scan.py` (CREATE)
**Action:** CREATE
**Change:** `README.md` holds the awkward cases, the real-data rule (who gives permission: the data's owner, in writing; the scrub steps for names, hosts, secrets and email addresses; the check; "the original is never committed") and a short "Megaroast testbed" section: the organization's name, the four repositories by role (fork, standalone GUI, holdout QA, example instance), that they are outside this repository, that nothing from them is committed here, that no test reads them, and that no builder agent reads the holdout QA repository. Repository names are written only if the owner agrees (Open question 18). `scan.py`: `scan(path)` reports email addresses, hosts not ending in `.test`, `.example` or `.invalid`, strings shaped like tokens or keys, and every term listed in a private term list read from a file outside the repository whose path comes from the environment variable `MANIFOLD_SCAN_TERMS` (Open question 12; the list is never committed). `SIGNOFFS.md` holds a table with no rows yet (columns: source, owner, permission date, scrub checked by, scan result) and states that no real data is committed. A test in `test_datasets.py`, `test_scan_flags_real_shaped_text_and_passes_the_committed_sets`, feeds `scan` a temporary file with an email address, a non-test host and a token-shaped string, and runs it over `curated/`.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q -k scan` passes (counts reported); `scan.py` over `curated/` prints no finding.
**Todo:** [ ]

---

### Task 27 — Test that the curated sets cover the awkward cases and hold no personal data
**Source:** INT-3 Constraints (awkward cases, no personal data)
**Files:** `server/tests/datasets/test_datasets.py`
**Action:** MODIFY
**Change:** `test_the_sets_cover_every_awkward_case` asserts each of dotted slug, look-alike slug, no frontmatter, duplicate title, stale page (through `wiki_freshness`), long page (via `long_page`), non-English text and AI-aimed text is present in `messy` or `hostile`; `test_no_set_contains_personal_data` runs `scan` for email addresses and for a first-name-plus-surname pattern list kept in the test, over every committed set.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q` passes (counts reported).
**Todo:** [ ]

---

### Task 28 — Record the owner's decisions on permission and visibility
**Source:** INT-3 Constraints (written permission, checked scrub); Concerns 7
**Files:** `server/tests/datasets/SIGNOFFS.md`
**Action:** MODIFY
**Who:** the owner writes the rows; the coder only prepares the empty table (Task 26) and an **Instructions** line above it.
**Change:** Add one row per Megaroast repository that derives from the company repository (repositories 1 and 2, and 4 if its content derives from it): source, owner, permission date, the repository's visibility (private or public), and "nothing committed here". The owner writes the name and date; the coder does not fill any cell. If the owner answers Open question 16 "no permission", Tasks 29 to 33 are marked `[~]` and stop.
**Acceptance:** each row is filled by the owner; `git diff` shows no content from any Megaroast repository, only the table rows.
**Todo:** [ ]

---

### Task 29 — Create Megaroast repository 1, the fork of the company's `company_dns`
**Source:** INT-3 owner answer (repository 1)
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner, using their own GitHub login (the coder does not run it).
**Change:** The owner forks the source repository into the Megaroast organization, private if Open question 16 says so, for example `gh repo fork <owner>/company_dns --org Megaroast` (flag `--org` verified in `gh repo fork --help`, gh 2.86.0), or by the GitHub page. No token or key is passed to, printed by or stored by an agent.
**Acceptance:** the owner confirms in chat the repository's URL and visibility; `gh repo view Megaroast/<name> --json visibility` (read-only, run by the owner) shows the visibility chosen in Task 28 (`visibility` is listed among the `--json` fields in `gh repo view --json`).
**Todo:** [ ]

---

### Task 30 — Create Megaroast repository 2, the standalone GUI
**Source:** INT-3 owner answer (repository 2)
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner.
**Change:** The owner creates an empty repository for the GUI, private if Open question 16 says so, for example `gh repo create Megaroast/<name> --private` (flag verified in `gh repo create --help`). Pulling the GUI out of `company_dns` is work inside that repository under its own plan and is out of scope here; this task needs only that the repository exists with a README.
**Acceptance:** the owner confirms the URL and visibility.
**Todo:** [ ]

---

### Task 31 — Create Megaroast repository 3, the holdout QA repository
**Source:** INT-3 owner answer (repository 3); `AGENTS.md` "Held-out scenarios"
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner. Builder agents never read, clone or ask for its content.
**Change:** The owner creates an empty private repository (`gh repo create Megaroast/<name> --private`). Which repositories the scenarios in it test, and who writes them, is the quality side's decision and is not planned here. No file of this repository is read by any session working on this plan.
**Acceptance:** the owner confirms the URL; it is private. The coder's report states that it did not read it.
**Todo:** [ ]

---

### Task 32 — Create Megaroast repository 4, the example manifold instance
**Source:** INT-3 owner answer (repository 4)
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner.
**Change:** The owner makes a local instance from the example or the starter with the documented route (`./manifold init`, `docs/quickstart.md`; read both before running it, since neither was run for this plan), and creates the private repository from it, for example `gh repo create Megaroast/<name> --private --source=<instance folder> --push` (flags `--source` and `--push` verified in `gh repo create --help`). The instance registers repositories 1 and 2 as components. The creation through the App is INT-6's GitHub part and is not used.
**Acceptance:** the owner confirms the URL; a clone of it has `manifold.yaml` listing two components (Task 33 checks it).
**Todo:** [ ]

---

### Task 33 — Check the example instance from a scratch clone
**Source:** INT-3 S3; INT-2 constraint (tests are offline, so this is a manual check, not a test)
**Files:** none changed; the note goes here (no repository content in it)
**Action:** none (manual check)
**Who:** the owner runs the clone, or the coder after the owner's explicit go-ahead; the clone goes to the scratchpad, outside this repository, and uses the owner's existing login (`gh repo clone Megaroast/<name> <scratch folder>`; no token is read or printed).
**Change:** Start the server against the clone as `docs/quickstart.md` describes (read it first; the exact start command is not recorded here), then call `wiki_health` and `wiki_inventory_tool`. Run `scan.py` (Task 26) with `MANIFOLD_SCAN_TERMS` pointing at the owner's private list over the clone, to learn what a scrub would still have to remove; the findings are counted in the note and never quoted. Do not copy any file from the clone into this repository.
**Acceptance:** the note records the commands, that health reports healthy, the two components listed and the count of scan findings per kind; `git status --short` in this repository is unchanged.
**Todo:** [ ]

---

**Verification:** `cd server && ../.venv/bin/python -m pytest -q` passes with counts; `python3 bundles/base/tools/build.py --check` prints `lint ok` and `.venv/bin/python -m pytest bundles/base/tests -q` still passes (no bundle change in this checkpoint); `git diff --stat` for the checkpoint lists only `server/tests/datasets/`; the owner confirms the four repositories exist with the visibility recorded in `SIGNOFFS.md`.

### CP4 — Release 0.3.1 (INT-27 owner answer)

Placed last because the owner said to release after the work is done. Only CP1 changes shipped files, so the owner may instead take it right after CP1 merges.

### Task 34 — Bump the bundle version to 0.3.1
**Source:** INT-27 Open question "Which release carries this?" (owner: "call the release V0.3.1"); commit `4f8b448` (how 0.3.0 was bumped)
**Files:** `bundles/base/VERSION`
**Action:** MODIFY
**Change:** Replace the single line `0.3.0` by `0.3.1`. Release 0.3.0 changed only `bundles/base/VERSION` and the `version` in `.manifold/manifest.json`, in two commits ("Bump the base bundle", then "Refresh this repository's own install"); do the same. The release workflow (`.github/workflows/release.yml`) fails unless the tag equals `v` plus the content of `bundles/base/VERSION`.
**Acceptance:** `cat bundles/base/VERSION` prints `0.3.1`; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported).
**Todo:** [ ]

---

### Task 35 — Refresh this repository's own install to 0.3.1
**Source:** commit `4f8b448` (second commit)
**Files:** `.manifold/manifest.json` (generated; plus any other file `install.py --status` reports)
**Action:** MODIFY
**Change:** Run the install over this repository as in Task 13 (dry run first, then `--apply` without `--force`) from a build of the new version; do not hand-edit `.manifold/manifest.json`. Commit it separately from Task 34.
**Acceptance:** `.manifold/manifest.json` reads `"version": "0.3.1"`; `install.py --status` reports no modified file.
**Todo:** [ ]

---

### Task 36 — Merge and tag v0.3.1
**Source:** `.github/workflows/release.yml` (trigger: a pushed tag `v*`)
**Files:** none
**Action:** none (outward action)
**Who:** the owner merges the pull request and creates the tag; the coordinator and coder do not tag and do not push a tag. The tag ruleset `protect-release-tags` exists and its rules are unverified (`docs/process/BRANCH_RULES.md`).
**Change:** After the pull request with Tasks 34 and 35 is merged, the owner creates the tag `v0.3.1` on the merge commit and pushes it. The workflow then lints, tests, builds the ZIP and creates the release.
**Acceptance:** the owner confirms the `release` workflow run for `v0.3.1` succeeded and the release lists `manifold-base-*.zip` and `SHA256SUMS` (names as in `release.yml`).
**Todo:** [ ]

---

**Verification:** `git tag` lists `v0.3.1` (run by the owner); `cat bundles/base/VERSION` on the tagged commit prints `0.3.1`.

## Completion checklist
- [ ] All tasks marked [x] by the coder (Tasks 28 to 32 and 36 by the owner's confirmation; Task 33 by the owner's go-ahead)
- [ ] `python3 bundles/base/tools/build.py --check` prints `lint ok`
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` and `cd server && ../.venv/bin/python -m pytest -q` pass clean (no regressions; xfail cases named)
- [ ] No [~] blocked items outstanding
- [ ] No Megaroast content, key, token or secret in any committed file (`git diff` of the phase read for it)
- [ ] Level aimed at: mergeable (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`)
- [ ] Summary note added by the coder below this line

## Open questions

Each has an `Answer:` line for the owner. Where the owner already answered in an intent file, the line quotes it and names the file. Still empty: 3, 6, 10, 12, 16, 17, 18, 19. Decided on delegation, owner may overrule: 7, 8, 9, 15.

1. **Split INT-27 from the server work?** What: do INT-27 (bundle text, CP1) and INT-2/INT-3 (server tests, CP2 and CP3) go in one phase, one pull request, or separately? Why: INT-27 is your current pain and must not wait on, or be held by, a large server review (the review loop allows three runs); the two have different release surfaces. Consequence: one pull request means one long review and a bigger risk of a late finding blocking the small fix; two pull requests cost one more cycle. Recommendation: keep one plan so the intents are reviewed once, but deliver CP1 as its own pull request first and merge it before CP2 starts; if you prefer, CP2 and CP3 move unchanged to `PHASE_5_PLAN.md`. Default: that recommendation.
   Answer: Keep one plan (Michael Hay, 2026-11-13, entered by the coordinator at the owner's instruction in chat: "Keep one plan").
2. **One slug shape for every human field?** What: a single form `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>`, label changed per field. Why: one search finds every unfilled field. Consequence if not: several shapes and gaps in detection. Recommendation and default: one shape (INT-27's recommendation), Mon-DD-YYYY as in your example.
   Answer: Yes (owner, `intent/INT-27-clear-human-instructions-in-the-pr.md`, Open questions: "Yes this is the right format.").
3. **Self-approval in a solo repository.** What: the ruleset requires one approving review and you are the only person. Why: the instruction for the Approve review needs a "if GitHub does not allow it" step, and nothing in the repository says what it is. Consequence: without a decision, the text can only say "stop and ask the owner" (it never claims what GitHub does). Recommendation: Task 1 reads GitHub's documentation and the ruleset first; then you choose to document an existing route (for example a bypass you already hold), a second account, or a ruleset change (your act, out of scope). Default: document what is read and ask.
   Answer:
   Related words of the owner, not an answer to this question (`intent/INT-27-...md`): "If there is more than one reviewer in the repo then it is unlikely a solo repo, otherwise it is a solo repo." They say when a repository counts as solo (this one, per `AGENTS.md` "Review process"); they do not say how the required approving review is met. Still open.
4. **Also cover the plan's **Approved by**, **Amendment approved by**, the test plan's **Approved by** and the intent's `accepted_by`?** What: the same slug and an instructions line (Task 7), and a slug counts as blank for `coder` (Task 8). Why: the same "no prompt" problem stops you at the next human line. Consequence if not: you are stopped again there. Recommendation and default: yes, in this phase.
   Answer: Yes (owner, `intent/INT-27-...md`: "Agree with the recommendation.").
5. **Does an unreplaced `<Insert ...>` count as missing, and do the instructions stay visible?** What: the coordinator and `/phase-status` read a leftover slug as the line being missing, and the instructions are visible text (not HTML comments) that stay in the finished description. Why: otherwise a pull request can look ready with no name. Consequence if not: S6 and S1 of INT-27 fail. Recommendation and default: yes to both.
   Answer: Yes to both (owner, `intent/INT-27-...md`: "Agree with the approach and recommendation" for the leftover slug counting as missing, and "Agree with the recommendation." for visible instructions).
6. **How does `/phase-status` read the pull request description?** What: the script reads repository files only; the description is on GitHub. Options: (a) an optional `--pr-body <file>` holding a saved copy, written by the coordinator or by you; (b) the script calls `gh` itself. Why: INT-27 S6 wants unreplaced slugs listed. Consequence: (b) makes a read-only script depend on `gh` and a network. Recommendation and default: (a).
   Answer:
7. **Contract recording format and place (INT-2).** What: one JSON file per tool and case under `server/tests/contracts/`, normalising commit hashes and timestamps, recorded by an explicit command that refuses to run in CI or under pytest. Why: a change to a recording must be a visible, reviewed diff. Consequence if not: a regenerated file can hide a broken tool. Recommendation and default: this format.
   Answer: Delegated to planning by the owner (`intent/INT-2-test-hardening-and-contracts.md`: "Survey the manifold repo ... the planning should determine how much additional work is required."). Decision after the survey (see "Intent review", INT-2): keep this format; no recording exists today, and the harness reuses `ToolWorld.call`, the `acme` fixture and the tool-set check of `test_tool_policy.py`. The owner may overrule.
8. **Conformance suite: required check or advisory (INT-2)?** What: whether the official MCP conformance run blocks the merge. Why: a flaky required check blocks every pull request, and making it required is a ruleset change that only you make. Consequence: too strict, merges stop; too loose, a protocol break can merge. Recommendation: advisory (non-required job, Task 22) until it has run green on several pull requests; then you decide. Default: advisory, and Task 22 only if Task 14 shows it runs offline.
   Answer: Delegated to planning by the owner (same words, `intent/INT-2-...md`). Decision after the survey: advisory. No conformance run exists in the repository (only the `initialize` call by `curl` in the `image` job of `server.yml`), and the server tests themselves are not required checks today (Concerns 6), so a required conformance check would be stricter than the rest. The owner may overrule.
9. **Coverage gate (INT-2)?** What: whether a coverage percentage blocks the merge. Why: the question is open in the intent; no coverage tool is in `server/requirements-dev.txt`, so adding one changes the locked dependencies. Consequence: a gate with no tool is wishful; adding a tool is a dependency change. Recommendation and default: no coverage gate in this phase; the contract list (every tool has a recording) and the import rule are the gates.
   Answer: Delegated to planning by the owner ("I believe we may already have some rules in the repo so the planner must find out", `intent/INT-2-...md`). Found: no coverage tool, configuration or percentage in `server/requirements-dev.txt`, `server/pytest.ini`, `.github/workflows/*`, `REVIEW.md`, `CONTRIBUTING.md` or `bundles/base/rules/`; the only coverage-related text is the template section "Coverage judgement" (a judgement, not a number) and the rule against committing coverage data. Decision: no coverage gate in this phase. The owner may overrule.
10. **What happens to a write-failure test that exposes a defect (Concerns 1)?** What: for each case where the server leaves a file, folder, sidebar entry or log line after a refused write, do you change the code (a `bug-coder` fix, a behavior change) or narrow INT-2's S3 to what the code promises? Why: git refusing is documented as non-fatal today. Consequence: either way the test must match the decision, and an `xfail` left in place hides it. Recommendation: treat a stray folder, partial file, sidebar entry or log line as defects to fix by `bug-coder` after this phase, and keep "file stays when only the commit fails" as the documented behavior, written down in the test. Default: record each as `xfail(strict=True)` with the reason and ask.
    Answer:
11. **What are small, medium and large (INT-3)?** What: the number of components and pages. Why: tests and demos ask by name. Consequence: the large size affects test run time. Recommendation: small 3 components and about 20 pages, medium 12 and 200, large 50 and 2000, all generated on demand in the test's temporary folder and never committed. Default: that recommendation (and the 20-second limit in Task 26).
    Answer: Superseded by the owner (`intent/INT-3-test-data-sets.md`: "Let's just start with Megaroast for now using 4 repos within the organization."). No sizes are defined in this phase; see Open question 17 for the deferred generator.
12. **Where does the list of terms to scan for live, and may real data ever be fetched (INT-3)?** What: the scan for real names and hosts needs a list, and a list of real names cannot be committed to a public repository. Recommendation: pattern checks in the repository (emails, non-test hosts, token shapes) plus a private list in a file outside the repository, named by `MANIFOLD_SCAN_TERMS`; "fetched" large data sets are not used. Consequence if not: the scan is weak, or it leaks the terms. Default: that recommendation.
    Answer:
13. **Is any real data on offer (INT-3)?** What: will the new company or other products offer real data, and under what terms. Why: the scrub procedure is only written, not used, until someone offers. Consequence: none now; this phase commits synthetic data only. Recommendation and default: no real data in this phase; the rule and scan ship so the first offer has a procedure.
    Answer: Yes, in a form the question did not foresee (owner, `intent/INT-3-...md`: "We can use the Megaroast organization to provide a testbed for external repos."). The rule and scan are therefore used in this phase (Tasks 26, 28, 33). Whether the company permits the derived repositories and whether any of them is public is Open question 16.
14. **Which release carries this?** What: CP1 changes shipped bundle text and so needs a version decision; CP2 and CP3 change no shipped file. Recommendation: you choose the number after CP1 merges (release is out of scope here). Default: no release task in this plan.
    Answer: Release as v0.3.1 after the work is done (owner, `intent/INT-27-...md`: "after we're done with the work we call the release V0.3.1 to signify we're patching the bundle"). CP4 (Tasks 34 to 36) does this; the owner tags.
15. **Decision recorded by the coordinator and planner on the owner's delegation: is the GitHub App (INT-7) pulled into this phase?** The owner left the call to the coordinator and the planner. Read: INT-7, INT-6 (GitHub part), INT-1, INT-14, INT-15, INT-16, and the server source.
    **Facts.** (1) The server makes no GitHub call: `server/tests/test_offline_clean.py` forbids an HTTP client library in the server, and `server/manifold_cli/init_cmd.py` says "No GitHub, no outside request". Git runs as a local subprocess only (`server/wiki_backend/git.py`). (2) The features that would use an App are drafts or unplanned: INT-14 (draft, needs "the App or a personal access token"), INT-15, INT-16, INT-6's GitHub part ("comes after INT-7"). (3) INT-7's own rules: "Every permission has a feature", S1 "Must never: Request a permission that no feature uses", "What an App cannot do ... is verified before any plan relies on it", "One App per company, created by the company", and its open questions (which organization owns it, manifest flow or by hand, organization-owner approval, one App or two) are marked "resolve in planning" and "needs a spike". (4) INT-14's constraint already accepts a personal access token "for a quick start", never stored in the instance repository.
    **Options.** (a) All of INT-7 in this phase: eight scenario seeds, sign-in and device flow, either-rule, revocation; it needs the spike, the INT-1 roles and server code that does not exist, and delays CP2 and CP3, whose purpose is a safety net before server change. Rejected. (b) A thin slice: create the App in Megaroast with only Metadata (read) and install it on the example instance repository; no sign-in, no device flow. It would cover INT-7 S1 (create and install, permissions listed), S3 (remove it, by hand), the "private first" and "name" constraints, and open questions 1, 2 and 6 by spike. It would leave S2 (the server acting as the App: no server code uses it), S4 to S8, the either-rule, the sign-in rule, the revocation promise and the Secrets question. Cost: about six more owner-gated tasks (a spike read, name check, create, install, uninstall test, record) and an App no feature uses, which breaks INT-7's own "every permission has a feature" and "verified before any plan relies on it" for the permissions beyond Metadata. (c) Keep INT-7 out, and give the Megaroast testbed existing means: git and `gh` under the owner's own login, no token read or stored by any agent (Tasks 29 to 33).
    **Decision: (c).** The testbed needs only to create four repositories and clone one; the owner's login does that today (`gh auth status` on this machine shows a keyring login for the owner's account; `gh repo fork --org`, `gh repo create --private --source --push` and `gh repo clone` exist in gh 2.86.0). Nothing in this phase would consume an App. Megaroast stays valuable to INT-7: it is the "first test organization" INT-7 names, so a later INT-7 plan, which should start with its spike, finds it ready. If the owner wants (b), the plan gains a CP5 of about six tasks and Tasks 29 to 33 are unchanged.
    **Unverified, to confirm in INT-7's own spike and not relied on here:** that the name `manifold` is free as a GitHub App name (unverified: confirm on GitHub's App creation page, an owner act); what an App cannot do (approve its own pull requests, create repositories, which permission creating a repository needs: unverified: confirm with GitHub's documentation on App permissions); whether an organization owner must approve the permissions for Megaroast (unverified: confirm with GitHub's documentation on installing an App in an organization).
    Answer (owner, to overrule or confirm):
16. **Real data in the Megaroast repositories.** What: (a) does the company that owns `company_dns` permit a fork and a GUI derived from it in the Megaroast organization, in writing; (b) will each of the four repositories be private; (c) may anything from them ever be copied into this public repository (default: no, nothing). Why: INT-3 forbids real content in a public repository without written permission and a checked scrub; the repositories derive from a company's code. Consequence: without an answer, Tasks 28 to 33 do not start and the rest of the phase goes on. Recommendation: private for all four; permission written in `SIGNOFFS.md` (Task 28); nothing copied here. Default: that.
    Answer:
17. **The sized synthetic generator (INT-3 S1: small, medium, large, same seed gives the same tree).** What: defer it, since the owner chose to start with Megaroast, or keep it as before. Why: S1 is an accepted seed and is not dropped silently; the curated messy and hostile sets (S2) stay either way. Consequence: deferring leaves no large instance for a later performance or store test (INT-4); keeping it adds about three tasks (the old Tasks 23, 25 and 26 in this file at commit `f939205`). Recommendation and default: defer, and add it when INT-4 needs a size.
    Answer:
18. **Names.** What: the exact names of the four Megaroast repositories, and whether the committed `README.md` of Task 26 may name them (default: it names the organization and the four roles, not the repository names). Why: the source repository belongs to a company. Consequence: Task 26 writes roles only until you answer.
    Answer:
19. **Should the server tests become a required check?** What: add `server tests (3.11)` and `server tests (3.12)` of `server.yml` to the ruleset's required checks (a ruleset change, your act on GitHub). Why: today a failing server test does not block a merge (Concerns 6), so CP2's contract tests would be advisory in effect. Consequence: not required, a broken tool can merge; required, a flaky test blocks every pull request. Recommendation: yes, after CP2 has passed on several pull requests. Default: no change in this phase.
    Answer:
