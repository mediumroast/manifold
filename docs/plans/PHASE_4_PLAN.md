# PHASE_4_PLAN.md

**Approved by:** Michael Hay on Nov 14, 2026
**Source intent:** INT-27 `intent/INT-27-clear-human-instructions-in-the-pr.md`, INT-2 `intent/INT-2-test-hardening-and-contracts.md`, INT-3 `intent/INT-3-test-data-sets.md` (all three `status: accepted`, `accepted_by: Michael Hay on Nov 14, 2026`; see "Intent review"). INT-7 `intent/INT-7-github-app.md` (`status: accepted`, `accepted_by: Michael Hay 2026-11-01`) is pulled in as a thin slice only, by the owner's decision on Nov 14, 2026 (Open question 15, option (b)); see "Intent review".

## Objective

A person who has never read the process documents can finish every human step of a coordinator-written pull request from the text in the pull request alone (INT-27). The server's tool behavior is pinned by recorded contract tests, the write and error paths that are not yet tested are tested, and the import rule is enforced by a test (INT-2). A curated messy and a curated hostile instance are committed, a real-data rule and scan exist, and an external test organization (Megaroast, four repositories that already exist) is checked and recorded as the real-shaped testbed (INT-3), and a private GitHub App named `manifold` is created in it by the owner with only the permissions this phase uses, installed on the Megaroast test repositories, and shown to mint short-lived installation tokens (thin slice of INT-7). The bundle is then released as v0.3.1 (INT-27 owner answer). Phase 5 server work (the content store refactor, INT-4, and later) then has a safety net.

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

| Question                  | Found                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             | Decision (owner may overrule)                                                                                    |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- |
| Recorded contracts        | No recording, snapshot or golden file in `server/tests` (searched for those words). Every tool is exercised by behavior tests (`test_tool_policy.py` lists valid arguments for each of the 16 tools, `test_tool_authz.py`, `test_handoff_*.py`, `test_onboarding.py`, `test_example_acme.py`), but `wiki_export_helper_tool` and `wiki_list_helpers_tool` appear only in `test_tool_policy.py` (who may call them, not what they return). Reusable: `ToolWorld.call` in `server/tests/conftest.py`, the `acme` fixture in `test_example_acme.py`, the tool set equality in `test_tool_policy.py`. | The harness and recordings are needed (S1); the work stays, built on those three patterns (Open question 7).     |
| Import rule               | Only `server/server.py` imports `fastmcp` or `starlette` (searched `server/`). No test enforces it; `test_offline_clean.py` has the AST scan to copy but covers only HTTP clients.                                                                                                                                                                                                                                                                                                                                                                                                                | A small test is needed (S4), Task 15.                                                                            |
| Failed-write tests        | Stale etag (`test_pickup_stale_etag_rejected`) and bad frontmatter (`test_write_validation.py`) are tested for refusal. No test injects a full disk or a git refusal, or checks that the tree, sidebar and log are unchanged afterwards.                                                                                                                                                                                                                                                                                                                                                          | Task 20 stays, narrowed to the missing cases.                                                                    |
| HTTP errors               | Host, origin and 401, 403, 421 refusals are covered (`test_request_guard.py`, `test_auth*.py`, `test_docs_route_policy.py`); `/ingest` traversal returns 400 (`test_server_smoke.py`). Nothing for malformed JSON, an unknown tool, a missing or wrong-typed argument, `GET /mcp` or an oversized body.                                                                                                                                                                                                                                                                                           | Task 21 stays, only for those cases.                                                                             |
| Conformance suite         | No conformance run anywhere. `server.yml` job `image` checks only an `initialize` call by `curl`. Not read yet: whether the official suite can run offline (unverified until Task 14).                                                                                                                                                                                                                                                                                                                                                                                                            | Advisory, and only if Task 14 shows it runs offline (Open question 8).                                           |
| Coverage gate             | No coverage tool or percentage anywhere: not in `server/requirements-dev.txt`, `.github/workflows/*`, `REVIEW.md`, `CONTRIBUTING.md`. The only coverage text is the template section "Coverage judgement" (a judgement of cases, not a number), and the rule `no-generated-artifacts-in-commits` (do not commit coverage data). The "thresholds" in `SATISFACTION_REPORT_TEMPLATE.md` belong to the quality side.                                                                                                                                                                                 | No percentage gate. The gates are "every registered tool has a recording" and the import rule (Open question 9). |
| What blocks a merge today | Required checks are only `test (3.10)` and `test (3.12)` of `ci.yml`, the bundle tests (`docs/process/BRANCH_RULES.md`). The `server.yml` jobs are not required, so a failing server test does not block a merge.                                                                                                                                                                                                                                                                                                                                                                                 | Concerns 6 and Open question 19; the ruleset is the owner's act.                                                 |

**Plan changes:** (1) Its scenario S3 ("a failed write leaves the instance clean", including "git refuses") conflicts with what the code documents today: `git_commit` is deliberately non-fatal and the file stays on disk after a refused commit (`server/wiki_backend/write.py`, `git.py`); also `write_page_of_kinds` creates the parent folder before the etag and frontmatter checks. The plan writes the tests, and any test that fails is reported as a defect, not fixed here (Concerns 1). (2) The conformance suite is not read yet (unverified); Task 14 reads it before any CI change. (3) "Python versions the server supports" means 3.11 and 3.12 (`server/requirements.txt`, `.github/workflows/server.yml`).
Intent accepted by: Michael Hay on Nov 14, 2026 (recorded in the intent file's `accepted_by`)

### INT-3 Test data sets, real and synthetic

**Asks:** A seeded generator for instances of any size, a small set of committed curated instances for awkward and hostile content, and a written rule for when real data may be used and how it is scrubbed.
**Owner's answers (in the intent file):** use the external test organization Megaroast as the testbed, with four repositories: (1) a fork of the company's `company_dns`, (2) a new repository that pulls the GUI out of `company_dns` as a standalone, (3) a holdout QA repository, (4) an example manifold repository; consider a simple GitHub App; sizes and committed-versus-generated are "start with Megaroast, see above".
**Plan changes:** (1) The sized generator is deferred (Open question 17); the curated messy and hostile instances stay because S2 and the awkward-case constraint do not depend on size. (2) The Megaroast repositories derive from the owner's company repository, so the real-data rule is now used, not only written: nothing from them enters this repository, and the permission and visibility are the owner's decisions (Open question 16). (3) The only forbidden-terms scan today is for the bundle (`FORBIDDEN_TERMS` in `bundles/base/tools/build.py`); the data sets need their own scan, and a list of real names cannot itself be committed in a public repository (Open question 12). (4) The four Megaroast repositories already exist (owner's statement, Nov 14, 2026), so the creation tasks became confirmation tasks (CP4). (5) The GitHub App is a thin slice (CP5, below).
Intent accepted by: Michael Hay on Nov 14, 2026 (recorded in the intent file's `accepted_by`)

### INT-7 A GitHub App named manifold (thin slice only)

**Asks (whole intent):** a private GitHub App `manifold` with only needed permissions, short-lived tokens, attributable actions, removable; later sign-in (device flow, browser), either-rule for components, revocation timing.
**Owner's decision:** on Nov 14, 2026 the owner overruled the earlier recorded decision to keep INT-7 out (Open question 15) and pulled in "a thin slice" because the Megaroast repositories already exist and the work should not be thrown away; the owner states the name `manifold` is available in the Megaroast organization, which the owner owns.
**The slice (CP5):** the owner creates the private App in Megaroast, installs it on the Megaroast test repositories, and mints a short-lived installation token by hand with only the permissions Phase 4 uses (Metadata read, Task 35). No server code calls GitHub and no key reaches the server in this phase.
**Seed mapping:**

| INT-7 seed                                     | In this phase                                                                                                                                                                                                                                                                        |
| ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| S1 Create and install                          | Tasks 33, 34 (settings page shows only the listed permission; installed only on selected Megaroast repositories). Must never "a permission no feature uses": Task 33 acceptance.                                                                                                     |
| S2 Act as the App                              | Partly: Task 35 (owner mints a token, makes one read call, the token expires after one hour per GitHub's documentation). Must never "key or token in a log or the instance repository": Tasks 33, 36. The server acting as the App is deferred (owner confirmed, Open question 20). |
| S3 Remove it                                   | Deferred (owner confirmed, Open question 20): uninstalling would remove the testbed's App; the server has no GitHub code to report "access gone".                                                                                                                                   |
| S4 Sign in from the command line               | Deferred (owner confirmed, Open question 20).                                                                                                                                                                                                                                                          |
| S5 Either a grant or repository write          | Deferred (owner confirmed, Open question 20).                                                                                                                                                                                                                                                          |
| S6 Repository the App cannot see               | Deferred (owner confirmed, Open question 20).                                                                                                                                                                                                                                                          |
| S7 Access lost on GitHub, within a stated time | Deferred (owner confirmed, Open question 20).                                                                                                                                                                                                                                                          |
| S8 Claude Desktop is a known gap               | Deferred (owner confirmed, Open question 20; a guide, no feature yet).                                                                                                                                                                                                                                |

**Constraints covered:** least privilege and "every permission has a feature" (Task 33); private first (Task 33); no long-lived secret in a repository and the key outside it (Tasks 33, 36); short-lived tokens only (Task 35); the name (the owner's statement, confirmed at creation, Task 33); "what an App cannot do verified before a plan relies on it" (only what the slice uses is read, Task 32; the rest stays unverified); the key never held by an agent (all tasks). **Deferred:** one App per company created by the company (the slice App belongs to the test organization only), identity and automation settings split, sign-in rule and lifetime, either-rule, protected mapping, revocation promise, no GitHub token kept, Secrets (write).
**INT-7 open questions:** (1) owner of the first App: Megaroast (owner's statement); whether ownership can be transferred later is unverified: confirm with GitHub's documentation. (2) Manifest flow versus by hand: the slice goes by hand through the settings page; the manifest flow is deferred. (3) Organization-owner approval: the owner owns Megaroast, so none blocks this slice; the question stays open for a company organization. (4), (5): deferred. (6) Secrets (write): no.
Intent accepted by: Michael Hay on Nov 1, 2026 (recorded in the intent file's `accepted_by`)

## Scope

**In scope:**

- CP1 (INT-27): visible **Instructions** and one slug shape in the pull request template, the plan, test-plan and intent templates, `REVIEW_CYCLE.md`, the coordinator and the rule/agent text that reads a blank approval; `/phase-status` reports unreplaced slugs. Both flavors from one source.
- CP2 (INT-2): import-rule test, contract-test harness and recordings for every tool, the missing write-failure and HTTP-error tests, the conformance run (if the owner agrees).
- CP3 (INT-3): curated messy and hostile instances with a loader and tests, the real-data rule, scan and sign-off record.
- CP4 (INT-3): the Megaroast testbed: the owner confirms the four existing repositories, their visibility and that the holdout QA repository is untouched; the example instance is checked from a scratch clone.
- CP5 (INT-7 thin slice): the owner creates the private App `manifold` in Megaroast, installs it on the test repositories and mints one short-lived installation token by hand; the scan learns key and token shapes. Placed after CP4 because the installation needs the confirmed repository list and the owner's answer on permission and visibility (Open question 16, answered: permission given, all repositories private this phase) before an App is installed on repositories derived from a company's code; nothing in CP4 needs the App (the owner's answer is Metadata read only, Open question 21). No server code, bundle file or dependency changes.
- CP6 (release): the bundle version becomes 0.3.1 and the owner tags it. The thin slice changes no shipped file, so 0.3.1 carries only CP1.

**Out of scope:**

- The content store refactor (INT-4) and the GitHub-API store (INT-14): they change the server this phase protects, so they follow it.
- The rest of INT-7 beyond the thin slice: browser or device-flow sign-in, the sign-in rule and lifetime, the either-rule for components, the protected mapping, revocation and re-check timing, the manifest flow, one App per company, Secrets (write), removing the App (S3), and any server code that uses the App or holds its key. Listed per seed in "Intent review"; owner confirmed (Open question 20).
- The GitHub part of INT-6 (creating the instance repository through the App) and INT-14, INT-15, INT-16: no Phase 4 task needs Contents or Pull requests permission, so the App does not request them.
- A helper that mints installation tokens (Task 35 is a manual owner act): deferred to the INT-7 phase that gives the server the key. Python's standard library cannot sign an RS256 token, and the server must not gain a runtime dependency; the later plan decides between a subprocess to `openssl` and a locked dependency.
- The work inside the Megaroast repositories (extracting the GUI from `company_dns`, the holdout scenarios, the example instance's content): it belongs in those repositories under their own plans. This plan only needs the four repositories to exist.
- The sized synthetic generator of INT-3 S1 (small, medium, large): deferred (owner confirmed, Open question 17). Its tasks are in this file at commit `f939205` (old Tasks 23, 25 and 26).
- INT-24 (review and answer in the UX): needs a UI; INT-27 stays plain text.
- INT-5 (agent harvest) and the rest of the backlog: not needed by the safety net and not started.
- Changing the GitHub ruleset, `.github/workflows/` (except the one optional job in Task 22, with the owner's go-ahead), and making the server tests a required check (Concerns 6).
- Fixing any defect that Tasks 20 and 21 expose: recorded and handed to `bug-coder` after the owner decides (Concerns 1).
- Performance and load tests, a UI, language-model-generated content (INT-2 and INT-3 Out of scope).
- Noticed, not done: `docs/process/BRANCH_RULES.md` records `RepositoryRole` 5 and `require_extra_approval_for_unattributed_changes` as unverified; Task 12 adds only what Task 1 reads.

**Needs from other repositories:** The four Megaroast repositories already exist (owner's statement); CP4 (Tasks 29 to 31) confirms them before Task 34 installs the App on them, and the owner's `manifold` App creation in the Megaroast organization (Task 33) before Task 35.

**Provides to other repositories:** Repositories that install the bundle receive the new template, process and agent text and the extended `/phase-status`, as release 0.3.1. Megaroast gets the first `manifold` App, so a later INT-7 plan starts with an organization and an App that exist.

**Constraints:**
INT-27: a human keeps the final say (instructions tell, never do; the coordinator never approves, moves out of draft, merges, ticks or fills a human field); instructions are in the pull request itself, not a link; ready still means reviewed (no ready-check line dropped or loosened); approval follows `AGENTS.md` "Review process" (solo is not made to look like a team); facts are not duplicated (point to `REVIEW_CYCLE.md` "Where each fact is recorded"); shipped text stays generic (`M. Kusanagi` is a neutral placeholder); both flavors from one source, deterministic build, standard library only for any script; concise, numbered, plain words, no bare internal IDs; no outward action without the owner (editing a live pull request, the ruleset, the workflow); no unverified claim about GitHub.
INT-2: no network and no real git remote in tests, finishing in a laptop-tolerable time; recorded responses contain no real data (the fictional example instance only); a change to a recording is a visible, reviewed decision, never automatic; only the entry module imports the web framework, enforced by a test; no flaky tests; tests run on the Python versions the server supports.
INT-3: nothing real enters a public repository without the owner's written permission and a checked scrub (until then only synthetic data); deterministic, same seed gives the same instance byte for byte (applies if the generator is kept); small enough to commit, or generated on demand when large; covers dotted and similar slugs, a page with no frontmatter, duplicates, stale pages, very long pages, non-English text and text aimed at an AI; no personal data, not even fake data that looks like a real person's.
INT-7 (applies to the thin slice): least privilege, each permission listed with the feature that needs it, none without a feature; private first, not published to the marketplace and not installable by others; no long-lived secret in the instance repository, the private key kept outside it and read from the environment or a secret file; short-lived tokens only, nothing caches them past expiry; the name `manifold` available to the owner (here the owner's statement, confirmed at creation) or a fallback chosen before anything is built; what an App cannot do is verified before any plan relies on it; the App's private key stays with its owner and agents never hold it; GitHub.com only. Owner's rule for this plan: the owner creates the App, installs it and handles the key and every token; no agent reads, prints, holds or stores either, and neither is ever written to a committed file, chat or a log.

## Concerns flagged

1. **INT-2 S3 versus documented behavior.** `git_commit` is non-fatal by design (the file stays when git refuses), and `write_page_of_kinds` runs `file_path.parent.mkdir(...)` before the conflict and frontmatter checks, so a refused write may leave an empty folder. S3 says a refused write leaves "no partial files". Owner decides: (a) keep the code, and narrow S3 to the cases the code already supports, or (b) treat the differences as defects for `bug-coder`. Decided by the owner (Open question 10): "file stays when only the commit fails" is the documented behavior and the test says so; a stray folder, partial file, sidebar entry or log line is a defect for `bug-coder` after this phase. Task 20 records each such case as `xfail(strict=True)` with the reason and fixes no code here.
2. **Split (settled).** INT-27 and INT-2/INT-3 touch different surfaces. The owner chose one plan (Open question 1); CP1 is delivered as its own pull request first, and CP2 and CP3 follow in later pull requests.
3. **`<Insert ...>` may not render in GitHub Markdown.** An unknown tag may be hidden in the rendered description (unverified: confirm with GitHub's Markdown documentation or a comment preview, Task 1). If hidden, the slug goes inside a code span and the detector accepts the span; the owner decides at Task 1.
4. **A slug in a plan's Approved by line must still count as blank** for `coder` and `test-coder` and for `/phase-status` (it already treats a `<...>` value as blank). Tasks 8 and 11 make that explicit; if it is missed, a slug would read as an approval.
5. **The conformance suite and CI.** Whether it runs offline against a locally started server, and what runtime it needs, is unread (unverified: confirm with the MCP project documentation, Task 14). Making it a required check is a ruleset change, the owner's act.
6. **The server tests do not block a merge today.** The required checks are only `test (3.10)` and `test (3.12)` from `ci.yml` (the bundle tests); the `server.yml` jobs are not required (`docs/process/BRANCH_RULES.md`). INT-2 S2 says a conformance failure "blocks the merge", and the contract tests of CP2 would not block one either. Making them required is the owner's act on GitHub, out of scope here (Open question 19).
7. **Real data in the Megaroast repositories.** They derive from the owner's company repository. INT-3 forbids real content in a public repository without the owner's written permission and a checked scrub. The owner answered (Open question 16): the owner owns the repositories personally and gives permission, and all stay private in this phase. The repositories already exist; nothing from them is committed here and no test reads them. The Task 28 rows are still the owner's to write (the coder fills none); part (c), copying anything from them here, stays "nothing". The owner plans to make the repositories public at V1; if the holdout QA repository goes public it stops being held out, and the INT-3 scrub rule applies first. That is out of scope for this phase.
8. **The holdout QA repository.** `AGENTS.md` "Held-out scenarios": builders do not read, copy or ask for the quality side's scenarios. Task 30 therefore has the owner confirm it is untouched by builders, and no builder agent session in this repository clones or reads it. The App (Task 34) is not installed on it, so no token from this phase can reach it.
9. **INT-7 is a thin slice** (Open question 15, overruled by the owner). Risks: (a) creating an App in the Megaroast organization needs the owner to be an organization owner or an app manager (GitHub's registration documentation, read Nov 14, 2026); the owner states they own the organization, not yet observed. (b) The private key is the one secret of the phase; it is generated by GitHub at creation, downloaded by the owner, and kept outside every repository. If it is exposed, the owner revokes it in the App's settings and generates a new one (unverified: confirm with GitHub's documentation, Task 32). (c) The name `manifold` is unique across GitHub (documentation): availability rests only on the owner's statement and is confirmed or refused at creation (Task 33); if refused, the owner picks a fallback and the plan's text is amended. (d) An App no Phase 4 feature consumes strains INT-7's "every permission has a feature": the slice requests Metadata read only, and the feature that uses it is Task 35's verification and Task 34's check of the installed repository list (Open question 21 on Contents read). (e) Deferred seeds are listed in "Intent review" and are not silently dropped.

## Prerequisites

- [x] Phase 3 merged (`4516792`); release 0.3.0 (`4f8b448`); `bundles/base/VERSION` reads `0.3.0`.
- [x] Project commands known: `AGENTS.md` "Project commands" (read; `pytest` here means the server tests command).
- [ ] The `.venv` exists (`python3 -m venv .venv`, then the install line in `AGENTS.md`; none exists in this worktree).
- [ ] The owner answered the Open questions still empty: 3 and 6 before CP1 (Tasks 5, 11, 12); 19 has a default (no change) and blocks nothing. Open question 18 is answered in part: permission to name the repositories is given, no names are supplied; until the owner supplies them, Task 26 writes the organization name and the four roles only.
- [ ] For Task 31: the owner's private excluded-terms file exists at `~/.manifold/excluded_terms.json` (a JSON list of strings, written by the owner; never committed, never printed). Owner decision in chat, 2026-11-14: this location replaces the earlier environment variable.
- [ ] For Task 1: the owner's go-ahead to read GitHub's documentation and the repository's settings with `gh` (GET only).
- [ ] For Task 22 only: the owner's go-ahead to edit `.github/workflows/server.yml`.
- [ ] For Tasks 29 to 31 and 33 to 35 (owner acts in the Megaroast organization, with the owner's own GitHub login): the owner's go-ahead for each task. No agent reads, prints or stores a token or the App's private key; `gh auth token` is not run; no key or token is written to the repository or to chat. The owner keeps the key outside every repository, in a secret file whose path is held in the environment variable `MANIFOLD_APP_KEY_FILE` (name only; chosen here, used by no code).
- [ ] CP1 is its own pull request and is merged before CP2 starts (Open question 1).

## File inventory

| Path                                                                                                                                             | Action                      | Reason                                                                                  |
| ------------------------------------------------------------------------------------------------------------------------------------------------ | --------------------------- | --------------------------------------------------------------------------------------- |
| `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, `docs/templates/PULL_REQUEST_TEMPLATE.md`                                                     | MODIFY                      | instructions, slugs, state values (the two copies stay identical)                       |
| `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`, `PHASE_TEST_PLAN_TEMPLATE.md`, `INTENT_TEMPLATE.md` and their `docs/templates/` copies          | MODIFY                      | slug and instructions on the human lines (if Open question 4 is yes)                    |
| `bundles/base/process/REVIEW_CYCLE.md` and `docs/process/REVIEW_CYCLE.md`                                                                        | MODIFY                      | slug rule, Approve review, ready check                                                  |
| `bundles/base/agents/coordinator.agent.md`, `coder.agent.md`, `test-coder.agent.md`, `bundles/base/rules/core/approved-plan-before-execution.md` | MODIFY                      | CI line shape, never fill a slug, a slug is blank                                       |
| `bundles/base/scripts/phase_status.py`, `bundles/base/commands/phase-status.md`, `phase-status.prompt.md`                                        | MODIFY                      | report unreplaced slugs, `--pr-body`                                                    |
| `bundles/base/tests/test_bundle.py`, `bundles/base/tests/test_phase_status.py`                                                                   | MODIFY                      | tests next to each change                                                               |
| `docs/process/BRANCH_RULES.md`                                                                                                                   | MODIFY                      | the Approve review facts read in Task 1 (not shipped)                                   |
| `.claude/agents/*`, `.claude/commands/phase-status.md`, `.manifold/*`, `docs/process/*`, `docs/templates/*`, `AGENTS.md` managed block           | MODIFY                      | refresh of this repository's own install (generated by `install.py`)                    |
| `server/tests/test_import_rule.py`                                                                                                               | CREATE                      | INT-2 S4                                                                                |
| `server/tests/contracts/` (`harness.py`, `record.py`, `test_tool_contracts.py`, `test_harness.py`, `<tool>.json` files)                          | CREATE                      | INT-2 S1                                                                                |
| `server/tests/test_write_failures.py`, `server/tests/test_http_errors.py`                                                                        | CREATE                      | INT-2 S3 and the HTTP layer                                                             |
| `.github/workflows/server.yml`                                                                                                                   | MODIFY                      | optional advisory conformance job (Task 22)                                             |
| `server/tests/datasets/` (`curated/`, `loader.py`, `scan.py`, `README.md`, `SIGNOFFS.md`, `test_datasets.py`)                                    | CREATE                      | INT-3 (no generator: Open question 17)                                                  |
| `server/tests/datasets/scan.py`, `README.md`, `test_datasets.py`                                                                                 | MODIFY                      | private-key and token shapes, App facts without secrets (Tasks 36, 37)                  |
| `bundles/base/VERSION`, `.manifold/manifest.json`                                                                                                | MODIFY                      | release 0.3.1 (Tasks 38, 39), as in `4f8b448`                                           |
| Megaroast repositories 1 to 4 and the `manifold` App (outside this repository)                                                                   | exist / CREATE by the owner | INT-3 testbed and INT-7 slice; nothing from them, no key and no token is committed here |

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
**Todo:** [x]

> Note (read 2026-11-14; owner's go-ahead: `gh` GET only, and public documentation pages):
> - (a) Author approval. Fact: "Pull request authors cannot approve their own pull requests." Source: https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/approving-a-pull-request-with-required-reviews (fetched through the WebFetch tool, which summarizes the page; the quoted sentence is the tool's quote). The page says approvals from "people with write or admin permissions" count toward merge requirements and Copilot reviews do not. What the "Review changes" control shows or whether it is disabled for the author: not stated on that page; unverified: confirm with the pull request page itself (the owner opens it on a pull request they authored).
> - (b) Ruleset. Command: `gh api --method GET repos/mediumroast/manifold/rulesets/26275761` (GET, read-only). Result: `protect-main`, enforcement `active`; rule `pull_request` with `required_approving_review_count: 1`, `dismiss_stale_reviews_on_push: true`, `require_code_owner_review: false`, `require_last_push_approval: false`, `required_review_thread_resolution: true`, `require_extra_approval_for_unattributed_changes: true`, `allowed_merge_methods: ["squash"]`, `required_reviewers: []`; `bypass_actors`: `OrganizationAdmin` (`pull_request`) and `RepositoryRole` 5 (`pull_request`); `current_user_can_bypass: "pull_requests_only"` (for the signed-in `gh` user). Same values as `docs/process/BRANCH_RULES.md` (updated 2026-11-11T05:57:53.911-08:00). What `RepositoryRole` 5 and `require_extra_approval_for_unattributed_changes` mean: still unverified. Whether `current_user_can_bypass` lets the owner merge their own pull request without an approving review: unverified: confirm with the GitHub documentation on rulesets bypass, or the pull request page.
> - (c) Slug rendering. Source: https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax (same tool). Fact: HTML comments are hidden; the page names a few supported tags; it does not say what happens to an unknown tag such as `<Insert ...>`, and it does not say whether backticks stop a tag being interpreted (it says text in backticks "will not be formatted"). Whether `<Insert ...>` shows in the rendered description: unverified: confirm in a comment preview (the owner pastes it, not posted). Until then Concerns 3 stays open.
> - Open question 3 (self-approval route) is the owner's choice after this read. Nothing was chosen here.

---

### Task 2 — Add the slug rule and the Approve review to the review cycle

**Source:** INT-27 S3, S5, S6, S7; "Facts are not duplicated"
**Files:** `bundles/base/process/REVIEW_CYCLE.md`
**Action:** MODIFY
**Change:** Add a section "Human fields and slugs" before "The ready check": the one slug shape `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>` (written out with the real example `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>`; the detection pattern is `<Insert [^<>]*>`); the human replaces the whole slug, brackets included; an agent never replaces one; a human field still holding a slug is missing, never met. Add a row "GitHub's Approve review" to "Where each fact is recorded" (a separate act in GitHub's "Review changes" control, not a row or tick of the description; who writes it: a human). In "The ready check" item 4 add one sentence that the Approve review is separate from the description's ticks and that nothing in the description satisfies it. Do not drop or loosen any ready-check line.
**Acceptance:** `grep -n "Human fields and slugs\|Approve review" bundles/base/process/REVIEW_CYCLE.md` finds the section and the row; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [x]

> Note: added "Human fields and slugs" section, the "GitHub's Approve review" row and one sentence in ready-check item 4 in `bundles/base/process/REVIEW_CYCLE.md`. `grep -n "Human fields and slugs\|Approve review"` finds all three; `python3 bundles/base/tools/build.py --check` printed `lint ok`. Commit: see the CP1 commit log (Tasks 1 and 2 together).

---

### Task 3 — Split the CI section of the pull request template and add its instructions

**Source:** INT-27 S1, S2, S3, S7 (the owner's worked example)
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** Rewrite "CI on the pushed commit" to the shape of INT-27's "After" example: **Commit (full hash)**; "1. Ran:" with one numbered sub-line per workflow run (name, run id, status, conclusion, link, or "no run found"); an **Instructions:** block as visible text (not a comment) with the pass step (open each link; if every run is `completed` with `success`, write your name below), the fail step (if a run failed, is not `completed`, or is missing, tell the coordinator and do not write your name) ; then `**Confirmed by:** <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>` (label changed to "confirmer" and "confirmation" for this field). Keep the full hash. Replace the template's HTML-comment hints for this section with one line that the coordinator writes the evidence and leaves the slug.
**Acceptance:** `grep -c "<Insert " bundles/base/templates/PULL_REQUEST_TEMPLATE.md` is at least 1 for this field; the section has no HTML comment holding instructions; the hash line still says "full hash".
**Todo:** [x]

> Note: rewrote "CI on the pushed commit" in `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` to INT-27's "After" shape (hash, numbered "Ran:" with sub-lines, visible **Instructions:**, `Confirmed by` slug with "confirmer"/"confirmation"). `grep -c "<Insert " ...` printed 1 at this step (the Task 4 slug came after); no instruction sits in an HTML comment in this section; "full hash" kept. Commit: see CP1 log.

---

### Task 4 — Make the ready-check State cell and the confirmation line say what to write

**Source:** INT-27 S3, S4
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** In "Ready check" change the header `State (met / missing)` to `State` and put into each State cell the placeholder `missing` (the safe value); add an **Instructions:** block above the table: the coordinator replaces the cell with exactly `met` or `missing`, `met` needs evidence in the Evidence cell, a human does not edit State cells. Replace the **Human confirmation** comment with the slug `<Insert Name of decider on Date of decision, ex. M. Kusanagi on Jan-01-2027>` plus numbered instructions (what to review, where, when to write the line, what not to write if a line is missing).
**Acceptance:** `grep -n "met / missing" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` prints nothing; both words `met` and `missing` appear in the instructions.
**Todo:** [x]

> Note: header is now `State`, each cell holds `missing`, an **Instructions:** block above the table names `met` and `missing`, and the Human confirmation comment is replaced by the `Human confirmation` slug with numbered instructions. `grep -n "met / missing"` prints nothing. Commit: see CP1 log.

---

### Task 5 — Add instructions to each tickable line and a step for the Approve review

**Source:** INT-27 S1, S5; Problem items 2 and 4
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`
**Action:** MODIFY
**Change:** Under "What remains for you" add an **Instructions:** block per kind of line: (a) per changed file: open the diff on the Files changed tab, what to look for, a tick means you read it and accept it, and if you do not accept it, leave it unticked and say why in a comment; (b) the CI line: points to the instructions under "CI on the pushed commit" (no second copy); (c) findings: read the "Decisions for you" table, write "accept all" or name the exceptions. Add a numbered step "GitHub's Approve review": separate from every tick and row here; needed when the repository's rules require an approving review (see its `Review process` and branch rules); where to click ("Review changes" on the Files changed tab, then Approve); if the control is missing or disabled for you, do not write a name or tick here instead, and ask the owner how approval is met in this repository. Add the fact Task 1 found, if it was read (otherwise no claim about GitHub). Keep each block to numbered short lines.
**Acceptance:** `grep -n "Approve review\|Review changes" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` finds the step; it makes no claim about self-approval (read the diff).
**Todo:** [x]

> Note: added an **Instructions:** block under "What remains for you" (files, CI line pointing to the CI section, findings, and a numbered "GitHub's Approve review" step stating it is separate, where to click, and what to do if the control is missing). It states no fact about self-approval: Task 1 found the documentation sentence, but Open question 3 (the route) is not answered, so no claim about GitHub's behavior is made; the step only says to ask the owner. `grep -n "Approve review\|Review changes"` finds line 72. Commit: see CP1 log.

---

### Task 6 — Add tests for the pull request template

**Source:** INT-27 S1, S3, S4, S7
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_pr_template_has_visible_instructions_and_one_slug_shape` (every human-written line, `Confirmed by` and `Human confirmation`, holds exactly one match of the pattern `<Insert [^<>]*>`; no instructions sit only inside an HTML comment; the pattern finds no text in the rest of the template), `test_pr_template_state_cells_name_both_values` (no `met / missing`; both words in the instructions), `test_pr_template_names_the_approve_review_and_claims_nothing_about_self_approval` (contains "Approve" and "Review changes"; contains none of "own pull request", "self-approv", "cannot approve"), and `test_pr_template_is_generic` (no "Michael Hay", no repository name). Follow the style of the existing `test_pr_template_has_remaining_steps_and_decisions_table`. Failing first: run them before Tasks 3 to 5 are applied to the source and record the counts.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "pr_template"` passes (counts reported); the note records the failing-first run.
**Todo:** [x]

> Note: added the four tests (plus `import re` and two helpers) to `bundles/base/tests/test_bundle.py`, following `test_pr_template_has_remaining_steps_and_decisions_table`. In `test_pr_template_is_generic` the word "manifold" is not in the forbidden list because the template legitimately names `.manifold/guard-log.jsonl` (the install's folder, not this repository's name). Failing first (before Tasks 3 to 5 touched the template; Task 2 only touched REVIEW_CYCLE): `.venv/bin/python -m pytest bundles/base/tests -q -k "pr_template"` gave 3 failed, 2 passed (the existing test and the generic test pass with the old text). After Tasks 3 to 5: same command, 5 passed, 2078 deselected. Commit: see CP1 log.

---

### Task 7 — Put the slug and instructions on the plan, test-plan and intent human lines

**Source:** INT-27 Open question on the other human lines (apply if answered yes)
**Files:** `bundles/base/templates/PHASE_PLAN_TEMPLATE.md` (**Approved by**, **Amendment approved by**), `PHASE_TEST_PLAN_TEMPLATE.md` (**Approved by**), `INTENT_TEMPLATE.md` (`accepted_by`)
**Action:** MODIFY
**Change:** On each line put the slug and one visible **Instructions:** line under it (what to read, then replace the whole slug; an agent leaves it). In `INTENT_TEMPLATE.md` the slug is a quoted YAML string (`accepted_by: "<Insert ...>"`) so the frontmatter still parses; the first line stays `---`. The reviewer's text "A blank **Approved by** is the right state of a new test plan" stays true and now also names a slug.
**Acceptance:** `grep -c "<Insert " bundles/base/templates/PHASE_PLAN_TEMPLATE.md` is 2; `.venv/bin/python -c "import yaml,sys; t=open('bundles/base/templates/INTENT_TEMPLATE.md').read().split('---')[1]; print(yaml.safe_load(t)['accepted_by'])"` prints the slug (PyYAML is in `server/requirements.txt`).
**Todo:** [x]

> Note: slug plus a visible **Instructions:** line on the plan's two lines, the test plan's line and the intent's `accepted_by` (quoted YAML string, instruction as a YAML comment line because frontmatter cannot hold visible prose; first line still `---`). `grep -c "<Insert "` on the plan template gives 2; the PyYAML command printed `<Insert Name of acceptor on Date of acceptance, ex. M. Kusanagi on Jan-01-2027>`. The existing test `test_plan_template_puts_checkpoints_under_tasks_and_the_amendment_after_the_checklist` pins "never fills in" and "human" on the amendment line; I did not edit it: the amendment line keeps a short trailing comment `<!-- human only: the planner never fills in this line -->` so the old assertions still hold (the instruction itself is visible text). Commit: see CP1 log.

---

### Task 8 — State that an unreplaced slug counts as a blank approval

**Source:** INT-27 S6, S7; Concerns 4
**Files:** `bundles/base/rules/core/approved-plan-before-execution.md`, `bundles/base/agents/coder.agent.md` (line 24 and 34), `bundles/base/agents/test-coder.agent.md` (line 33)
**Action:** MODIFY
**Change:** Where each says "If it is blank", add "or still holds an `<Insert ...>` slug" (same words in all three). No other word changes.
**Acceptance:** `grep -rn "Insert" bundles/base/rules/core/approved-plan-before-execution.md bundles/base/agents/coder.agent.md bundles/base/agents/test-coder.agent.md` finds all three; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [x]

> Note: "or still holds an `<Insert ...>` slug" added in the rule, coder (lines 24 and 34) and test-coder (line 33), same words. The grep finds all three; `build.py --check` printed `lint ok`. Commit: see CP1 log.

---

### Task 9 — Teach the coordinator the new CI line, the slugs and the rule that it never fills one

**Source:** INT-27 S2, S6, S7
**Files:** `bundles/base/agents/coordinator.agent.md` ("CI of the exact commit", "Ready check", "What you do not do")
**Action:** MODIFY
**Change:** In "CI of the exact commit" write the result as the numbered shape of Task 3 (one line per run with link; the **Instructions:** block; the slug left as is) and never tell the human to confirm when a run is not `completed` with `success`. In "Ready check" treat any `<Insert` text left in a human field as missing and name each such field in the report. Add to "What you do not do": replace a slug, write a name or date in a human field, tick a box, or write "approved" for a human. Do not weaken any existing line.
**Acceptance:** `grep -n "Insert\|never replace" bundles/base/agents/coordinator.agent.md` finds each; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [x]

> Note: coordinator now writes the CI result in the numbered shape with the slug left alone, treats `<Insert` in a human field as missing (naming each field), and "What you do not do" gains the slug line; nothing weakened. `grep -n "Insert\|never replace"` finds each; `build.py --check` printed `lint ok`. Commit: see CP1 log.

---

### Task 10 — Add tests for Tasks 2, 7, 8 and 9

**Source:** INT-27 S6, S7
**Files:** `bundles/base/tests/test_bundle.py`
**Action:** MODIFY
**Change:** Add `test_review_cycle_defines_slug_rule_and_approve_review`, `test_plan_and_intent_templates_carry_a_slug` (and the intent frontmatter parses), `test_blank_approval_text_counts_a_slug_as_blank` (rule, coder, test-coder), `test_coordinator_never_fills_a_slug_and_treats_one_as_missing`. If an existing test pins text these tasks changed, stop, name the test and the assertion and ask the owner before editing it. Failing first, counts recorded.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests -q -k "slug or approve_review or blank_approval"` passes with the counts reported.
**Todo:** [x]

> Note: four tests added to `bundles/base/tests/test_bundle.py`. The intent test does not use PyYAML (CI installs only pytest and skills-ref, not PyYAML) and checks the quoted-string shape instead. Failing first, run after Tasks 2 to 6 and before Tasks 7 to 9: `.venv/bin/python -m pytest bundles/base/tests -q -k "slug or approve_review or blank_approval"` gave 3 failed, 7 passed (the review cycle test passed already, because Task 2 was done; it is a guard now). After Tasks 7 to 9: all pass. Full run `.venv/bin/python -m pytest bundles/base/tests -q`: 2086 passed, 1 skipped (one existing test needed no edit; see Task 7). Commit: see CP1 log.

---

### Task 11 — Report unreplaced slugs in `/phase-status`

**Source:** INT-27 S6
**Files:** `bundles/base/scripts/phase_status.py`, `bundles/base/commands/phase-status.md`, `bundles/base/commands/phase-status.prompt.md`, `bundles/base/tests/test_phase_status.py`
**Action:** MODIFY
**Change:** Add `SLUG_RE = re.compile(r"<Insert [^<>]*>")` and a function `slugs(lines, label)` that returns, for each match on a line, the field name taken from the text before the first colon on that line with asterisks removed, and counts the match only when that field name is a human-field label: `Approved by`, `Amendment approved by`, `Confirmed by`, `Human confirmation`, `Intent accepted by`, `accepted_by`. A slug written as an example in prose (a task's `**Change:**` line, a code span in a sentence) is therefore not reported, while a slug inside a code span on a human-field line still is (Concerns 3). Found in `phase_status.py` today (read): `COMMENT_RE` blanks HTML comments only; `is_blank_approval` reads a value as blank when it starts with `<` and ends with `>`, but only on the plan's and test plan's approval lines; nothing there knows `Insert`, code spans or fenced blocks. In `report`, add a section "Unreplaced slugs" over the plan and test plan, listing `file:line field`; add each to `reasons` so the level reads below mergeable. Add an optional `--pr-body <file>` (parsed like `--root` in `main`) that scans a saved copy of the description the same way and prints the same list; with the option absent the output states that the pull request description was not read. Standard library only, read-only, sorted output. Update `argument-hint` in both command files to `<phase number> [--pr-body <file>]`. Add tests: a plan with a slug reports it and level below mergeable; a plan with the slug replaced lists none; `--pr-body` with two slugs lists both by field name; output is identical on two runs.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` passes (counts reported); `.venv/bin/python bundles/base/scripts/phase_status.py 4` run on this plan lists no unreplaced slug (the "Intent accepted by" lines and the plan's own **Approved by** line hold the owner's recorded name and date; the `<Insert ...>` text elsewhere in this plan is prose in task text, not on a human-field line, so it is not listed), and run on a copy of the plan in the scratchpad where one "Intent accepted by" line holds the slug it lists exactly that line; it is read-only (`git status --short` unchanged).
**Todo:** [x]

> Note: `phase_status.py` gains `SLUG_RE`, `HUMAN_LABELS`, `slugs(lines)`, an "Unreplaced slugs" section that feeds `reasons`, and `--pr-body <file>` (read-only; a missing file exits 2); `is_blank_approval` now also reads a slug (even inside a code span) as blank; both command files' `argument-hint` is `<phase number> [--pr-body <file>]`. The field label is stripped with `strip("* ")`, not `replace`, because the existing AST test bans `.replace(` calls in the script (it could write a file). Five tests added to `bundles/base/tests/test_phase_status.py` (slug in plan; slug in Approved by and in a code span; slug replaced lists none; `--pr-body` two slugs by field name, a commented one hidden; identical output twice and missing file exits 2) plus `["7", "--pr-body"]` in the bad-argument test. `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q`: 27 passed. Full `.venv/bin/python -m pytest bundles/base/tests -q`: 2092 passed, 1 skipped; `build.py --check`: lint ok. Acceptance: `phase_status.py 4` on this plan printed `Unreplaced slugs: 0`; on a scratchpad copy with one "Intent accepted by" line replaced by the slug it printed `Unreplaced slugs: 1` at `PHASE_4_PLAN.md:19 Intent accepted by` and `Level: below mergeable (1 unreplaced slug(s); ...)` (scratch script `.../scratchpad/check_task11.py`, run with `python3 -I`, deleted its temp copy); `git status --short` showed only my source edits. Commit: see CP1 log.

---

### Task 12 — Record the Approve review facts in the branch rules

**Source:** INT-27 Affected files (`docs/process/BRANCH_RULES.md`); Open question on self-approval
**Files:** `docs/process/BRANCH_RULES.md` (not shipped)
**Action:** MODIFY
**Change:** In the "Approving reviews" row and the sentence "how the owner's approval is met ... is not recorded here", record only what Task 1 read, with its source, and the route the owner chose in answer 3 (document an existing route, a second account, or a ruleset change, which stays the owner's act). Write "unverified: confirm with <source>" for anything not read.
**Acceptance:** each new statement shows its source or "unverified"; `git diff --stat -- .github` is empty.
**Todo:** [x]

> Note (2026-11-14): `docs/process/BRANCH_RULES.md` "Approving reviews" row now points to a new subsection that records, each with its source, the review count of 1, the documentation sentence on authors, the two bypass actors and `current_user_can_bypass: "pull_requests_only"`, and the owner's chosen route (the repository's bypass, Open question 3). Four items stay "unverified: confirm with <source>": what `RepositoryRole` 5 and `require_extra_approval_for_unattributed_changes` mean, whether the bypass lets the owner merge without an approving review, and what "Review changes" shows an author. No claim about GitHub behavior beyond what Task 1 read. The Task 5 template step (line 72) says only "ask the owner how approval is met" and claims nothing about self-approval, so it does not contradict this; no shipped text changed. `git diff --stat -- .github` printed nothing. Commit: see CP1 log.

---

### Task 13 — Refresh this repository's own install from the build

**Source:** INT-27 Affected files (installed copies); Phase 3 Task 18 route
**Files:** `docs/templates/*`, `docs/process/REVIEW_CYCLE.md`, `.claude/agents/*`, `.claude/commands/phase-status.md`, `.manifold/*`, `AGENTS.md` managed block (all generated)
**Action:** MODIFY
**Change:** Build into the scratchpad (`python3 bundles/base/tools/build.py --out <scratchpad>/dist`), unzip, read `install.py --help`, run the install over this repository as in Phase 3 Task 6 (dry run first, then `--apply` without `--force`); stage explicit paths only. Do not hand-edit the managed block.
**Acceptance:** `cmp bundles/base/templates/PULL_REQUEST_TEMPLATE.md docs/templates/PULL_REQUEST_TEMPLATE.md` prints nothing; `install.py --status` from the unzipped bundle reports no modified file.
**Todo:** [x]

> Note: done out of order, before Task 12 (it does not depend on it; Task 12 waits for the owner's answer to Open question 3). `python3 bundles/base/tools/build.py --out <scratchpad>/dist` -> `manifold-base-0.3.0.zip` (348342 bytes), unzipped; `install.py --help` read first; dry run `--target . --format claude --profile build` -> UPDATE coder, test-coder, coordinator agents, `phase-status.md`, the three templates plus the PR template, `REVIEW_CYCLE.md`, `.manifold/phase_status.py`, AGENTS.md managed block (one line: the rule text), everything else SKIP; then the same with `--apply`, no `--force` -> "Installed manifold 0.3.0". The guard did not block the install (the three `.claude/agents/*.md` files changed in this worktree; see the report). `cmp bundles/base/templates/PULL_REQUEST_TEMPLATE.md docs/templates/PULL_REQUEST_TEMPLATE.md` printed nothing; `install.py --status` (from the unzipped bundle): every file `ok`, 0 MODIFIED. No hand edit of an installed file; the managed block of AGENTS.md was changed only by the installer (diff is the one rule line). Commit: see CP1 log.

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

**Source:** INT-2 S3 and Must never; Concerns 1; Open question 10 (owner agreed)
**Files:** `server/tests/test_write_failures.py` (CREATE)
**Action:** CREATE
**Change:** Read `write_page_of_kinds` and `handoff_create` first to name each failure point. The refusals of a stale etag and bad frontmatter are already tested (`test_pickup_stale_etag_rejected`, `test_write_validation.py`); do not repeat them, only add the unchanged-tree assertion for them. Using `ToolWorld` and monkeypatch, inject: a stale etag; invalid frontmatter; a write refused (`OSError` with `errno.ENOSPC` from `Path.write_text`); git refusing the commit (`git_commit` returning `committed=False`); a failure part-way through `handoff_create`. For the git refusal, assert the documented behavior and not an unchanged tree: the file stays on disk, the call reports that the commit did not happen, and nothing else changed (no stray folder, sidebar entry or log line beyond what the code documents). For every other case, assert that the tree (relative paths, empty folders and sha256 of every file outside `.git`), `wiki/_sidebar.md` and `wiki/log.md` equal their snapshot from before the call, and that `wiki_health` reports healthy. Where the existing code fails an assertion because of a stray folder, partial file, sidebar entry or log line, mark the case `pytest.mark.xfail(strict=True, reason="defect: <one line>")` (the owner's answer to Open question 10: these are defects for `bug-coder` after this phase), so the suite stays green and the defect is listed; do not edit the code and do not stop to ask.
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

### CP3 — Curated test data sets (INT-3)

INT-3 scenario seeds: S1 (instance by size) is deferred (owner confirmed, Open question 17). S2 (hostile text) is Tasks 23, 24, 25 and 27. S3 (a real source is scrubbed before use) is Tasks 26, 28 and 31, and applies to the Megaroast repositories.

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
**Change:** `README.md` holds the awkward cases, the real-data rule (who gives permission: the data's owner, in writing; the scrub steps for names, hosts, secrets and email addresses; the check; "the original is never committed") and a short "Megaroast testbed" section: the organization's name, the four repositories by role (fork, standalone GUI, holdout QA, example instance), that they are outside this repository, that nothing from them is committed here, that no test reads them, and that no builder agent reads the holdout QA repository. The owner gave permission to name the repositories (Open question 18) but supplied no names, so until the owner supplies them the README holds the organization name and the four roles only. Whether the holdout QA repository's name is covered by that permission is not stated (the answer says "it"); owner question: may it be named, or does it stay a role only? Default: role only. `scan.py`: `scan(path)` reports email addresses, hosts not ending in `.test`, `.example` or `.invalid`, strings shaped like tokens or keys, and every term listed in a private term list read from `~/.manifold/excluded_terms.json`, a file outside every checkout, as a JSON list of strings (the standard library has no YAML parser; `scan(path, terms_file=...)` takes the path as an argument so tests use a fixture file and never the owner's real one; Open question 12; the list is never committed or printed). `SIGNOFFS.md` holds a table with no rows yet (columns: source, owner, permission date, scrub checked by, scan result) and states that no real data is committed. A test in `test_datasets.py`, `test_scan_flags_real_shaped_text_and_passes_the_committed_sets`, feeds `scan` a temporary file with an email address, a non-test host and a token-shaped string, and runs it over `curated/`.
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

**Verification:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q` passes (counts reported); `cd server && ../.venv/bin/python -m pytest -q` passes; `git diff --stat` for the checkpoint lists only `server/tests/datasets/`.

### CP4 — The Megaroast testbed (INT-3)

The four repositories already exist (owner's statement, Nov 14, 2026). The tasks confirm and record; nothing is created. The owner permits naming the repositories (Open question 18) but has supplied no names; until the owner supplies them, rows and notes use the role names (fork, standalone GUI, holdout QA, example instance). The holdout QA repository stays a role only unless the owner says it may be named (Task 26).

### Task 28 — Record the owner's decisions on permission and visibility

**Source:** INT-3 Constraints (written permission, checked scrub); Concerns 7
**Files:** `server/tests/datasets/SIGNOFFS.md`
**Action:** MODIFY
**Who:** the owner writes the rows; the coder only prepares the empty table (Task 26) and an **Instructions** line above it.
**Change:** Add one row per Megaroast repository that derives from the company repository (the fork, the standalone GUI, and the example instance if its content derives from it): source (by role), owner, permission date, the repository's visibility (private or public), and "nothing committed here". The owner writes the name and date; the coder does not fill any cell. Open question 16 is answered (the owner gives permission; all repositories are private this phase), so it blocks nothing; if a row's visibility is not private, stop and tell the owner.
**Acceptance:** each row is filled by the owner; `git diff` shows no content from any Megaroast repository, only the table rows.
**Todo:** [ ]

---

### Task 29 — Confirm the three working Megaroast repositories exist

**Source:** INT-3 owner answer (the fork, the standalone GUI, the example instance)
**Files:** none in this repository; the note goes here (counts and non-sensitive facts only)
**Action:** none (owner check)
**Who:** the owner, with their own GitHub login; the coder does not run it.
**Change:** The owner confirms in chat that the fork of `company_dns`, the standalone GUI repository and the example manifold instance exist in the Megaroast organization, and reads each one's visibility with `gh repo view <Megaroast>/<name> --json visibility` (read-only; `visibility` is a listed `--json` field, gh 2.86.0). The note records: three repositories exist, and the visibility of each by role. Repository names are written only after the owner supplies them (Open question 18); until then the note uses roles.
**Acceptance:** the note says "3 of 3 exist" with each visibility, and the visibility matches the Task 28 rows; `git diff` shows no Megaroast content.
**Todo:** [ ]

---

### Task 30 — Confirm the holdout QA repository exists and is untouched by builders

**Source:** INT-3 owner answer (holdout QA repository); `AGENTS.md` "Held-out scenarios"
**Files:** none in this repository; the note goes here
**Action:** none (owner check)
**Who:** the owner. Builder agents never read, clone or ask for its content.
**Change:** The owner confirms the holdout QA repository exists, is private, and that no builder session (this repository's agents) has been given access to it. The App is not installed on it (Task 34). Which repositories its scenarios test, and who writes them, is the quality side's decision and is not planned here.
**Acceptance:** the note records "exists, private, not read by builders"; the coder's report states that it did not read it.
**Todo:** [ ]

---

### Task 31 — Check the example instance from a scratch clone

**Source:** INT-3 S3; INT-2 constraint (tests are offline, so this is a manual check, not a test)
**Files:** none changed; the note goes here (no repository content in it)
**Action:** none (manual check)
**Who:** (needs the owner's private excluded-terms file to exist at `~/.manifold/excluded_terms.json`, never committed and never printed; if it does not exist, stop and tell the owner) the owner runs the clone, or the coder after the owner's explicit go-ahead; the clone goes to the scratchpad, outside this repository, and uses the owner's existing login (`gh repo clone <Megaroast>/<name> <scratch folder>`, form verified in `gh repo clone --help`; no token is read or printed). The App is not used here.
**Change:** Start the server against the clone as `docs/quickstart.md` describes (read it first; the exact start command is not recorded here), then call `wiki_health` and `wiki_inventory_tool`. Run `scan.py` (Task 26) using the owner's private `~/.manifold/excluded_terms.json` over the clone, to learn what a scrub would still have to remove; the findings are counted in the note and never quoted. Do not copy any file from the clone into this repository.
**Acceptance:** the note records the commands, that health reports healthy, the number of components `wiki_inventory_tool` lists (the owner expects two) and the count of scan findings per kind; `git status --short` in this repository is unchanged.
**Todo:** [ ]

---

**Verification:** `git diff --stat` for the checkpoint lists only `server/tests/datasets/SIGNOFFS.md`; the owner confirms in chat that the three working repositories and the holdout QA repository exist with the visibility recorded in `SIGNOFFS.md`; `git status --short` is otherwise unchanged.

### CP5 — The GitHub App thin slice (INT-7)

Every task that creates the App, installs it or touches its key or a token is the owner's act. The key lives outside every repository in the file named by `MANIFOLD_APP_KEY_FILE` (a variable name only; nothing reads it). No agent holds the key or a token.

### Task 32 — Read what GitHub says about creating an App and minting a token

**Source:** INT-7 constraints "What an App cannot do ... verified before any plan relies on it", "Every permission has a feature"
**Files:** none changed; the note goes here
**Action:** none (read)
**Change:** Read GitHub's documentation and record each fact with its source, or "unverified: confirm with <source>". Read already (Nov 14, 2026): (a) an organization owner, or a person the organization lets manage all its apps, registers an App under Organization settings, Developer settings, GitHub Apps, New GitHub App; the name must be unique across GitHub, not longer than 34 characters; "Where can this GitHub App be installed?" offers "Only on this account" (private) or "Any account"; each repository permission is Read-only, Read & write or No access (registering a GitHub App). (b) An installation access token is requested with `POST /app/installations/INSTALLATION_ID/access_tokens`, authenticated with a JWT as a Bearer token; it expires after one hour; the request can narrow it to listed repositories (at most 500) and to chosen permissions, never beyond the App's (generating an installation access token). Still to read: the JWT's claims and signing algorithm (the page refers to a separate guide; unverified: confirm with GitHub's guide on generating a JWT for a GitHub App); that Metadata read is always granted to an App and what it allows; whether the installation endpoint `GET /installation/repositories` needs only Metadata; how a lost private key is revoked and replaced; whether a private App can be transferred to another organization later.
**Acceptance:** the note lists each fact above with its source or "unverified"; the permission list in Task 33 is justified by it.
**Todo:** [ ]

---

### Task 33 — The owner creates the private App `manifold` in Megaroast

**Source:** INT-7 S1; constraints least privilege, private first, the name, no long-lived secrets in a repository
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner, by the settings page of the Megaroast organization (path in Task 32). The coder and every agent do not do this, and do not see the key.
**Change:** The owner, following these steps: (1) New GitHub App; name `manifold`. GitHub refuses the name if it is taken (documentation: unique across GitHub); the owner states it is available, and records the outcome. If refused, the owner chooses a fallback name and says so in chat before anything else is built. (2) Installability: "Only on this account" (private). (3) No webhook (uncheck Active), no callback URL, no user authorization, no device flow (none is used by this slice). (4) Permissions, only these: **Metadata: Read-only**, needed by Task 34 (checking the installed repository list and visibility) and Task 35 (the verification call that lists the repositories the token can see). No other permission, in particular no Contents, Pull requests, Issues, Administration or Secrets: no Phase 4 task needs them (Open question 21). (5) Create the App, generate one private key, and save the file outside every repository (the path in `MANIFOLD_APP_KEY_FILE`). The key is never pasted into chat, a log, a pull request or any file in a repository.
**Acceptance:** the owner confirms in chat (a) the App exists and is private, (b) the settings page's permission list shows Metadata read-only and nothing else, (c) the name is `manifold` or the chosen fallback, (d) the key file is outside every repository. No key, App secret or token appears in chat.
**Todo:** [ ]

---

### Task 34 — The owner installs the App on the Megaroast test repositories

**Source:** INT-7 S1 ("installed only on the chosen repository")
**Files:** none in this repository
**Action:** none (outward action in the Megaroast organization)
**Who:** the owner.
**Change:** The owner installs the App on the Megaroast organization with "Only select repositories", choosing the fork, the standalone GUI and the example instance, and not the holdout QA repository (Concerns 8). No organization-owner approval step is expected because the owner owns the organization; if one appears, the owner records it.
**Acceptance:** the owner confirms the installation's repository count is 3 and the holdout QA repository is not among them; the note records the count and "permissions: Metadata read-only". No names or IDs in the note until the owner supplies repository names (Open question 18); roles only, and never an App ID or installation ID.
**Todo:** [ ]

---

### Task 35 — The owner mints one short-lived installation token and uses it once

**Source:** INT-7 S2 (token expiry); constraint "short-lived tokens only"
**Files:** none in this repository
**Action:** none (owner act; no helper script is written in this phase)
**Who:** the owner, on their own machine. No agent runs, reads or sees it.
**Change:** Using the key file named by `MANIFOLD_APP_KEY_FILE`, the owner signs a JWT as GitHub's guide describes (Task 32 reads it; how to sign it with the tools on the owner's machine is unverified), exchanges it at `POST /app/installations/INSTALLATION_ID/access_tokens` (documented, Task 32) asking for `permissions` limited to Metadata read, then makes one request with the token that lists the repositories the installation can see, and discards the token. The token is never written to a file, chat or log. After one hour the owner repeats the one request and observes the refusal (the documented expiry).
**Acceptance:** the owner confirms in chat: the exchange succeeded, the listing shows 3 repositories, and the same token is refused after one hour (HTTP status only, no token). No script is added to the repository.
**Todo:** [ ]

---

### Task 36 — Teach the scan to flag private keys and installation tokens

**Source:** INT-7 S2 Must never; constraint "No long-lived secrets in the instance repository"
**Files:** `server/tests/datasets/scan.py`, `server/tests/datasets/test_datasets.py`
**Action:** MODIFY
**Change:** In `scan.py` add to the token-shape patterns of Task 26: a PEM private-key header line (`-----BEGIN` followed by any words and `PRIVATE KEY-----`), and the GitHub token prefixes `ghs_`, `ghp_`, `gho_` and `github_pat_` followed by at least 20 word characters (the prefixes are unverified: confirm with GitHub's documentation on token formats before relying on them). Add `test_scan_flags_a_private_key_header_and_github_token_shapes` that feeds `scan` a temporary file holding a fake PEM header and fake prefixed strings built in the test by string concatenation (so no real or whole-looking secret is committed), and checks `curated/` stays clean.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q -k scan` passes (counts reported); failing first, counts recorded.
**Todo:** [ ]

---

### Task 37 — Record the App facts, without any secret, in the datasets README

**Source:** INT-7 constraints (permission listed with its feature; private; key outside); INT-3 "Megaroast testbed" section
**Files:** `server/tests/datasets/README.md`
**Action:** MODIFY
**Change:** In the "Megaroast testbed" section add a subsection "GitHub App `manifold` (Megaroast)": the App is private; its only permission is Metadata (read), with the feature that needs it (checking which repositories an installation sees); it is installed on three of the four repositories, never the holdout QA repository; installation tokens last one hour (documentation, Task 32); the private key is kept by the owner outside every repository and no agent or test reads it; and the list of INT-7 seeds not covered by this phase (copied from "Intent review"). No App ID, installation ID, key, token or repository name.
**Acceptance:** `cd server && ../.venv/bin/python -m pytest tests/datasets -q` passes; `.venv/bin/python server/tests/datasets/scan.py server/tests/datasets` prints no finding; `grep -n "PRIVATE KEY\|ghs_\|ghp_" server/tests/datasets/README.md` prints nothing.
**Todo:** [ ]

---

**Verification:** `cd server && ../.venv/bin/python -m pytest -q` passes with counts; `python3 bundles/base/tools/build.py --check` prints `lint ok` and `.venv/bin/python -m pytest bundles/base/tests -q` still passes (no bundle or other server file changed); `git diff --stat` for the checkpoint lists only `server/tests/datasets/`; `git grep -n "BEGIN .*PRIVATE KEY"` over the whole repository matches only the detection pattern in `server/tests/datasets/scan.py` (no key file, no fake key in the test: it is built by concatenation); the owner's confirmations of Tasks 33 to 35 are in chat.

### CP6 — Release 0.3.1 (INT-27 owner answer)

Placed last because the owner said to release after the work is done. Only CP1 changes shipped files (the thin slice, CP4 and CP5 change no file under `bundles/base/`), so the owner may instead take the release right after CP1 merges.

### Task 38 — Bump the bundle version to 0.3.1

**Source:** INT-27 Open question "Which release carries this?" (owner: "call the release V0.3.1"); commit `4f8b448` (how 0.3.0 was bumped)
**Files:** `bundles/base/VERSION`
**Action:** MODIFY
**Change:** Replace the single line `0.3.0` by `0.3.1`. Release 0.3.0 changed only `bundles/base/VERSION` and the `version` in `.manifold/manifest.json`, in two commits ("Bump the base bundle", then "Refresh this repository's own install"); do the same. The release workflow (`.github/workflows/release.yml`) fails unless the tag equals `v` plus the content of `bundles/base/VERSION`.
**Acceptance:** `cat bundles/base/VERSION` prints `0.3.1`; `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported).
**Todo:** [ ]

---

### Task 39 — Refresh this repository's own install to 0.3.1

**Source:** commit `4f8b448` (second commit)
**Files:** `.manifold/manifest.json` (generated; plus any other file `install.py --status` reports)
**Action:** MODIFY
**Change:** Run the install over this repository as in Task 13 (dry run first, then `--apply` without `--force`) from a build of the new version; do not hand-edit `.manifold/manifest.json`. Commit it separately from Task 38.
**Acceptance:** `.manifold/manifest.json` reads `"version": "0.3.1"`; `install.py --status` reports no modified file.
**Todo:** [ ]

---

### Task 40 — Merge and tag v0.3.1

**Source:** `.github/workflows/release.yml` (trigger: a pushed tag `v*`)
**Files:** none
**Action:** none (outward action)
**Who:** the owner merges the pull request and creates the tag; the coordinator and coder do not tag and do not push a tag. The tag ruleset `protect-release-tags` exists and its rules are unverified (`docs/process/BRANCH_RULES.md`).
**Change:** After the pull request with Tasks 38 and 39 is merged, the owner creates the tag `v0.3.1` on the merge commit and pushes it. The workflow then lints, tests, builds the ZIP and creates the release.
**Acceptance:** the owner confirms the `release` workflow run for `v0.3.1` succeeded and the release lists `manifold-base-*.zip` and `SHA256SUMS` (names as in `release.yml`).
**Todo:** [ ]

---

**Verification:** `git tag` lists `v0.3.1` (run by the owner); `cat bundles/base/VERSION` on the tagged commit prints `0.3.1`.

## Completion checklist

- [ ] All tasks marked [x] by the coder (Tasks 28 to 30, 33 to 35 and 40 by the owner's confirmation; Tasks 31 by the owner's go-ahead; Task 32 is a recorded read)
- [ ] `python3 bundles/base/tools/build.py --check` prints `lint ok`
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` and `cd server && ../.venv/bin/python -m pytest -q` pass clean (no regressions; xfail cases named)
- [ ] No [~] blocked items outstanding
- [ ] No Megaroast content, key, token or secret in any committed file (`git diff` of the phase read for it)
- [ ] Level aimed at: mergeable (see "Definition of done" in `docs/process/REVIEW_CYCLE.md`)
- [ ] Summary note added by the coder below this line

## Open questions

Each has an `Answer:` line for the owner. Where the owner already answered in an intent file, the line quotes it and names the file. Still empty: 3, 6 and 19 (three; the owner accepts the defaults of 6 and 19 separately). Answered in part: 18 (permission to name the repositories, no names supplied). Decided on delegation, owner may overrule: 7, 8, 9. Overruled by the owner: 15.

1. **Split INT-27 from the server work?** What: do INT-27 (bundle text, CP1) and INT-2/INT-3 (server tests, CP2 and CP3) go in one phase, one pull request, or separately? Why: INT-27 is your current pain and must not wait on, or be held by, a large server review (the review loop allows three runs); the two have different release surfaces. Consequence: one pull request means one long review and a bigger risk of a late finding blocking the small fix; two pull requests cost one more cycle. Recommendation: keep one plan so the intents are reviewed once, but deliver CP1 as its own pull request first and merge it before CP2 starts; if you prefer, CP2 and CP3 move unchanged to `PHASE_5_PLAN.md`. Default: that recommendation.
   Answer: Keep one plan (Michael Hay, 2026-11-13, entered by the coordinator at the owner's instruction in chat: "Keep one plan").
2. **One slug shape for every human field?** What: a single form `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>`, label changed per field. Why: one search finds every unfilled field. Consequence if not: several shapes and gaps in detection. Recommendation and default: one shape (INT-27's recommendation), Mon-DD-YYYY as in your example.
   Answer: Yes (owner, `intent/INT-27-clear-human-instructions-in-the-pr.md`, Open questions: "Yes this is the right format.").
3. **Self-approval in a solo repository.** What: the ruleset requires one approving review and you are the only person. Why: the instruction for the Approve review needs a "if GitHub does not allow it" step, and nothing in the repository says what it is. Consequence: without a decision, the text can only say "stop and ask the owner" (it never claims what GitHub does). Recommendation: Task 1 reads GitHub's documentation and the ruleset first; then you choose to document an existing route (for example a bypass you already hold), a second account, or a ruleset change (your act, out of scope). Default: document what is read and ask.
   Answer: Document the existing route: the repository's bypass (the ruleset's `pull_request` bypass the owner already holds), because this is a solo repository (Michael Hay, 2026-11-14, entered by the coordinator at the owner's instruction in chat: "We will use a bypass since this is a solo-repo."). What the bypass does exactly stays "unverified" until read from GitHub's documentation.
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
   Answer: Delegated to planning by the owner (same words, `intent/INT-2-...md`). Decision after the survey: advisory. No conformance run exists in the repository (only the `initialize` call by `curl` in the `image` job of `server.yml`), and the server tests themselves are not required checks today (Concerns 6), so a required conformance check would be stricter than the rest. The owner may overrule. Answer: I agree with the deferrals.
9. **Coverage gate (INT-2)?** What: whether a coverage percentage blocks the merge. Why: the question is open in the intent; no coverage tool is in `server/requirements-dev.txt`, so adding one changes the locked dependencies. Consequence: a gate with no tool is wishful; adding a tool is a dependency change. Recommendation and default: no coverage gate in this phase; the contract list (every tool has a recording) and the import rule are the gates.
   Answer: Delegated to planning by the owner ("I believe we may already have some rules in the repo so the planner must find out", `intent/INT-2-...md`). Found: no coverage tool, configuration or percentage in `server/requirements-dev.txt`, `server/pytest.ini`, `.github/workflows/*`, `REVIEW.md`, `CONTRIBUTING.md` or `bundles/base/rules/`; the only coverage-related text is the template section "Coverage judgement" (a judgement, not a number) and the rule against committing coverage data. Decision: no coverage gate in this phase. The owner may overrule. Answer: I agree with the recommendation
10. **What happens to a write-failure test that exposes a defect (Concerns 1)?** What: for each case where the server leaves a file, folder, sidebar entry or log line after a refused write, do you change the code (a `bug-coder` fix, a behavior change) or narrow INT-2's S3 to what the code promises? Why: git refusing is documented as non-fatal today. Consequence: either way the test must match the decision, and an `xfail` left in place hides it. Recommendation: treat a stray folder, partial file, sidebar entry or log line as defects to fix by `bug-coder` after this phase, and keep "file stays when only the commit fails" as the documented behavior, written down in the test. Default: record each as `xfail(strict=True)` with the reason and ask.
    Answer: I agree with the recommendation
11. **What are small, medium and large (INT-3)?** What: the number of components and pages. Why: tests and demos ask by name. Consequence: the large size affects test run time. Recommendation: small 3 components and about 20 pages, medium 12 and 200, large 50 and 2000, all generated on demand in the test's temporary folder and never committed. Default: that recommendation (and the 20-second limit in Task 26).
    Answer: Superseded by the owner (`intent/INT-3-test-data-sets.md`: "Let's just start with Megaroast for now using 4 repos within the organization."). No sizes are defined in this phase; see Open question 17 for the deferred generator.
12. **Where does the list of terms to scan for live, and may real data ever be fetched (INT-3)?** What: the scan for real names and hosts needs a list, and a list of real names cannot be committed to a public repository. Recommendation: pattern checks in the repository (emails, non-test hosts, token shapes) plus a private list in a file outside the repository, named by `MANIFOLD_SCAN_TERMS`; "fetched" large data sets are not used. Consequence if not: the scan is weak, or it leaks the terms. Default: that recommendation.
    Answer: I agree with the recommendation
    Update (owner, 2026-11-14, in chat; entered by the coordinator): the private list lives at `~/.manifold/excluded_terms.yml` or `.json` instead of a file named by `MANIFOLD_SCAN_TERMS`. The plan uses `.json` because the standard library has no YAML parser; the owner may overrule.
13. **Is any real data on offer (INT-3)?** What: will the new company or other products offer real data, and under what terms. Why: the scrub procedure is only written, not used, until someone offers. Consequence: none now; this phase commits synthetic data only. Recommendation and default: no real data in this phase; the rule and scan ship so the first offer has a procedure.
    Answer: Yes, in a form the question did not foresee (owner, `intent/INT-3-...md`: "We can use the Megaroast organization to provide a testbed for external repos."). The rule and scan are therefore used in this phase (Tasks 26, 28, 31). Whether the company permits the derived repositories and whether any of them is public is Open question 16.
14. **Which release carries this?** What: CP1 changes shipped bundle text and so needs a version decision; CP2 and CP3 change no shipped file. Recommendation: you choose the number after CP1 merges (release is out of scope here). Default: no release task in this plan.
    Answer: Release as v0.3.1 after the work is done (owner, `intent/INT-27-...md`: "after we're done with the work we call the release V0.3.1 to signify we're patching the bundle"). CP6 (Tasks 38 to 40) does this; the owner tags.
15. **Is the GitHub App (INT-7) pulled into this phase? Decided: option (b), a thin slice.** The record below is the earlier decision of the coordinator and planner on the owner's delegation, which the owner overruled on Nov 14, 2026 (see the Answer line). The owner left the call to the coordinator and the planner. Read: INT-7, INT-6 (GitHub part), INT-1, INT-14, INT-15, INT-16, and the server source.
    **Facts.** (1) The server makes no GitHub call: `server/tests/test_offline_clean.py` forbids an HTTP client library in the server, and `server/manifold_cli/init_cmd.py` says "No GitHub, no outside request". Git runs as a local subprocess only (`server/wiki_backend/git.py`). (2) The features that would use an App are drafts or unplanned: INT-14 (draft, needs "the App or a personal access token"), INT-15, INT-16, INT-6's GitHub part ("comes after INT-7"). (3) INT-7's own rules: "Every permission has a feature", S1 "Must never: Request a permission that no feature uses", "What an App cannot do ... is verified before any plan relies on it", "One App per company, created by the company", and its open questions (which organization owns it, manifest flow or by hand, organization-owner approval, one App or two) are marked "resolve in planning" and "needs a spike". (4) INT-14's constraint already accepts a personal access token "for a quick start", never stored in the instance repository.
    **Options.** (a) All of INT-7 in this phase: eight scenario seeds, sign-in and device flow, either-rule, revocation; it needs the spike, the INT-1 roles and server code that does not exist, and delays CP2 and CP3, whose purpose is a safety net before server change. Rejected. (b) A thin slice: create the App in Megaroast with only Metadata (read) and install it on the example instance repository; no sign-in, no device flow. It would cover INT-7 S1 (create and install, permissions listed), S3 (remove it, by hand), the "private first" and "name" constraints, and open questions 1, 2 and 6 by spike. It would leave S2 (the server acting as the App: no server code uses it), S4 to S8, the either-rule, the sign-in rule, the revocation promise and the Secrets question. Cost: about six more owner-gated tasks (a spike read, name check, create, install, uninstall test, record) and an App no feature uses, which breaks INT-7's own "every permission has a feature" and "verified before any plan relies on it" for the permissions beyond Metadata. (c) Keep INT-7 out, and give the Megaroast testbed existing means: git and `gh` under the owner's own login, no token read or stored by any agent (Tasks 29 to 33).
    **Earlier decision (overruled): (c).** The testbed needs only to create four repositories and clone one; the owner's login does that today (`gh auth status` on this machine shows a keyring login for the owner's account; `gh repo fork --org`, `gh repo create --private --source --push` and `gh repo clone` exist in gh 2.86.0). Nothing in this phase would consume an App. Megaroast stays valuable to INT-7: it is the "first test organization" INT-7 names, so a later INT-7 plan, which should start with its spike, finds it ready. If the owner wants (b), the plan gains a checkpoint of about six tasks (it did: CP5, Tasks 32 to 37).
    **Unverified, to confirm in INT-7's own spike and not relied on here:** that the name `manifold` is free as a GitHub App name (unverified: confirm on GitHub's App creation page, an owner act); what an App cannot do (approve its own pull requests, create repositories, which permission creating a repository needs: unverified: confirm with GitHub's documentation on App permissions); whether an organization owner must approve the permissions for Megaroast (unverified: confirm with GitHub's documentation on installing an App in an organization).
    **Why the earlier decision was overruled.** The owner weighed the Megaroast repositories already existing against the cost of an App no server code uses, and chose to avoid throwing the work away. The owner also stated that the name `manifold` is available as a private App name because the owner owns the Megaroast organization. The slice, its seed mapping and its deferrals are in "Intent review" and CP5; the risks are Concerns 9.
    Answer (Michael Hay, 2026-11-14, entered by the coordinator at the owner's instruction in chat): "Pull in a thin slice of INT-7 because the Megaroast repo already exists and I don't want throw away work. As to the point of the private github app manifold name being available or not in a private app well it is. I own the org." The decision is option (b), the thin slice. Whether the name is free is confirmed at creation (Task 33); the plan states only the owner's words.
16. **Real data in the Megaroast repositories.** What: (a) does the company that owns `company_dns` permit a fork and a GUI derived from it in the Megaroast organization, in writing; (b) will each of the four repositories be private; (c) may anything from them ever be copied into this public repository (default: no, nothing). Why: INT-3 forbids real content in a public repository without written permission and a checked scrub; the repositories derive from a company's code. Consequence: without an answer, the Task 28 rows stay empty, Tasks 31 and 34 do not start, and the rest of the phase goes on. (The owner has said the four repositories already exist; that does not answer (a) to (c).) Recommendation: private for all four; permission written in `SIGNOFFS.md` (Task 28); nothing copied here. Default: that.
    Answer: I own the repos personally and can provide permission. For this phase we will keep all repos in Megaroast private.  When Manifold is ready for V1 release we will make the repos, including Manifold, public as a demonstration of function.  This is why it is preferred to work with the dummy organization so early: No wasted work.
17. **The sized synthetic generator (INT-3 S1: small, medium, large, same seed gives the same tree).** What: defer it, since the owner chose to start with Megaroast, or keep it as before. Why: S1 is an accepted seed and is not dropped silently; the curated messy and hostile sets (S2) stay either way. Consequence: deferring leaves no large instance for a later performance or store test (INT-4); keeping it adds about three tasks (the old Tasks 23, 25 and 26 in this file at commit `f939205`). Recommendation and default: defer, and add it when INT-4 needs a size.
    Answer: Defer it
18. **Names.** What: the exact names of the four Megaroast repositories, and whether the committed `README.md` of Task 26 may name them (default: it names the organization and the four roles, not the repository names). Why: the source repository belongs to a company. Consequence: Task 26 writes roles only until you answer.
    Answer: It is ok to name it since the intention is to eventually provide a public demoonstration.
19. **Should the server tests become a required check?** What: add `server tests (3.11)` and `server tests (3.12)` of `server.yml` to the ruleset's required checks (a ruleset change, your act on GitHub). Why: today a failing server test does not block a merge (Concerns 6), so CP2's contract tests would be advisory in effect. Consequence: not required, a broken tool can merge; required, a flaky test blocks every pull request. Recommendation: yes, after CP2 has passed on several pull requests. Default: no change in this phase.
    Answer:
20. **Are the INT-7 deferrals right?** What: this phase covers INT-7 S1 and the first half of S2 (Task 35) only. Deferred to a later phase: the server acting as the App (rest of S2), removing the App (S3), sign-in from the command line (S4), either-rule (S5), repository the App cannot see (S6), revocation timing (S7), the Claude Desktop note (S8), the browser or device-flow sign-in, sign-in lifetime, the manifest flow, one App per company, Secrets (write), and a token-minting helper (needs RS256 signing, which Python's standard library lacks, and the server must not gain a dependency). Why: INT-7 says nothing is dropped silently. Consequence: confirmed, a later INT-7 plan takes them; if you want S3 (uninstall and re-install the App) now, add one owner task to CP5. Recommendation and default: the deferrals as listed.
    Answer: Yes the deferrals are right.
21. **Does any Phase 4 task need more than Metadata (read)?** What: Task 31 clones with your own login, so no. Contents (read) would let a narrowed token clone the example instance in Task 31, and would be the only added permission. Why: INT-7 requires each permission to have a feature; a clone by token is a feature only if you want the testbed to exercise tokens. Consequence: yes, Task 33 adds Contents read-only and Task 31 gains an optional token route; no, Metadata only. Pull requests and Contents write stay out either way. Recommendation and default: no, Metadata only. Plan note: any permission beyond Metadata (read) is a plan amendment that needs the owner's amendment approval before Task 33 changes.
    Answer: Metadata only unless we run into a problem

## Review amendment (round 1)

**Source:** `docs/plans/REVIEW_PLAN_4.md`, revision 1 (reviewed commit `9895935`, CP1 only; four Important, five Nit)
**Amendment approved by:** <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>
**Instructions:** read this amendment, then replace the whole slug above, brackets included, with your name and the date. The planner and every other agent leave it as it is; the coder will not run the repair checkpoint while it holds a slug.

Owner decision applied (chat, 2026-11-14: "Repair all"): every finding is repaired, except where noted below. The completed CP1 tasks, their notes and acceptance lines are not changed; the failing-first run for F6 goes in Task 41's own note. Choices the owner may overrule are in the open questions.

Files added to the inventory by this amendment (all MODIFY, source under `bundles/base/`; the installed copies are refreshed by Task 56 with `install.py`, never by hand): `bundles/base/agents/planner.agent.md`, `bundles/base/agents/reviewer.agent.md`, `bundles/base/HOWTO.md`, `bundles/base/templates/INTENT_TEMPLATE.md` (comment only), `bundles/base/commands/phase-status.md`, `bundles/base/commands/phase-status.prompt.md`. `bundles/base/agents/coordinator.agent.md`, `PULL_REQUEST_TEMPLATE.md`, `REVIEW_CYCLE.md`, `phase_status.py` and the two test files are already in the inventory. Shipped text stays generic (no owner name, no "Phase 4", no "INT-27").

F3 is a coordinator action, not a coder task: the coordinator records the two refused `no-heredocs` commands of the coder (and the refused `cp`, once the owner says what it was) in `docs/agents/claude-desktop-failures.md`, by `docs/process/BREACH_PROCEDURE.md` ("How to record", step 1: the record is `docs/agents/<harness>-failures.md`) and from `docs/templates/AGENT_FAILURES_TEMPLATE.md` for the entry shape; both files exist, and `docs/agents/claude-desktop-failures.md` exists. The coder's "Rule exceptions" line is corrected in the pull request.

### CP7 — Repairs from review round 1

### Task 41 — Record a failing-first run of the five new phase-status tests

**Source:** `REVIEW_PLAN_4.md F6`
**Files:** none changed in the repository; the result goes in this task's note
**Action:** none (run and record)
**Change:** `git worktree add --detach <scratchpad>/old c6b059e`; in it, copy the five tests added in Task 11 from `bundles/base/tests/test_phase_status.py` as it is now (`git diff c6b059e..HEAD -- bundles/base/tests/test_phase_status.py` names them) into that worktree's copy with the `Edit` tool; run `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` there (use this checkout's `.venv/bin/python` by absolute path); record the counts; `git worktree remove --force <scratchpad>/old`. No shell redirect. If a step cannot be done, do not work around a guard refusal: name the step and why. Edit no test in this checkout.
**Acceptance:** the note holds the command and a failed count for the five tests on the `c6b059e` script, or one sentence naming the step that could not be done and why; `git status --short` shows no change caused by this task.
**Todo:** [ ]

---

### Task 42 — Say "tick the box and write the line" once, in the template's CI instructions

**Source:** `REVIEW_PLAN_4.md F1`
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` (the **Instructions** under "CI on the pushed commit", lines 49-52; remaining-steps instruction 2, line 70)
**Action:** MODIFY
**Change:** Recommended choice: keep both the tick and the `Confirmed by` line. In the CI **Instructions**, make step 2 read: if every run is `completed` with the conclusion `success`, write your name and the date on the **Confirmed by** line, replacing the whole slug, and then tick the box "CI of commit <full hash> is green" under "Rule exceptions"; step 3 keeps "do not write your name and do not tick" for a failed, unfinished or missing run. In remaining-steps instruction 2 keep the pointer to the CI **Instructions** ("There is no second copy here") and add "(two acts: the line and the tick)". Change no other line. Edit only the file under `bundles/base/`; the `docs/templates/` copy is refreshed in Task 56.
**Acceptance:** `grep -n "Confirmed by" bundles/base/templates/PULL_REQUEST_TEMPLATE.md` shows the instruction naming both acts in one place; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 43 — Make the review cycle agree on the two acts

**Source:** `REVIEW_PLAN_4.md F1`
**Files:** `bundles/base/process/REVIEW_CYCLE.md` (single-home table row "The CI confirmation", line 47; the name-and-date list in "Human fields and slugs", line 54; ready-check line 3, line 66)
**Action:** MODIFY
**Change:** In the table row, replace "a tick in the pull request, never a commit" with "the **Confirmed by** line and the tick of the CI line in the pull request, never a commit". In "Human fields and slugs", keep the CI confirmation in the list and add one clause that the tick of the CI line is the second act, described in the template's CI **Instructions**. In ready-check line 3, change "ticked by a human" to "ticked by a human, with the **Confirmed by** line holding a name and date and no slug". Change nothing else.
**Acceptance:** `grep -n "Confirmed by" bundles/base/process/REVIEW_CYCLE.md` shows the three places agreeing; `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 44 — Make the coordinator's CI text name both acts

**Source:** `REVIEW_PLAN_4.md F1`
**Files:** `bundles/base/agents/coordinator.agent.md` (lines 57-58, the numbered CI shape and the "for a human to tick" line)
**Action:** MODIFY
**Change:** Where the coordinator writes the CI shape, state that the human writes the **Confirmed by** line (replacing the whole slug) and then ticks the CI box, and that the coordinator does neither. Keep the sentence that the coordinator never replaces a slug, writes a name or date, ticks, or writes "approved".
**Acceptance:** `grep -n "Confirmed by" bundles/base/agents/coordinator.agent.md` shows both acts; `python3 bundles/base/tools/build.py --check` prints `lint ok` (both flavors are built from this one source).
**Todo:** [ ]

---

### Task 45 — Add a test for the two-acts wording

**Source:** `REVIEW_PLAN_4.md F1`
**Files:** `bundles/base/tests/test_bundle.py` (CREATE `test_ci_confirmation_is_the_line_and_the_tick_in_every_place`, beside `test_pr_template_has_visible_instructions_and_one_slug_shape`)
**Action:** MODIFY
**Change:** Add the test: the CI **Instructions** in `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` name the `Confirmed by` line and the tick in one step; remaining-steps instruction 2 points to them and names no second procedure; the `REVIEW_CYCLE.md` table row, the slug section and ready-check line 3, and the coordinator text each mention both the `Confirmed by` line and the tick; no one of them says the confirmation is "a tick" only. Edit no existing test.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_bundle.py -q -k ci_confirmation_is_the_line_and_the_tick` shows 1 passed; the same run before Tasks 42 to 44 shows 1 failed (record both in the note).
**Todo:** [ ]

---

### Task 46 — Word the planner, reviewer and coordinator lines to match the slug rule

**Source:** `REVIEW_PLAN_4.md F2`
**Files:** `bundles/base/agents/coordinator.agent.md` (line 36), `bundles/base/agents/planner.agent.md` (line 76), `bundles/base/agents/reviewer.agent.md` (line 82)
**Action:** MODIFY
**Change:** In each line, replace "blank" with the rule's own words: "blank or still holding a slug" (coordinator: the amendment's **Amendment approved by** is blank or holds a slug; planner: leaves **Amendment approved by** as the template has it, a slug, and never deletes or fills it; reviewer: "a blank Approved by, or one still holding a slug, is the right state of a new test plan"). Generic text only.
**Acceptance:** `grep -nE "blank" bundles/base/agents/coordinator.agent.md bundles/base/agents/planner.agent.md bundles/base/agents/reviewer.agent.md` shows each remaining "blank" on an approval line followed by "or still holding a slug" (read each hit); `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 47 — Word the guide and the intent template comment to match

**Source:** `REVIEW_PLAN_4.md F2`
**Files:** `bundles/base/HOWTO.md` (lines 35-36), `bundles/base/templates/INTENT_TEMPLATE.md` (the comment at line 18)
**Action:** MODIFY
**Change:** In `HOWTO.md` step 3 write "if it is blank or still holds a slug, asks ..." and "Write your name and the date on **Approved by**: replace the whole slug." In the `INTENT_TEMPLATE.md` comment, say to replace the whole slug on `accepted_by` with the name and date; do not move or reword the frontmatter, and the opening `---` stays the first line.
**Acceptance:** `grep -n "replace the whole slug" bundles/base/HOWTO.md bundles/base/templates/INTENT_TEMPLATE.md` prints both files; `head -1 bundles/base/templates/INTENT_TEMPLATE.md` prints `---`.
**Todo:** [ ]

---

### Task 48 — Add a test for the "blank or slug" wording

**Source:** `REVIEW_PLAN_4.md F2`
**Files:** `bundles/base/tests/test_bundle.py` (CREATE `test_agent_and_guide_text_counts_a_slug_as_blank`, beside `test_blank_approval_text_counts_a_slug_as_blank`)
**Action:** MODIFY
**Change:** Add the test over `coordinator.agent.md`, `planner.agent.md`, `reviewer.agent.md` and `HOWTO.md` (and the Copilot and skills flavors where the build writes them): each approval-line sentence that says "blank" also says "slug"; `HOWTO.md` holds "replace the whole slug"; the intent template comment holds the same phrase. Edit no existing test.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_bundle.py -q -k agent_and_guide_text_counts_a_slug` shows 1 passed (1 failed before Tasks 46 and 47; record both).
**Todo:** [ ]

---

### Task 49 — Read slugs behind list, quote and table markers, and without a colon

**Source:** `REVIEW_PLAN_4.md F5`
**Files:** `bundles/base/scripts/phase_status.py` (`slugs`, lines 49-61)
**Action:** MODIFY
**Change:** In `slugs`, before reading the field, strip a leading list marker (`-`, `*`, a number and `.`), quote marker (`>`) and table marker (`|`) and surrounding asterisks, and accept the label followed by a colon, by a `|` cell border or by a space (so `- **Confirmed by:** <slug>`, `> **Confirmed by:** <slug>`, `| **Confirmed by** | <slug> |` and `**Confirmed by** <slug>` are reported). Keep the human-field rule: a line whose label is not in `HUMAN_LABELS` is still not reported. Add a keyword argument `every=False`; when `--pr-body` input is read, call it with `every=True` and report every slug on any line (the description is a generated page; the field shown is the label if one is found, else `(description)`). Do not use `.replace(` (an existing test bans it in this script). Standard library only, read-only, sorted output.
**Acceptance:** `.venv/bin/python bundles/base/scripts/phase_status.py 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` still lists lines 54 and 105 (line numbers may shift after Tasks 42 and 53, so compare by label); `python3 bundles/base/tools/build.py --check` prints `lint ok`.
**Todo:** [ ]

---

### Task 50 — Add tests for the new slug forms

**Source:** `REVIEW_PLAN_4.md F5`
**Files:** `bundles/base/tests/test_phase_status.py` (CREATE `test_slugs_are_found_behind_list_quote_and_table_markers`, `test_pr_body_reports_every_slug`, `test_prose_slug_in_a_plan_is_still_not_reported`)
**Action:** MODIFY
**Change:** The first test feeds the four forms from the review (list item, quote, table row, no colon) plus the three forms that already worked and expects each to be reported with its label; the second feeds a description with a slug on a line with no human label and expects it reported under `--pr-body`; the third feeds a plan whose task `Change` line quotes a slug as an example and expects none. Edit no existing test.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q` shows all passed with the three new tests counted; the first two fail on the script before Task 49 (record the counts).
**Todo:** [ ]

---

### Task 51 — Update the phase-status command text for `--pr-body` and the intent limit

**Source:** `REVIEW_PLAN_4.md F7`, `REVIEW_PLAN_4.md F5` (intent files are not read)
**Files:** `bundles/base/commands/phase-status.md` (`description`, line 2, and the body sentence), `bundles/base/commands/phase-status.prompt.md` (`description`, line 3, the body and the `Limit:` paragraph)
**Action:** MODIFY
**Change:** In both files change the `description` to "List what is still open in a phase (read-only). Usage /phase-status <phase number> [--pr-body <file>]" and the body sentence to say the script reads the plan, test plan and review files, and the pull request description when `--pr-body <file>` is given, and does not read intent files (an unreplaced `accepted_by` slug is found only by reading the intent). In the Copilot prompt, state whether `${input:phase}` can carry `4 --pr-body <file>`: read the VS Code prompt-file documentation (reference for `${input:...}`) and state what it says with its source; if it cannot be read, write "unverified: confirm with the VS Code prompt-file documentation" in the `Limit:` paragraph and do not claim it works. Keep `.claude/commands/phase-status.md` for Task 56 (refresh).
**Acceptance:** `grep -n "pr-body" bundles/base/commands/phase-status.md bundles/base/commands/phase-status.prompt.md` shows it in `description`, `argument-hint` and the body of each file; the Copilot file holds either the documented sentence with its source or the word "unverified".
**Todo:** [ ]

---

### Task 52 — Add a test for the command text

**Source:** `REVIEW_PLAN_4.md F7`
**Files:** `bundles/base/tests/test_phase_status.py` (CREATE `test_command_files_describe_pr_body_and_the_intent_limit`)
**Action:** MODIFY
**Change:** Add the test: both command files carry `--pr-body` in `description`, `argument-hint` and the body, and the sentence that intent files are not read; the Copilot file carries either a cited sentence or "unverified" about the input. Edit no existing test.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_phase_status.py -q -k command_files_describe` shows 1 passed (1 failed before Task 51; record both).
**Todo:** [ ]

---

### Task 53 — Cite or mark the Approve review click path

**Source:** `REVIEW_PLAN_4.md F8`
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` (remaining-steps instruction 4, line 72), `bundles/base/process/REVIEW_CYCLE.md` (line 50)
**Action:** MODIFY
**Change:** Read GitHub's documentation page on reviewing proposed changes in a pull request (the coder finds the page; record its URL and what it says about the Files changed tab, "Review changes" and the Approve choice in this task's note). If it confirms the click path, add the link after the sentence in the template and in `REVIEW_CYCLE.md`. If it cannot be read or does not say it, add "(unverified: confirm with GitHub's documentation)" after the click path in both places. Make no claim about whether an author can approve their own pull request (the existing test forbids "own pull request", "self-approv" and "cannot approve"). Name no repository, owner or bypass in this shipped text: the owner's bypass route stays in this repository's own pull request text and `docs/process/BRANCH_RULES.md` (not shipped, not changed here).
**Acceptance:** `grep -n "Review changes" bundles/base/templates/PULL_REQUEST_TEMPLATE.md bundles/base/process/REVIEW_CYCLE.md` shows a link or the word "unverified" in both; `git diff bundles/base | grep -iE "bypass|Michael|mediumroast"` prints nothing.
**Todo:** [ ]

---

### Task 54 — Add a test for the Approve review wording

**Source:** `REVIEW_PLAN_4.md F8`
**Files:** `bundles/base/tests/test_bundle.py` (CREATE `test_approve_review_step_is_linked_or_marked_unverified`)
**Action:** MODIFY
**Change:** Add the test: the Approve review step in the template and in `REVIEW_CYCLE.md` holds either an `https://docs.github.com/` link or the word "unverified"; none of "bypass", "own pull request", "self-approv" or "cannot approve" appears in either shipped file. Edit no existing test.
**Acceptance:** `.venv/bin/python -m pytest bundles/base/tests/test_bundle.py -q -k approve_review_step` shows 1 passed (1 failed before Task 53; record both).
**Todo:** [ ]

---

### Task 55 — Put the slug in a code span, only if the owner's preview shows it hidden

**Source:** `REVIEW_PLAN_4.md F4`
**Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` (the two slug lines, 54 and 105), `bundles/base/tests/test_bundle.py` (`test_pr_template_has_visible_instructions_and_one_slug_shape`, pattern check only)
**Action:** MODIFY
**Gate (owner):** the owner pastes the template into a comment on any pull request or issue and reads the preview without posting it. Who: the owner only; no agent previews, posts or reads a comment for this. Run this task only if the preview shows the `<Insert ...>` text hidden or the line empty. If the slug is visible, mark this task `[~]` with the owner's result in the note and do nothing else.
**Change:** Wrap each of the two slugs in a code span (backticks). Change the pattern check of the named test to accept the span (the detection regex in `phase_status.py` already finds a slug inside a code span, so no script change). Record the owner's preview result in this task's note. Same wording for the other slugs in the plan, test-plan and intent templates is not changed here: they are read as text in the repository, not in the rendered description.
**Acceptance:** `.venv/bin/python bundles/base/scripts/phase_status.py 4 --pr-body bundles/base/templates/PULL_REQUEST_TEMPLATE.md` still lists both slugs; `.venv/bin/python -m pytest bundles/base/tests -q -k "pr_template"` passes.
**Todo:** [ ]

---

### Task 56 — Refresh this repository's own install from the build

**Source:** `REVIEW_PLAN_4.md F1, F2, F7, F8` (and F4 if Task 55 ran)
**Files:** `docs/templates/PULL_REQUEST_TEMPLATE.md`, `docs/templates/INTENT_TEMPLATE.md`, `docs/process/REVIEW_CYCLE.md`, `.claude/agents/*` (coordinator, planner, reviewer), `.claude/commands/phase-status.md`, `.manifold/phase_status.py`, `.manifold/manifest.json`, and the HOWTO copy if installed
**Action:** MODIFY (generated by `install.py`, never by hand)
**Change:** Exactly as Task 13 did: `python3 bundles/base/tools/build.py --out <scratchpad>/dist`, unzip into a fresh scratchpad folder, read `install.py --help`, run `install.py --target . --format claude --profile build` as a dry run (expect UPDATE for only the files above, SKIP for the rest), then with `--apply` and no `--force`. If the guard refuses a write to an agent definition from this non-main worktree, STOP, report the refused path and that a human must grant a path exception (`.manifold/guard-allow.json`); do not work around it. Stage explicit paths only.
**Acceptance:** `cmp bundles/base/templates/PULL_REQUEST_TEMPLATE.md docs/templates/PULL_REQUEST_TEMPLATE.md`, the same for `INTENT_TEMPLATE.md`, and `cmp bundles/base/process/REVIEW_CYCLE.md docs/process/REVIEW_CYCLE.md` print nothing; `cmp bundles/base/scripts/phase_status.py .manifold/phase_status.py` prints nothing; every installed file's sha256 equals its entry in `.manifold/manifest.json`; `install.py --status` from the unzipped bundle reports no MODIFIED file.
**Todo:** [ ]

---

**Verification:** from the repository root, `python3 bundles/base/tools/build.py --check` prints `lint ok`; `.venv/bin/python -m pytest bundles/base/tests -q` passes (counts reported, new tests counted); `.venv/bin/python tools/vendor_web.py --check` prints "vendored files match a fresh build"; `.venv/bin/python bundles/base/scripts/phase_status.py 4 --pr-body docs/templates/PULL_REQUEST_TEMPLATE.md` lists the same two slugs by label; then the `reviewer` writes a second review revision (revision 2) of `REVIEW_PLAN_4.md` for the repair commits.

Rule exceptions (Tasks 41 to 56): to be filled in by the coder.

**Findings not repaired:**

| Finding | End | Reason |
|---|---|---|
| `F3` | repaired outside this plan | a coordinator action (see above), not a coder task |
| `F9` | rejected (no repair) | history is not rewritten; Task 13 out of order is recorded; only the owner's answer to Open question 6 is open |

**Open questions:**

1. **Keep both the `Confirmed by` line and the tick for the CI confirmation, or only one?** What: Tasks 42 to 45 make the person write the line and tick the box, said in one place. Why: the review found the text told the person to write the line, while the ready check needs a tick. Consequence: if you choose one, Tasks 42 to 45 change (drop the other act from the template, `REVIEW_CYCLE.md`, the coordinator text and the test) and the ready check moves to that single act. Recommendation: both (your own worked example in the intent has the line; the ready check needs a tick). Default: both.
   Answer:
2. **What was the refused `cp` the coder tried?** What: it is not in the guard log, so the coordinator cannot record it. Why: F3. Consequence: without your answer it is left out of the failures record and noted as unknown. Recommendation: say what it copied, or "unknown". Default: recorded as unknown.
   Answer:
3. **What does GitHub's comment preview show for the slug?** What: paste the template in a comment, read the preview, do not post, and report whether the `Confirmed by` slug is visible. Why: F4 (Task 55). Consequence: hidden means Task 55 runs; visible means it is marked `[~]`; no answer leaves F4 open and the release goes out with the risk. Recommendation: preview before release (about a minute). Default: Task 55 stays unrun and F4 stays open.
   Answer:
4. Open question 6 of the plan above (how `/phase-status` reads the description) still has an empty answer (F9). Nothing changes if you leave it; the default (option a) was built.

