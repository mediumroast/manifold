# PHASE_4_PLAN.md

**Approved by:**
**Source intent:** INT-27 `intent/INT-27-clear-human-instructions-in-the-pr.md`, INT-2 `intent/INT-2-test-hardening-and-contracts.md`, INT-3 `intent/INT-3-test-data-sets.md` (all three still `status: draft`; see "Intent review")

## Objective

A person who has never read the process documents can finish every human step of a coordinator-written pull request from the text in the pull request alone (INT-27). The server's tool behavior is pinned by recorded contract tests, its write and error paths and its import rule are tested, and tests can ask for a small, medium or large synthetic instance, or a curated messy or hostile one, and get the same tree every time (INT-2, INT-3). Phase 5 server work (the content store refactor, INT-4, and later) then has a safety net.

## Intent review

The owner reads each entry, answers its decision line, and the plan is approved only after that. No agent fills these lines.

### INT-27 Tell the human exactly what to do, and where to write, in the pull request
**Asks:** Put visible, numbered **Instructions** next to every human step of the pull request (CI line, ready-check table, ticks, GitHub's Approve review), and one replaceable `<Insert ...>` slug in every place a human writes a name and date, so an unfilled field is found by a script. It never lets an agent fill a human's part.
**Recommendation: accept with changes.** (1) Its scenario S6 asks `/phase-status` to list unreplaced slugs, but that script reads only files in the repository and the pull request description is not one; the plan adds an optional `--pr-body <file>` input (Open question 6). (2) Its self-approval question cannot be answered from the files; Task 1 reads GitHub's documentation first. (3) A `<...>` slug may be hidden by GitHub's Markdown rendering; Task 1 checks (unverified until then).
Intent accepted by: <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>

### INT-2 Test hardening and contract tests for the server
**Asks:** Pin what every MCP tool promises its callers as recorded request/response tests that change only by a reviewed edit, run the official MCP conformance checks, close gaps in write and error paths, and enforce by test that only the entry module imports the web framework.
**Recommendation: accept with changes.** (1) Its scenario S3 ("a failed write leaves the instance clean", including "git refuses") conflicts with what the code documents today: `git_commit` is deliberately non-fatal and the file stays on disk after a refused commit (`server/wiki_backend/write.py`, `git.py`); also `write_page_of_kinds` creates the parent folder before the etag and frontmatter checks. The plan writes the tests, and any test that fails is reported as a defect, not fixed here (Concerns 1). (2) The conformance suite is not read yet (unverified); Task 14 reads it before any CI change. (3) "Python versions the server supports" means 3.11 and 3.12 (`server/requirements.txt`, `.github/workflows/server.yml`).
Intent accepted by: <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>

### INT-3 Test data sets, real and synthetic
**Asks:** A seeded generator for instances of any size, a small set of committed curated instances for awkward and hostile content, and a written rule for when real data may be used and how it is scrubbed.
**Recommendation: accept with changes.** (1) Sizes need numbers (Open question 11); the plan proposes defaults. (2) The only forbidden-terms scan today is for the bundle (`FORBIDDEN_TERMS` in `bundles/base/tools/build.py`); the server data sets need their own scan, and a list of real names cannot itself be committed in a public repository (Open question 12). (3) No real source has been offered, so this phase ships the procedure and the scan and commits only synthetic data.
Intent accepted by: <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>

## Scope

**In scope:**

- CP1 (INT-27): visible **Instructions** and one slug shape in the pull request template, the plan, test-plan and intent templates, `REVIEW_CYCLE.md`, the coordinator and the rule/agent text that reads a blank approval; `/phase-status` reports unreplaced slugs. Both flavors from one source.
- CP2 (INT-2): import-rule test, contract-test harness and recordings for every tool, write-failure and HTTP-error tests, the conformance run (if the owner agrees).
- CP3 (INT-3): generator, curated instances, loader, tests, the real-data rule and scan.

**Out of scope:**

- The content store refactor (INT-4), the GitHub-API store and App (INT-14, INT-7 and the GitHub part of INT-6): they change the server this phase protects, so they follow it.
- INT-24 (review and answer in the UX): needs a UI; INT-27 stays plain text.
- INT-5 (agent harvest) and the rest of the backlog: not needed by the safety net and not started.
- Changing the GitHub ruleset, `.github/workflows/` (except the one optional job in Task 22, with the owner's go-ahead), the release number, releasing.
- Fixing any defect that Tasks 20 and 21 expose: recorded and handed to `bug-coder` after the owner decides (Concerns 1).
- Performance and load tests, a UI, language-model-generated content (INT-2 and INT-3 Out of scope).
- Noticed, not done: `docs/process/BRANCH_RULES.md` records `RepositoryRole` 5 and `require_extra_approval_for_unattributed_changes` as unverified; Task 12 adds only what Task 1 reads.

**Needs from other repositories:** None.

**Provides to other repositories:** Repositories that install the bundle receive the new template, process and agent text and the extended `/phase-status`.

**Constraints:**
INT-27: a human keeps the final say (instructions tell, never do; the coordinator never approves, moves out of draft, merges, ticks or fills a human field); instructions are in the pull request itself, not a link; ready still means reviewed (no ready-check line dropped or loosened); approval follows `AGENTS.md` "Review process" (solo is not made to look like a team); facts are not duplicated (point to `REVIEW_CYCLE.md` "Where each fact is recorded"); shipped text stays generic (`M. Kusanagi` is a neutral placeholder); both flavors from one source, deterministic build, standard library only for any script; concise, numbered, plain words, no bare internal IDs; no outward action without the owner (editing a live pull request, the ruleset, the workflow); no unverified claim about GitHub.
INT-2: no network and no real git remote in tests, finishing in a laptop-tolerable time; recorded responses contain no real data (the fictional example instance only); a change to a recording is a visible, reviewed decision, never automatic; only the entry module imports the web framework, enforced by a test; no flaky tests; tests run on the Python versions the server supports.
INT-3: nothing real enters a public repository without the owner's written permission and a checked scrub (until then only synthetic data); deterministic, same seed gives the same instance byte for byte; small enough to commit, or generated on demand when large; covers dotted and similar slugs, a page with no frontmatter, duplicates, stale pages, very long pages, non-English text and text aimed at an AI; no personal data, not even fake data that looks like a real person's.

## Concerns flagged

1. **INT-2 S3 versus documented behavior.** `git_commit` is non-fatal by design (the file stays when git refuses), and `write_page_of_kinds` runs `file_path.parent.mkdir(...)` before the conflict and frontmatter checks, so a refused write may leave an empty folder. S3 says a refused write leaves "no partial files". Owner decides: (a) keep the code, and narrow S3 to the cases the code already supports, or (b) treat the differences as defects for `bug-coder`. Default: the tests are written to S3 as the intent states it, any failure is recorded and not fixed in this phase, and the owner chooses (a) or (b) per failure.
2. **Split.** INT-27 and INT-2/INT-3 touch different surfaces (bundle text versus server tests) and release differently. See Open question 1.
3. **`<Insert ...>` may not render in GitHub Markdown.** An unknown tag may be hidden in the rendered description (unverified: confirm with GitHub's Markdown documentation or a comment preview, Task 1). If hidden, the slug goes inside a code span and the detector accepts the span; the owner decides at Task 1.
4. **A slug in a plan's Approved by line must still count as blank** for `coder` and `test-coder` and for `/phase-status` (it already treats a `<...>` value as blank). Tasks 8 and 11 make that explicit; if it is missed, a slug would read as an approval.
5. **The conformance suite and CI.** Whether it runs offline against a locally started server, and what runtime it needs, is unread (unverified: confirm with the MCP project documentation, Task 14). Making it a required check is a ruleset change, the owner's act.

## Prerequisites

- [x] Phase 3 merged (`4516792`); release 0.3.0 (`4f8b448`); `bundles/base/VERSION` reads `0.3.0`.
- [x] Project commands known: `AGENTS.md` "Project commands" (read; `pytest` here means the server tests command).
- [ ] The `.venv` exists (`python3 -m venv .venv`, then the install line in `AGENTS.md`; none exists in this worktree).
- [ ] The owner answered the Open questions below, at least 1 to 6 before CP1 and 7 to 10 before CP2 and 11 to 13 before CP3.
- [ ] For Task 1: the owner's go-ahead to read GitHub's documentation and the repository's settings with `gh` (GET only).
- [ ] For Task 22 only: the owner's go-ahead to edit `.github/workflows/server.yml`.

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
| `server/tests/datasets/` (`generate.py`, `curated/`, `loader.py`, `scan.py`, `README.md`, `SIGNOFFS.md`, `test_datasets.py`) | CREATE | INT-3 |

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
**Acceptance:** the note lists, per question (a), (b), (c), the fact and its source or "unverified". The owner then answers Open questions 3 and 5.
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
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` passes (counts reported); `.venv/bin/python bundles/base/scripts/phase_status.py 4` run on this plan lists the three "Intent accepted by" lines (the plan's own **Approved by** line is blank, not a slug) and is read-only (`git status --short` unchanged).
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
**Change:** Read `write_page_of_kinds` and `handoff_create` first to name each failure point. Using `ToolWorld` and monkeypatch, inject: a stale etag; invalid frontmatter; a write refused (`OSError` with `errno.ENOSPC` from `Path.write_text`); git refusing the commit (`git_commit` returning `committed=False`); a failure part-way through `handoff_create`. After each, assert that the tree (relative paths, empty folders and sha256 of every file outside `.git`), `wiki/_sidebar.md` and `wiki/log.md` equal their snapshot from before the call, and that `wiki_health` reports healthy. Where the existing code fails the assertion (Concerns 1), mark the case `pytest.mark.xfail(strict=True, reason="defect: <one line>")` with the reason, so the suite stays green and the defect is listed, and stop to ask the owner; do not edit the code.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/test_write_failures.py -q` passes (counts reported, including the number of xfail cases, each named in the note).
**Todo:** [ ]

---

### Task 21 — Test the HTTP layer's refusals and errors
**Source:** INT-2 Problem (HTTP layer thin)
**Files:** `server/tests/test_http_errors.py` (CREATE)
**Action:** CREATE
**Change:** Use `TestClient(server.asgi_app, base_url="http://127.0.0.1:8686")` as `test_request_guard.py` does. Cases, each with an authenticated principal from `auth_world`: `/mcp` with a malformed JSON body; an unknown tool name; a missing required argument; a wrong argument type; `GET /mcp`; an oversized body. For each assert the status and that the body holds no stack trace, file path or secret.
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

### CP3 — Test data sets (INT-3)

### Task 23 — Create the seeded generator
**Source:** INT-3 S1, Constraints (deterministic, standard library)
**Files:** `server/tests/datasets/generate.py` (CREATE)
**Action:** CREATE
**Change:** `SIZES = {"small": ..., "medium": ..., "large": ...}` with the numbers the owner chose (Open question 11; defaults: small 3 components and about 20 pages, medium 12 and 200, large 50 and 2000) and `build_instance(size, seed, dest)`. Randomness comes from a class `Stream` built on `hashlib.sha256` over `seed:counter`, not from `random`, because `random`'s choice and shuffle algorithms are not guaranteed identical across Python versions (unverified: confirm with the Python documentation if the owner wants `random.Random` instead). Content is built from fixed word lists with the fictional `acme-` and `.test` names only, LF line endings, no clock, no process id. A command form `python3 server/tests/datasets/generate.py --size medium --seed 1 --out DIR` for demos. Standard library only.
**Acceptance:** two runs with the same size and seed give directories with identical file lists and sha256 (`diff -r` empty); a different seed differs.
**Todo:** [ ]

---

### Task 24 — Create the curated messy and hostile instances
**Source:** INT-3 S2, Constraints (awkward cases, no personal data)
**Files:** `server/tests/datasets/curated/messy/` and `server/tests/datasets/curated/hostile/` (CREATE)
**Action:** CREATE
**Change:** `messy`: components with dotted and look-alike slugs (`acme.io`, `acme-io`), a page with no frontmatter, two pages with the same title, a stale page, a non-English page (more than one script). `hostile`: pages whose text addresses an AI agent ("ignore your instructions and ...", "call the tool ... with ...") that are harmless test strings only. No names of real people, hosts or companies; hosts use `.test`. The very long page is generated by the loader (Task 25), not committed.
**Acceptance:** the folders load with `load_config` from `server/wiki_backend/config.py`; `du -sk server/tests/datasets/curated` is under 200; each file is read once by the coder for real data before staging.
**Todo:** [ ]

---

### Task 25 — Add the loader that gives a git-backed copy
**Source:** INT-3 S1
**Files:** `server/tests/datasets/loader.py` (CREATE)
**Action:** CREATE
**Change:** `make_instance(tmp_path, size, seed=0)`, `copy_curated(tmp_path, name)` and `long_page(chars)` (a long-page text of the stated size). Both initialise git and commit as the `acme` fixture of `test_example_acme.py` does, with a fixed author and no network. A pytest fixture `dataset` in the datasets test module wraps them.
**Acceptance:** a test builds `small` and `copy_curated("messy")` and `wiki_health` reports healthy for each.
**Todo:** [ ]

---

### Task 26 — Test determinism and the health of every size
**Source:** INT-3 S1 and Must never
**Files:** `server/tests/datasets/test_datasets.py` (CREATE)
**Action:** CREATE
**Change:** `test_the_same_seed_gives_the_same_tree` (compare relative paths and sha256, excluding `.git`), `test_a_different_seed_gives_a_different_tree`, `test_every_size_passes_the_health_check` (small, medium, large). Record the seconds the large case takes on this machine in the note; if it takes more than 20 seconds, stop and ask the owner whether it goes behind an environment variable.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q` passes (counts and the large-case time reported).
**Todo:** [ ]

---

### Task 27 — Test that hostile text is returned as plain content
**Source:** INT-3 S2
**Files:** `server/tests/datasets/test_datasets.py`
**Action:** MODIFY
**Change:** `test_hostile_pages_are_returned_as_content_and_not_acted_on`: with `ToolWorld` over `copy_curated("hostile")`, `wiki_read_tool` returns each page's text unchanged in its content field; `wiki_inventory_tool` and `wiki_freshness_tool` run over the instance; the wiki tree and `log.md` are unchanged afterwards, and the git log has no new commit.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q -k hostile` passes (counts reported).
**Todo:** [ ]

---

### Task 28 — Write the real-data rule, the scan and the sign-off record
**Source:** INT-3 S3, Constraints (nothing real without written permission and a checked scrub)
**Files:** `server/tests/datasets/README.md`, `server/tests/datasets/SIGNOFFS.md`, `server/tests/datasets/scan.py` (CREATE)
**Action:** CREATE
**Change:** `README.md` holds the sizes, the determinism rule, the awkward cases and the real-data rule: who gives permission (the data's owner, in writing), the scrub steps (names, hosts, secrets, email addresses), the check, and "the original is never committed". `scan.py`: `scan(path)` reports email addresses, hosts not ending in `.test`, `.example` or `.invalid`, strings shaped like tokens or keys, and every term listed in a private term list read from a file outside the repository whose path comes from the environment variable `MANIFOLD_SCAN_TERMS` (Open question 12; nothing real is committed). `SIGNOFFS.md` holds a table with no rows yet (columns: source, owner, permission date, scrub checked by, scan result) and states that no real data is committed. A test in `test_datasets.py`, `test_scan_flags_real_shaped_text_and_passes_the_committed_sets`, feeds `scan` a temporary file with an email address, a non-test host and a token-shaped string, and runs it over the generator output and `curated/`.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q -k scan` passes (counts reported); `scan.py` over `curated/` prints no finding.
**Todo:** [ ]

---

### Task 29 — Test that the set covers the awkward cases and holds no personal data
**Source:** INT-3 Constraints (awkward cases, no personal data)
**Files:** `server/tests/datasets/test_datasets.py`
**Action:** MODIFY
**Change:** `test_the_sets_cover_every_awkward_case` asserts each of dotted slug, look-alike slug, no frontmatter, duplicate title, stale page (through `wiki_freshness`), long page (via `long_page`), non-English text and AI-aimed text is present in `messy`, `hostile` or the generator output; `test_no_set_contains_personal_data` runs `scan` for email addresses and for a first-name-plus-surname pattern list kept in the test, over every committed and generated set.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q` passes (counts reported).
**Todo:** [ ]

---

**Verification:** `cd server && ../.venv/bin/python -m pytest -q` passes with counts; `python3 server/tests/datasets/generate.py --size medium --seed 1 --out <scratch>` run twice gives identical directories (`diff -r`); `python3 bundles/base/tools/build.py --check` prints `lint ok` and `.venv/bin/python -m pytest bundles/base/tests -q` still passes (no bundle change in this checkpoint).

## Completion checklist
- [ ] All tasks marked [x] by the coder
- [ ] `python3 bundles/base/tools/build.py --check` prints `lint ok`
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` and `cd server && ../.venv/bin/python -m pytest -q` pass clean (no regressions; xfail cases named)
- [ ] No [~] blocked items outstanding
- [ ] Level aimed at: mergeable (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`)
- [ ] Summary note added by the coder below this line

## Open questions

Each has an empty `Answer:` line for the owner. "accept all" settles every default.

1. **Split INT-27 from the server work?** What: do INT-27 (bundle text, CP1) and INT-2/INT-3 (server tests, CP2 and CP3) go in one phase, one pull request, or separately? Why: INT-27 is your current pain and must not wait on, or be held by, a large server review (the review loop allows three runs); the two have different release surfaces. Consequence: one pull request means one long review and a bigger risk of a late finding blocking the small fix; two pull requests cost one more cycle. Recommendation: keep one plan so the intents are reviewed once, but deliver CP1 as its own pull request first and merge it before CP2 starts; if you prefer, CP2 and CP3 move unchanged to `PHASE_5_PLAN.md`. Default: that recommendation.
   Answer:
2. **One slug shape for every human field?** What: a single form `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>`, label changed per field. Why: one search finds every unfilled field. Consequence if not: several shapes and gaps in detection. Recommendation and default: one shape (INT-27's recommendation), Mon-DD-YYYY as in your example.
   Answer:
3. **Self-approval in a solo repository.** What: the ruleset requires one approving review and you are the only person. Why: the instruction for the Approve review needs a "if GitHub does not allow it" step, and nothing in the repository says what it is. Consequence: without a decision, the text can only say "stop and ask the owner" (it never claims what GitHub does). Recommendation: Task 1 reads GitHub's documentation and the ruleset first; then you choose to document an existing route (for example a bypass you already hold), a second account, or a ruleset change (your act, out of scope). Default: document what is read and ask.
   Answer:
4. **Also cover the plan's **Approved by**, **Amendment approved by**, the test plan's **Approved by** and the intent's `accepted_by`?** What: the same slug and an instructions line (Task 7), and a slug counts as blank for `coder` (Task 8). Why: the same "no prompt" problem stops you at the next human line. Consequence if not: you are stopped again there. Recommendation and default: yes, in this phase.
   Answer:
5. **Does an unreplaced `<Insert ...>` count as missing, and do the instructions stay visible?** What: the coordinator and `/phase-status` read a leftover slug as the line being missing, and the instructions are visible text (not HTML comments) that stay in the finished description. Why: otherwise a pull request can look ready with no name. Consequence if not: S6 and S1 of INT-27 fail. Recommendation and default: yes to both.
   Answer:
6. **How does `/phase-status` read the pull request description?** What: the script reads repository files only; the description is on GitHub. Options: (a) an optional `--pr-body <file>` holding a saved copy, written by the coordinator or by you; (b) the script calls `gh` itself. Why: INT-27 S6 wants unreplaced slugs listed. Consequence: (b) makes a read-only script depend on `gh` and a network. Recommendation and default: (a).
   Answer:
7. **Contract recording format and place (INT-2).** What: one JSON file per tool and case under `server/tests/contracts/`, normalising commit hashes and timestamps, recorded by an explicit command that refuses to run in CI or under pytest. Why: a change to a recording must be a visible, reviewed diff. Consequence if not: a regenerated file can hide a broken tool. Recommendation and default: this format.
   Answer:
8. **Conformance suite: required check or advisory (INT-2)?** What: whether the official MCP conformance run blocks the merge. Why: a flaky required check blocks every pull request, and making it required is a ruleset change that only you make. Consequence: too strict, merges stop; too loose, a protocol break can merge. Recommendation: advisory (non-required job, Task 22) until it has run green on several pull requests; then you decide. Default: advisory, and Task 22 only if Task 14 shows it runs offline.
   Answer:
9. **Coverage gate (INT-2)?** What: whether a coverage percentage blocks the merge. Why: the question is open in the intent; no coverage tool is in `server/requirements-dev.txt`, so adding one changes the locked dependencies. Consequence: a gate with no tool is wishful; adding a tool is a dependency change. Recommendation and default: no coverage gate in this phase; the contract list (every tool has a recording) and the import rule are the gates.
   Answer:
10. **What happens to a write-failure test that exposes a defect (Concerns 1)?** What: for each case where the server leaves a file, folder, sidebar entry or log line after a refused write, do you change the code (a `bug-coder` fix, a behavior change) or narrow INT-2's S3 to what the code promises? Why: git refusing is documented as non-fatal today. Consequence: either way the test must match the decision, and an `xfail` left in place hides it. Recommendation: treat a stray folder, partial file, sidebar entry or log line as defects to fix by `bug-coder` after this phase, and keep "file stays when only the commit fails" as the documented behavior, written down in the test. Default: record each as `xfail(strict=True)` with the reason and ask.
    Answer:
11. **What are small, medium and large (INT-3)?** What: the number of components and pages. Why: tests and demos ask by name. Consequence: the large size affects test run time. Recommendation: small 3 components and about 20 pages, medium 12 and 200, large 50 and 2000, all generated on demand in the test's temporary folder and never committed. Default: that recommendation (and the 20-second limit in Task 26).
    Answer:
12. **Where does the list of terms to scan for live, and may real data ever be fetched (INT-3)?** What: the scan for real names and hosts needs a list, and a list of real names cannot be committed to a public repository. Recommendation: pattern checks in the repository (emails, non-test hosts, token shapes) plus a private list in a file outside the repository, named by `MANIFOLD_SCAN_TERMS`; "fetched" large data sets are not used. Consequence if not: the scan is weak, or it leaks the terms. Default: that recommendation.
    Answer:
13. **Is any real data on offer (INT-3)?** What: will the new company or other products offer real data, and under what terms. Why: the scrub procedure is only written, not used, until someone offers. Consequence: none now; this phase commits synthetic data only. Recommendation and default: no real data in this phase; the rule and scan ship so the first offer has a procedure.
    Answer:
14. **Which release carries this?** What: CP1 changes shipped bundle text and so needs a version decision; CP2 and CP3 change no shipped file. Recommendation: you choose the number after CP1 merges (release is out of scope here). Default: no release task in this plan.
    Answer:
