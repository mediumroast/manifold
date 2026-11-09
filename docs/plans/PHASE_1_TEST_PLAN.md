# PHASE_1_TEST_PLAN.md

**Approved by:** Michael Hay on November 9, 2026

## Purpose

This plan certifies Phase 1 (security baseline and local installer). Passing means three things. First, the three gate commands pass clean. Second, the gap checks below, which the builders' tests do not cover, pass. Third, a human has run the manual cases below on real clients and a real Docker host. This plan adds only what the existing suite (56 files under `server/tests/`) misses.

## Source

**Phase plan:** `PHASE_1_PLAN.md`
**Tasks covered:** Tasks 2-33, 35 and 37-58 (Task 34's documents are checked by A13 only; its HTTPS client observation is excluded below).

**Tasks excluded:**

- Task 1 (`[~]`): the Linux SQLite probe is not run. The owner is deferring it: "we're accruing this tech debt till later".
- Task 34 (`[~]`): connecting Claude Code, VS Code and a browser over HTTPS, and the upgrade walk-through, are not planned. Same owner reason.
- Task 36 (`[~]`): the Linux walk-through is not planned. Same owner reason.
- Out of scope: GitHub parts of INT-6, INT-7, INT-14, INT-18 and INT-19, per the phase plan.

## Source intents

- `INT-1` Security baseline for the Manifold server (accepted 2026-11-01). Seeds S1-S16; all constraints; all "Must never" lines.
- `INT-6` An installer that takes you from nothing to a working instance (accepted 2026-11-01). Local part only: S1, S2, S4 and the constraints. S3 and "GitHub through its API" are deferred.

## Coverage judgement

| Seed or constraint                                                                                          | Existing test                                                                                  | Judgement      | Reason                                                                                            |
| ----------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------- |
| INT-1 S1 own credential, never shown again                                                                  | `test_tokens`, `test_cli_principals`, `test_auth_middleware`                                   | adequate       | Hash only at rest, shown once, revoke affects one credential. Not checked in git history: see A7. |
| S2 agent acts only for its component                                                                        | `test_handoff_authz`, `test_tool_authz`, `test_handoff_forgery`                                | adequate       |                                                                                                   |
| S3 every change names who                                                                                   | `test_principal_attribution`, `test_log_forgery`                                               | adequate       | Registration values: A8.                                                                          |
| S4 guessing slowed, nothing revealed                                                                        | `test_throttle`, `test_auth_middleware`, `test_audit`                                          | thin           | The secret is checked in the audit, not in process logs (A3).                                     |
| S5 wrong host or origin                                                                                     | `test_request_guard`                                                                           | adequate       |                                                                                                   |
| S6 no unprotected network start                                                                             | `test_startup`                                                                                 | thin           | Look-alike host names and empty settings: A10.                                                    |
| S7 TLS is a setting                                                                                         | `test_deploy_files`                                                                            | thin           | Docs never advise turning off certificate checks: A13.                                            |
| S8 retiring the shared token                                                                                | `test_startup`, `test_deploy_files`, `test_auth`                                               | adequate       |                                                                                                   |
| S9 admin cannot read                                                                                        | `test_tool_policy`, `test_tool_authz`                                                          | thin           | Browser routes (A6) and `/health` detail (A4).                                                    |
| S10 registrar                                                                                               | `test_registrar`, `test_tool_authz`                                                            | thin           | Multi-line values: A8.                                                                            |
| S11 deliberate retirement, limits                                                                           | `test_component_manage`, `test_registrar`, `test_cli_purge`                                    | thin           | Limits are tested only in sequence: A9.                                                           |
| S12 shared pages                                                                                            | `test_tool_authz`                                                                              | adequate       |                                                                                                   |
| S13 works offline                                                                                           | `test_offline_clean` (import scan)                                                             | thin           | No runtime check: A11.                                                                            |
| S14 immediate revocation                                                                                    | `test_revocation_smoke`                                                                        | thin           | Open SSE session after revoke: A12.                                                               |
| S15 only the source closes                                                                                  | `test_handoff_authz`, `test_docs_links`                                                        | adequate       |                                                                                                   |
| S16 page written only where allowed                                                                         | `test_path_policy`, `test_ingest`                                                              | thin           | In-root symlinks (A1, A2) and browser routes (A5).                                                |
| Constraints: safe by default, no off switch, no new service, portable store, TLS switch, limits as settings | `test_startup`, `test_security_store`, `test_cli_export`, `test_deploy_files`, `test_settings` | adequate       |                                                                                                   |
| Constraint: secrets stay out of the wiki                                                                    | `test_tokens`, `test_audit`, `test_init`                                                       | thin           | A3, A7.                                                                                           |
| Constraint: client compatibility                                                                            | `test_auth` (Basic, Bearer)                                                                    | thin           | Real clients are manual: M1, M2.                                                                  |
| Constraint: revocation durable                                                                              | `test_revocation_smoke`, `test_store_locks`                                                    | adequate       |                                                                                                   |
| INT-6 S1, S2, S4 and constraints                                                                            | `test_init` (40 cases)                                                                         | adequate       | Real Docker is manual: M4. Linux is excluded.                                                     |
| INT-1 S6 "short or default credential"                                                                      | none                                                                                           | not applicable | Credentials are generated and cannot be supplied.                                                 |

## Gaps found

- A1, A2: in-root symlinks. Probe evidence: `scopes.classify` returned `('component','acme-api')` for a symlink to `manifold.yaml`. Expected outcome is refusal; if the test fails it is a defect.
- A3, A7: the credential in logs and in git.
- A4: `/health` detail. Plan T10 says detail goes only to "an authenticated reader". The code (`server.py`, `detailed = caller_from_scope(...) is not None`) gives it to any valid credential, so A4 should fail for an admin-only principal.
- A5, A6: browser routes.
- A8: multi-line registration values.
- A9: concurrent limits.
- A10: start rule with unusual hosts.
- A11: runtime offline check.
- A12: SSE session after revoke.
- A13: docs advising certificate checks off.
- M1-M4: real clients and a real Docker run.

## Test environment

**Verify command:** none exists (no lint or type-check). The gate is the three commands below.
**Test command:** `cd server && ../.venv/bin/python -m pytest -q`; also `.venv/bin/python -m pytest bundles/base/tests -q` and `.venv/bin/python tools/vendor_web.py --check`.
**Environment variables / fixtures required:**

- Install first: `python3 -m venv .venv`, then `.venv/bin/pip install -r server/requirements-dev.txt -c server/requirements.lock` (the worktree has no `.venv`).
- Fixtures: `tool_world`, `auth_world`, `wiki_root`, `security_conn` (`conftest.py`) and `ServerProcess` (`realserver.py`).
- Docker only for M3 and M4.

**Seed and sample size:** A9: 4 processes x 3 calls, limit 5, no randomness. Otherwise not applicable.

## Checkpoints

The phase plan has no checkpoint table; CP1-CP7 are derived from the `CP<n>` labels in its task notes (CP7 is the planner's grouping of the review amendment). Every gate is the three commands from `AGENTS.md` "Project commands" (server tests, bundle tests, vendored web files check).

| Checkpoint | Phase-plan tasks | Gate                    |
| ---------- | ---------------- | ----------------------- |
| CP1        | Task 2-7         | the three gate commands |
| CP2        | Task 8-11        | the three gate commands |
| CP3        | Task 12-18       | the three gate commands |
| CP4        | Task 19-27       | the three gate commands |
| CP5        | Task 28-30       | the three gate commands |
| CP6        | Task 31-35       | the three gate commands |
| CP7        | Task 37-58       | the three gate commands |

No new automated case for CP1, CP5 or CP7. No REGRESSION cases are planned: every earlier defect already has a failing-first test in its task note.

## Manual test cases

### M1 — Browser Basic prompt

**Checkpoint:** CP2
**Related task:** Task 10
**Derived from:** INT-1 constraint "Client compatibility" (a browser keeps working with the standard sign-in prompt); plan T10 acceptance (Basic works)
**Existing or new:** new (extends `test_auth.py::test_a_browser_can_use_basic_authentication`, which cannot show a real prompt)
**Precondition:** A server runs on `127.0.0.1` with one reader principal and a credential. A browser is available.
**Steps:**

1. Open `http://127.0.0.1:<port>/docs/` with no credential.
2. Cancel the prompt.
3. Reload, enter any username and the credential as the password.
4. Revoke the credential with the host command, then reload.
   **Expected outcome:** A native sign-in prompt appears; cancelling shows a plain refusal. The correct credential shows the wiki. After revoke, the next reload prompts again or is refused.
   **Pass criteria:** All four observations match.
   **Result:** [ ] Pass  [ ] Fail  [ ] Blocked
   **Notes:**

---

### M2 — Claude Code and VS Code with a bearer header

**Checkpoint:** CP2
**Related task:** Task 10
**Derived from:** INT-1 constraint "Client compatibility"
**Existing or new:** new
**Precondition:** Same server. `examples/clients/claude-code-mcp.json` and `vscode-mcp.json` are filled with the credential.
**Steps:**

1. Connect Claude Code and call `wiki_ping_tool`.
2. Connect VS Code (GitHub Copilot) and call `wiki_ping_tool`.
3. Repeat each with a wrong credential.
   **Expected outcome:** Each client connects and ping returns the principal name. With a wrong credential each client shows an authentication failure.
   **Pass criteria:** Both clients work with the right credential and fail with the wrong one.
   **Result:** [ ] Pass  [ ] Fail  [ ] Blocked
   **Notes:**

---

### M3 — Plain HTTP on a network address shows a visible warning

**Checkpoint:** CP5
**Related task:** Task 29
**Derived from:** INT-1 S7 Must never ("TLS turned off on a shared address without a visible warning"); plan T29
**Existing or new:** new (`test_deploy_files` asserts text, not visibility)
**Precondition:** A Docker environment file exists with a non-loopback `BIND_ADDRESS` and `MANIFOLD_TLS=off`.
**Steps:**

1. Run `./svc_ctl.sh <env> start` without `MANIFOLD_ALLOW_PLAIN_ON_NETWORK`.
2. Run it with `MANIFOLD_ALLOW_PLAIN_ON_NETWORK=yes`.
   **Expected outcome:** Step 1 refuses to start and says why. Step 2 starts and prints a warning that a person reading the terminal notices.
   **Pass criteria:** Both outcomes observed; the tester judges the warning visible.
   **Result:** [ ] Pass  [ ] Fail  [ ] Blocked
   **Notes:**

---

### M4 — `manifold init` on a Docker machine, twice

**Checkpoint:** CP6
**Related task:** Task 33
**Derived from:** plan T33 acceptance ("to be covered by the test plan"); INT-6 S1, S2, S4
**Existing or new:** new (`test_init.py` uses a fake runner without Docker)
**Precondition:** Docker with Compose runs. An empty temporary folder, a free port, and no earlier settings file.
**Steps:**

1. Run `./manifold init --yes --instance <dir> --data-dir <dir2> --port <port> --name <name> --person-secret-file <f1> --agent-secret-file <f2>`.
2. Record checksums of the instance, the credential files and the settings file.
3. Run the same command again.
4. Compare the checksums, then run `./svc_ctl.sh <env> stop`.
   **Expected outcome:** Run 1 ends with a healthy server, two components and a handoff read back. Both credential files are mode 0600. Run 2 prints the plan with what already exists and changes nothing.
   **Pass criteria:** Checksums are identical after run 2. No credential is printed.
   **Result:** [ ] Pass  [ ] Fail  [ ] Blocked
   **Notes:**

---

## Automated test cases

### A1 — Write through an in-root symlink is refused

**Checkpoint:** CP2
**Related task:** Task 9
**Derived from:** INT-1 S16 Must never; constraint "The server writes only where it should"
**Existing or new:** new
**Precondition:** `wiki_root` fixture. Symlinks inside it: `wiki/components/acme-api.md -> manifold.yaml`, `wiki/components/acme-web.md -> wiki/log.md`, `wiki/decisions/d.md -> wiki/components/acme-web.md`. Caller holds a write grant on `acme-api` and `_shared`.
**Action:** Call `wiki_write_page` on each of the three paths.
**Expected outcome:** Each returns `status == "error"` with a refusal reason. The link targets are byte-identical afterwards and `git status` is clean.
**Test file:** `server/tests/test_path_policy.py`
**Todo:** [x] Written (`test_A1_...`, 3 links x create/update-with-etag). RED, defect: with an etag, all three links return `updated` (the write goes through the link); without an etag they return `conflict`, not `error`. Added grant on `acme-web` (needed so the second link is refused for being a link) and the etag variant.
**Owner decisions (2026-11-09, review F2, F3):** (F2) `conflict` does NOT count as a refusal for a create through a symlink; the create variants keep asserting `status == "error"` and stay red until the code refuses before the existence check (owner-confirmed 2026-11-09). (F3) The etag in the update variants is now computed without `wiki_read`: `hashlib.sha256` of the link's bytes (the backend's `generate_etag` is sha256 of the file text), so A1 no longer depends on A2's defect. After the change the three update-with-etag variants still fail on `assert 'updated' == 'error'` (status `updated`, the write went through the link); the three create variants fail on `assert 'conflict' == 'error'`.

---

### A2 — Read through an in-root symlink is refused

**Checkpoint:** CP2
**Related task:** Task 9
**Derived from:** Plan D6 (reads confined; `manifold.yaml` and `.git/config` unreadable)
**Existing or new:** new
**Precondition:** `wiki_root` fixture. `wiki/a.md -> .git/config` and `wiki/b.md -> manifold.yaml`.
**Action:** Call `wiki_read` on `wiki/a.md` and `wiki/b.md`.
**Expected outcome:** Both raise `ValueError` or `FileNotFoundError`; no content is returned.
**Test file:** `server/tests/test_path_policy.py`
**Todo:** [x] Written (`test_A2_...`). RED, defect: `wiki_read` on `wiki/a.md -> .git/config` and `wiki/b.md -> manifold.yaml` raises nothing (content returned).

---

### A3 — A presented credential never appears in process logs or responses

**Checkpoint:** CP2
**Related task:** Task 10
**Derived from:** INT-1 S4 Must never (guess not written to the log); constraint "Secrets stay out of the wiki"
**Existing or new:** new (`test_audit` checks only audit rows)
**Precondition:** In-process app with log capture at DEBUG, and a real `ServerProcess` with its log. Credentials to try: a wrong one, a malformed one, a revoked one, and one presented while throttled. Each is sent as Bearer and as Basic.
**Action:** Send each request, then read all captured log text, all response bodies and headers, and the server process log.
**Expected outcome:** No presented secret and no `Authorization` header value appears anywhere.
**Test file:** `server/tests/test_secret_hygiene.py` (new)
**Todo:** [x] Written (two tests: in-process with DEBUG log capture; real `running_server` with `server.log`). GREEN, 2 passed. Revoked/wrong/malformed/throttled, each as Bearer and Basic; the in-process test asserts a 429 occurred. Caveat: a passing test only shows no leak through the logger output captured and the server log.

---

### A4 — `/health` detail is for an authenticated reader only

**Checkpoint:** CP2
**Related task:** Task 10
**Derived from:** Plan T10: "`/health` stays open and shows detail only to an authenticated reader"; INT-1 S9
**Existing or new:** new (extends `test_auth_middleware.py::test_health_is_open_and_marks_the_caller_only_when_the_credential_is_good`)
**Precondition:** Principals: an admin-only one, a reader, a disabled reader. Each has a credential.
**Action:** `GET /health` with no credential, with a wrong credential, and with each valid credential.
**Expected outcome:** Anonymous, wrong-credential and admin-only callers get only the brief status, with no checks or detail. The reader gets the detailed checks. Expected to fail today for the admin-only principal, because the code accepts any valid credential.
**Test file:** `server/tests/test_auth_middleware.py`
**Todo:** [x] Written (`test_A4_...`). RED, defect as predicted: an admin-only principal gets the detailed `checks` payload from `/health`. The reader of the fixture is the agent `build-bot`.
**Fixed:** bug-coder, server/server.py: /health now needs the read capability for the detail (_store_access.authorize(..., authorizer.READ, ...)); A4 is green; full suite 12 failed (A1, A2, A8), 1048 passed. Side effect accepted by the owner (2026-11-09): each admin-only call to /health writes one authorizer.refusal audit row, not throttled. Owner-confirmed 2026-11-09.

---

### A5 — Browser routes refuse traversal and escaping symlinks

**Checkpoint:** CP3
**Related task:** Task 12
**Derived from:** INT-1 constraint "Paths that leave the wiki folder are refused"; S16. See Q3.
**Existing or new:** new
**Precondition:** The app with a reader credential. Symlinks `wiki/leak.md -> ../manifold.yaml` and `wiki/g.md -> .git/config`.
**Action:** As the reader, GET `/docs/..%2fmanifold.yaml`, `/docs/../manifold.yaml`, `/docs/raw/../../manifold.yaml`, `/docs/leak.md` and `/docs/g.md`.
**Expected outcome:** Each answers 4xx and no response body contains registry or git config content.
**Test file:** `server/tests/test_docs_route_policy.py` (new)
**Todo:** [x] Written (5 params). GREEN. Not seen failing: no production change allowed; a probe showed an in-root symlink is served 200 and an escaping one 404, so the check is not vacuous. The app is the real `_build_docs_routes` for a temp instance behind the real auth and route-policy middleware.

---

### A6 — Browser routes refuse an admin-only principal

**Checkpoint:** CP3
**Related task:** Task 12
**Derived from:** INT-1 S9; plan T12 (`/docs/**` and `/docs/raw/**` need `read`)
**Existing or new:** new (extends `test_tool_policy.py::test_the_wiki_browser_needs_the_read_capability`, which covers `/docs/log.md` only)
**Precondition:** Admin-only principal and a reader, each with a credential.
**Action:** GET `/docs/`, `/docs/index.html`, `/docs/raw/<existing file>`, and a vendor asset under `/docs/_manifold/vendor/`.
**Expected outcome:** Admin-only: 403 on each. Reader: 200. No credential: 401.
**Test file:** `server/tests/test_docs_route_policy.py`
**Todo:** [x] Written (4 paths: admin 403, reader 200, anonymous 401). GREEN. Not seen failing (same reason as A5).

---

### A7 — The credential never reaches git history or the wiki

**Checkpoint:** CP3
**Related task:** Task 15
**Derived from:** INT-1 constraint "Secrets stay out of the wiki"; S3
**Existing or new:** new
**Precondition:** Real `ServerProcess` on a temporary instance with a contributor and a registrar credential.
**Action:** With those credentials, write a page, append a log entry, register a component, create a handoff and ingest a document. Then run `git log --all -p` and read every file in the instance.
**Expected outcome:** Neither secret appears in any output or file. Commit authors and trailers name the principals.
**Test file:** `server/tests/test_secret_hygiene.py`
**Todo:** [x] Written (`test_A7_...`; real server, MCP over /mcp plus POST /ingest, then `git log --all -p` and every file in the instance). GREEN; the tool calls all succeeded. Not seen failing (no production change allowed). Commit authors `alice` and `reg` asserted.
**Review F1 fix (2026-11-09):** the secret part is taken with `split("_", 2)[2]` (the token secret can contain `_`), so the needle is the full secret. `pytest tests/test_secret_hygiene.py -k A7` run 35 times, each in a separate process: 35 passed, 0 failed (the reviewer saw 5 of 35 fail before the fix).

---

### A8 — A multi-line registration value never becomes more than one entry

**Checkpoint:** CP3
**Related task:** Task 16 and Task 17
**Derived from:** `REVIEW.md` Security rule (one caller value must never become more than one entry or key); INT-1 S10, S3. See Q4.
**Existing or new:** new
**Precondition:** `tool_world` with a human registrar.
**Action:** Call `wiki_register_component_tool` and `wiki_component_manage_tool(update)` with `description`, `repo` and `owner` containing `\n`, `: `, `## ` and `- [x](y)`.
**Expected outcome:** Either an error result with nothing changed, or the value stored encoded on one line. In both cases `manifold.yaml` gains at most one entry, the component page has exactly one `**Repository:**` line, and the sidebar, index, log and commit subject each gain at most one entry. A reload of the registry shows no extra key or component.
**Test file:** `server/tests/test_register_untrusted_values.py` (new)
**Todo:** [x] Written (3 fields x register, 3 fields x update). RED on 4 of 6, defects found (seen failing as written). Register with hostile `description`: `wiki/index.md` grows by 6 lines (benign: 1). Register with hostile `repo` or `owner`: the component page gets a heading and extra frontmatter keys (`key`, ...). Update with hostile `repo`: the page gets an injected `## Injected heading`. Update of description and owner pass (one-line encoding). The bound "at most one" is measured against a benign registration and update run first in the same instance (Q4: either outcome accepted).

---

### A9 — Concurrent registrations cannot exceed the daily limit

**Checkpoint:** CP3
**Related task:** Task 18
**Derived from:** INT-1 S11 Must never (exceed daily limits)
**Existing or new:** new (`test_registrar -k limit` is sequential)
**Precondition:** A store with an agent principal and `agent_registrations_per_day=5`.
**Action:** 4 separate processes, each with its own connection, call `limits.consume` 3 times (12 calls).
**Expected outcome:** Exactly 5 are allowed and 7 refused. The usage row reads 5. Refusals name the setting.
**Test file:** `server/tests/test_limits_concurrency.py` (new)
**Todo:** [x] Written (4 spawned processes x 3 calls, limit 5, shared start time). GREEN: 5 allowed, 7 refused naming the setting, usage 5, no lock errors. Not seen failing. Seed: none.

---

### A10 — The start rule holds for look-alike and empty hosts

**Checkpoint:** CP4
**Related task:** Task 21
**Derived from:** INT-1 S6 Must never (start on a shared address because a setting was left empty)
**Existing or new:** new
**Precondition:** An empty store.
**Action:** `check_startup` and `server._check_auth_settings` with `MANIFOLD_HOST` of `localhost.evil.test`, `127.0.0.1.nip.io` and `0`. Then with `MANIFOLD_HOST=0.0.0.0` and `MANIFOLD_PUBLIC_ADDRESS=""`. Then with `MANIFOLD_HOST=""`.
**Expected outcome:** The first four refuse to start naming `./manifold init`. The empty `MANIFOLD_HOST` starts with a warning and the app refuses every request.
**Test file:** `server/tests/test_startup.py`
**Todo:** [x] Written (`test_A10_...`, 5 tests). GREEN. Not seen failing. `check_startup` is called with the empty `MANIFOLD_HOST` only through `server._check_auth_settings` (env `""` becomes None); `check_startup(conn, "")` directly would refuse. Observation, unverified: `server.py` main passes `os.getenv("MANIFOLD_HOST", "127.0.0.1")` to uvicorn, which is `""` when the variable is set empty; what uvicorn binds then was not checked.

---

### A11 — No outside connection at run time

**Checkpoint:** CP4
**Related task:** Task 21
**Derived from:** INT-1 S13 and constraint "Offline-clean"
**Existing or new:** new (`test_offline_clean` scans imports only)
**Precondition:** `socket.socket.connect` and `socket.getaddrinfo` are patched to raise for any non-loopback target and to record attempts.
**Action:** Start the app, then call one tool of each kind (read, write, handoff, register, archive), `POST /ingest`, `/health` and `/docs/`.
**Expected outcome:** Every call works and no non-loopback connection is attempted.
**Test file:** `server/tests/test_offline_clean.py`
**Todo:** [x] Written (`test_A11_...`). GREEN: all calls worked and no non-loopback `connect` or `getaddrinfo` was attempted. Not seen failing. Caveat: tools run in-process through the MCP client; HTTP routes through Starlette's in-process test client, so only socket calls made by the server code itself are observed.

---

### A12 — An open SSE session is cut off by revocation

**Checkpoint:** CP4
**Related task:** Task 27
**Derived from:** INT-1 S14
**Existing or new:** new (`test_revocation_smoke` covers `/docs` and `/ingest` only)
**Precondition:** Real `ServerProcess`; two contributor credentials. Credential A opens `/sse` and holds the session id.
**Action:** A posts a call to `/messages/` (works). Revoke A with the host command and POST again. Repeat with a deny on the component instead of a revoke.
**Expected outcome:** The POST after revoke is 401. The POST after a deny returns a refusal result. The tool does not run, and nothing is written. Credential B still works.
**Test file:** `server/tests/test_revocation_smoke.py`
**Todo:** [x] Written (`test_A12_...`, raw `/sse` sessions, JSON-RPC over `/messages/`). GREEN: 401 after revoke, refusal result after deny, nothing written (page and HEAD unchanged), second principal unaffected. Not seen failing. `test_revocation_smoke.py` passed 5 of 5 (53 s).

---

### A13 — The docs never advise turning off certificate checks

**Checkpoint:** CP6
**Related task:** Task 34 and Task 35
**Derived from:** INT-1 S7 Must never
**Existing or new:** new (the existing check scans the CI workflow only)
**Precondition:** The documents in `test_docs_links.DOCS` and `examples/clients/*.json`.
**Action:** Scan code blocks and instructions for `--insecure`, `curl -k`, `NODE_TLS_REJECT_UNAUTHORIZED`, `rejectUnauthorized`, `verify=False` and `sslVerify false`. A sentence that warns against doing so is allowed.
**Expected outcome:** No recommendation to disable certificate checks.
**Test file:** `server/tests/test_docs_certificate_checks.py` (new)
**Todo:** [x] Written (one param per document, plus a check that the scan catches a recommendation and allows a warning). GREEN. The only hit is the warning in `docs/tls.md`. Seen failing in the scanner self-check (a sample recommendation is caught), not against the repository documents.

---

## Questions for the human

### Q3 — Is the `/docs` browser route in scope for path confinement?

D6 names `wiki_read` only, and the constraint "paths that leave the wiki folder are refused" is written about writes. A5 assumes the browser route is in scope.
**Blocking:** no
**Answer:** yes in scope

### Q4 — Refuse or encode a newline in registration values?

A8 accepts either a refusal or encoding on one line.
**Blocking:** no
**Answer:** Either; the test enforces one entry per value. Decide when A8 first shows what the code does.

## Quality gates (all must pass before the phase is certified complete)

- [ ] All manual test cases marked Pass by a human tester
- [ ] All automated tests passing (`cd server && ../.venv/bin/python -m pytest -q`)
- [ ] `.venv/bin/python -m pytest bundles/base/tests -q` and `.venv/bin/python tools/vendor_web.py --check` pass clean (no lint or type-check exists)
- [ ] No [~] blocked test cases outstanding without a documented reason
- [ ] No blocking question is open
- [ ] **Approved by** is filled in by a human before the test-coder starts
- [ ] Summary signed off by tester below this line

## Automation summary (test-coder)

All 13 automated cases (A1-A13) are written and run. Command per touched file set: `cd server && ../.venv/bin/python -m pytest -q <the ten files>` gave 13 failed, 166 passed. The full suite and the three gate commands were not run (the human's job).

Red, defects found (checks left as written): A1 (write through an in-root symlink succeeds with an etag; `conflict` without), A2 (read through an in-root symlink returns content), A4 (`/health` detail for an admin-only principal), A8 (4 of 6: hostile `description` grows `index.md`; hostile `repo` or `owner` injects headings and frontmatter keys on registration; hostile `repo` injects a heading on update). Green: A3, A5, A6, A7, A9, A10, A11, A12, A13. Manual cases M1-M4 are not implemented.

Files: `test_path_policy.py`, `test_auth_middleware.py`, `test_startup.py`, `test_offline_clean.py`, `test_revocation_smoke.py` (extended); `test_secret_hygiene.py`, `test_docs_route_policy.py`, `test_register_untrusted_values.py`, `test_limits_concurrency.py`, `test_docs_certificate_checks.py` (new). No new shared fixture.

Deferred (owner, 2026-11-09, review F4): the green cases A3, A5, A6, A7, A9, A11, A12, A13 were not seen failing. Reason: no production change is allowed in this task, so a failing run could not be produced without one. Root cause of the gap and the value of adding a negative check for each are unknown. No new test written.

Deferred (owner, 2026-11-09, review F5): A10's empty `MANIFOLD_HOST` case is checked only through `_check_auth_settings()`. What uvicorn binds when the variable is set empty is unverified. No new test written.

Rule exceptions: one attempted heredoc in a Bash command, refused by the guard hook before it ran (no file written); otherwise none.
