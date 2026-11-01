# PHASE_1_PLAN.md

**Approved by:**
**Source intent:** [INT-1 Security baseline for the Manifold server][i1] (status accepted, accepted_by Michael Hay 2026-11-01), all of it; and the local part of [INT-6 An installer that takes you from nothing to a working instance][i6] (status accepted, accepted_by Michael Hay 2026-11-01). [INT-7][i7] (accepted, same date) is not planned here; it builds on this plan.

## Objective
When this phase is complete, one small team can run Manifold on a shared host with no GitHub and no outside service: every person, agent and service is its own principal with a hashed credential; four additive roles (reader, contributor, registrar, admin) and per-component grants and denies decide what each may do; administration happens only from the host; every change names the credential behind it; revocation is immediate and durable; requests for the wrong host or origin, repeated bad credentials, unsafe binds and the old shared token are refused; TLS is a setting served by a Caddy service; the page tool can no longer write outside the scope its caller owns; and `manifold init` takes a Linux or macOS user from an empty folder to a healthy, protected server with a first administrator, a first agent credential, two registered components and a read-back handoff.

## Scope

**Traceability to the intents.** Task numbers refer to the Tasks section. Link text names the intent item; every link resolves to a heading in the intent file (constraint bullets share the `#constraints` anchor, so the bullet is named in the link text).

| Intent item | In this plan | Note |
|---|---|---|
| [INT-1 Outcome 1: own identity][i1-p] | T2, T5, T23, T27 | |
| [INT-1 Outcome 2: writes limited, four roles, close = source][i1-p] | T7, T12-T14, T16, T17 | |
| [INT-1 Outcome 3: every change names who][i1-p] | T15 | |
| [INT-1 Outcome 4: systems management separate from data][i1-p] | T7, T12, T22-T26 | |
| [INT-1 Outcome, closing paragraph (hardening, TLS switch, local mode)][i1-p] | T19-T21, T29 | GitHub sign-in is INT-7 |
| [INT-1 Constraints: Safe by default][i1-c] | T10, T21 | |
| [INT-1 Constraints: Secrets stay out of the wiki][i1-c] | T2, T6, T10, T15 | |
| [INT-1 Constraints: Client compatibility][i1-c] | T10, T35 | Claude Desktop and claude.ai: documented as a known limitation only (T35); the work is INT-18 |
| [INT-1 Constraints: No new service needed][i1-c] | T2, T28 | SQLite file, no new server |
| [INT-1 Constraints: A complete local mode][i1-c] | T21, T31-T33, T36 | |
| [INT-1 Constraints: One portable store][i1-c] | T25 | |
| [INT-1 Constraints: Admin is not data][i1-c] | T7, T12 | |
| [INT-1 Constraints: Administrative functions live on the host only][i1-c] | T7, T12, T22-T26 | agent and service kinds never admin (T5) |
| [INT-1 Constraints: The server writes only where it should][i1-c] | T8, T9, T13 | |
| [INT-1 Constraints: Revocation inside Manifold is immediate and durable][i1-c] | T2, T5, T10, T27 | The GitHub half is INT-7 |
| [INT-1 Constraints: Deleting a component takes deliberate steps][i1-c] | T17, T18, T26 | GitHub-API purge: handed to INT-14 |
| [INT-1 Constraints: Limits are settings, with defaults][i1-c] | T4, T18, T20, T26 | |
| [INT-1 Constraints: TLS can be switched on and off][i1-c] | T29, T34 | |
| [INT-1 Constraints: Standards, not inventions][i1-c] | T10, T19, T29 | Bearer and 401 per common practice; the MCP OAuth surface is INT-19 |
| [INT-1 Constraints: Offline-clean][i1-c] | T21, T29 | |
| [INT-1 Constraints: Open license][i1-c] | T29, T36 | no new Python dependencies; Caddy image licence to verify |
| [INT-1 Constraints: Reads][i1-c] | T12 | any signed-in reader reads; per-component read limits are not in the first version (owner's answer in [INT-1 Open questions][i1-oq]) |
| [INT-1 Constraints: Priority][i1-c] | whole plan | this plan is the first shared-host milestone |
| [INT-1 S1][i1-s1] | T5, T23, T27 | |
| [INT-1 S2][i1-s2] | T7, T14 | |
| [INT-1 S3][i1-s3] | T15 | |
| [INT-1 S4][i1-s4] | T10, T20 | |
| [INT-1 S5][i1-s5] | T19 | |
| [INT-1 S6][i1-s6] | T21 | reading of "works with a visible warning" is Open question 1 |
| [INT-1 S7][i1-s7] | T29, T34 | |
| [INT-1 S8][i1-s8] | T21, T31, T34 | |
| [INT-1 S9][i1-s9] | T7, T12 | |
| [INT-1 S10][i1-s10] | T13, T16, T17 | |
| [INT-1 S11][i1-s11] | T17, T18, T26 | |
| [INT-1 S12][i1-s12] | T9, T13 | |
| [INT-1 S13][i1-s13] | T21, T36 | |
| [INT-1 S14][i1-s14] | T5, T10, T27 | |
| [INT-1 S15][i1-s15] | T14, T35 | |
| [INT-1 S16][i1-s16] | T8, T9, T13 | |
| [INT-6 Outcome (local part)][i6-p] | T31-T33 | optional GitHub repository creation is deferred |
| [INT-6 Constraints: Two parts][i6-c] | T31-T33 | GitHub part deferred to the plan after INT-7 |
| [INT-6 Constraints: Local part is complete without GitHub][i6-c] | T31-T33 | |
| [INT-6 Constraints: Linux and macOS][i6-c] | T30, T31 | |
| [INT-6 Constraints: A writable data volume][i6-c] | T28, T32 | |
| [INT-6 Constraints: GitHub through its API][i6-c] | DEFERRED | INT-6 GitHub part |
| [INT-6 Constraints: Show before creating][i6-c] | T31 | applied to the local steps too; GitHub creation itself deferred |
| [INT-6 Constraints: Secrets][i6-c] | T32 | |
| [INT-6 Constraints: Safe to run twice][i6-c] | T31 | |
| [INT-6 Constraints: Clear failure messages][i6-c] | T31, T32 | |
| [INT-6 S1][i6-s1] | T33 | |
| [INT-6 S2][i6-s2] | T31 | |
| [INT-6 S3][i6-s3] | DEFERRED | create the repository on GitHub: INT-6 GitHub part, after INT-7 |
| [INT-6 S4][i6-s4] | T32, T33 | |
| [INT-6 Open question: quality repository][i6-oq] | DEFERRED | belongs to the GitHub part |
| [INT-1 Affected users and systems][i1-aff] | T28-T30, T34, T35 | container, CI, docs, and instances still on the shared token (S8) |
| [INT-1 Open questions][i1-oq] (lockout, read limits, purge with INT-14, agent self-grant) | T20, T12, T26 (handoff to INT-14), T16 | answered by the owner in the intent |
| [INT-1 Out of scope][i1-oos] and [INT-6 Out of scope][i6-oos] | not planned | none of them is planned here |

**In scope:**
- The security store, principals, roles, grants, denies, audit, authorizer, path policy, request guards, throttle, startup rules, component lifecycle, host CLI, Caddy/TLS, CI, documentation, and `manifold init` (local part), as traced above.

**Out of scope:**
- INT-6 GitHub part and all of [INT-7][i7] (sign-in with GitHub, the repo-write arm of the either-rule, the App). This plan leaves the repo-write arm as an interface that answers "not available" (T7).
- Claude Desktop and claude.ai ([INT-18][i18]); an MCP authorization server ([INT-19][i19]); per-component read limits; an admin screen in the new UI; webhooks.
- The purge path when the server has no local checkout ([INT-14][i14]): see Provides below.
- Starting the server without Docker from `manifold init`; a non-Docker start is documented only.
- The held-out behavior scenarios and the test plan (the test-planner and the quality side write those). Acceptance lines that will need the test plan: T10, T19-T21, T27, T29, T33.
- Noticed, not planned: refusing a repository already used by another component; automatic audit pruning.

**Constraints:** (from [INT-1 Constraints][i1-c] and [INT-6 Constraints][i6-c]; every item is traced above) safe by default; secrets never in the wiki, log or git history and only hashes at rest; Claude Code and VS Code keep working with a bearer header, a browser with the Basic prompt; no new service (one SQLite file outside the instance repo); complete local mode; one portable JSON export without credentials; admin is not data; administration on the host only and agent/service never admin; page tool writes only inside the caller's scope; Manifold-side revocation is immediate and durable; component deletion is deliberate (reason, no open handoffs, 14-day hold, host-only purge); limits are settings; TLS on/off via Caddy; standards; offline-clean in local mode; Apache-2.0-compatible; any signed-in caller may read; Linux and macOS; safe to run twice; clear failures.

**Needs from other repositories:** None.

**Provides to other repositories:**
- [INT-14][i14] (this repository, a later plan): the purge handoff. When the server has no local checkout, `registry purge` (T26) must remove the component's pages, raw documents and registry entry through the GitHub APIs. The owner's answer is recorded in [INT-1 Open questions][i1-oq]. T26 isolates the file removal behind one function so INT-14 can supply a second implementation.
- [INT-7][i7] (a later plan): the authorizer's repo-write interface (T7), the `authority` setting per component (T24), the principal model keyed for a GitHub identity (T5), and the credential mechanism with expiry (T3). INT-7's 12-hour default and 24-hour cap for sign-in credentials are not implemented here.

## Concerns flagged
1. **INT-7 conflict (decision needed before the INT-7 spike plan, not this plan).** [INT-7 Constraints][i7-c] says: "**One App per company, created by the company.** Not a shared Manifold-owned App. Identity settings (client ID, secret, callback URLs) and automation settings (App ID, private key, installation ID) are separate configuration so the App can be split in two later. To be confirmed by a spike." The owner's answer in [INT-7 Open questions][i7-oq] says: "I presume we are talking one app create by mediumroast and then one app by the company using manifold or both. I'd opt for both because if the user allows the mediumroast app then they will make their lives easier. However for clear control then they can create and install their own following a guide and our example app." Owner decides which stands.
2. **[INT-6 Outcome][i6-p] says "one registered component"; [INT-6 S1][i6-s1] says "two registered components".** The plan follows S1 (a handoff needs two). Owner confirms.
3. **S15 changes documented behavior.** `docs/concepts.md` says the target may close a handoff for work that needs no review, and `assets/helpers/commands/handoff-close.md` tells the target to close. [INT-1 S15][i1-s15] forbids it. T14 and T35 change the code and texts; the target's path is request-review, then the source confirms. Owner confirms.
4. **[INT-1 S6][i1-s6] reading.** With no principals on a loopback start, "works with a visible warning" is planned as: the server starts, warns, and refuses every request with a message naming `./manifold init`, unless the deliberate setting `MANIFOLD_AUTH=off` is set on loopback. Owner confirms (Open question 1).
5. **Tools I assumed read-only.** I read every tool body. `wiki_agent_catalog_tool` is not read-only: it writes `wiki/guides/agents/<component>.md` and the sidebar, so it needs contributor on the component (T13). The rest of the read tools (ping, read, inventory, freshness, onboarding, reconcile_plan, bundle_info, list_helpers, export_helper, export_component_helpers, handoff list) write nothing (no `write_text` or `git_commit` in `onboarding.py`, `freshness.py`, `helpers.py`, `bundles.py`, `ping.py`, `inventory.py`, `read.py`).
6. **Gaps beyond S16 found in the code (not run, read only).** `wiki_write_page` joins the caller's path to the wiki root with no check (`write.py`), so it could overwrite `manifold.yaml`, the sidebar, a handoff page or the log, and a `..` path may escape the root. `wiki_read` has the same join (`read.py`), so any readable file may be read, including by absolute path. `wiki_log_append` writes `Agent: <component>` from the caller's claim (`log.py`), which breaks S3. The read confinement (T9) goes beyond the text of S16; owner confirms.
7. **Ingest before register.** The documented onboarding calls `/ingest` before the component is registered. T13 allows a registrar to ingest to a slug that is not yet registered. This rule is not in the intents; owner confirms.
8. **SQLite across the Docker boundary.** The store is opened by the server in the container and by the CLI. SQLite's WAL mode is documented as unsafe across hosts or network file systems; I have not verified how Docker Desktop on macOS behaves for a bind-mounted data folder (unverified). The plan therefore runs the CLI where the database is used (inside the container for Docker deployments) and verifies on macOS in T1 before relying on it.
9. **How a tool learns the caller.** FastMCP 4.1.4 (pinned in `server/requirements.lock`) is not installed here, so the mechanism for passing the authenticated principal to tool functions, including over `/sse`, is unverified. T11 verifies it with tests before T12 depends on it.
10. **The admin principal has no credential.** Admin is host-only and "Admin is not data", so a credential would not be usable anywhere. T32 creates the first administrator as a principal record with no credential; the audit names the host user. [INT-6 S4][i6-s4] ("the administrator's host command works") is met by the host command. Owner confirms.
11. **Numbers not in the intents.** The throttle defaults (T20) and the audit-event list are my proposals; the intents give only the 5 registrations, 1 archive and 14-day hold defaults. All are settings (T4).

## Prerequisites
- [x] [INT-1][i1], [INT-6][i6] and [INT-7][i7] are accepted (read from the files, `accepted_by: Michael Hay 2026-11-01`).
- [ ] The owner confirms the project commands below and the answers to Open questions 1 to 6.
- [ ] A virtual environment exists: `.venv` is missing in this worktree and `fastmcp` is not installed in the system `python3` (3.11.3). The owner agrees the coder creates `.venv` per [server/README.md](../../server/README.md) ("Directly, without Docker"); nothing outside the repository is changed.
- [ ] Docker with Compose is available for T28 to T33 (`docker` is at `/usr/local/bin/docker` here); a macOS machine with Docker Desktop is available for T1.
- **Project commands (PROPOSED, UNVERIFIED: none was run).** `AGENTS.md` "Project commands" is blank; I did not edit it.
  - Install: `python3 -m venv .venv` then `.venv/bin/pip install -r server/requirements-dev.txt -c server/requirements.lock` (found in `server/README.md`, `.github/workflows/server.yml`).
  - Server tests: `cd server && ../.venv/bin/python -m pytest -q` (`server/README.md`; CI runs `python -m pytest -q` in `server/` on Python 3.11 and 3.12; `pytest.ini` sets `testpaths = tests`).
  - Bundle tests: `python -m pytest bundles/base/tests -q` (`CONTRIBUTING.md`; `ci.yml` uses Python 3.8, 3.10, 3.12).
  - Vendored web files: `python tools/vendor_web.py --check` (`server.yml`).
  - Build and run: `./svc_ctl.sh <dev|staging|production> init-env|start|status|logs|health|stop` (`svc_ctl.sh`, `docs/operations.md`); direct run `CONTAINER_WIKI_ROOT=<path> .venv/bin/python server/server.py` (`server/README.md`).
  - Lint and type-check: none found.
  - In acceptance lines below, `pytest` means `cd server && ../.venv/bin/python -m pytest -q`.

## File inventory

| Path | Action | Reason |
|------|--------|--------|
| `experiments/sqlite-bind-mount/` | CREATE | T1 scratch experiment (not production code) |
| `server/manifold_security/` (`store.py`, `migrations/0001_initial.sql`, `tokens.py`, `settings.py`, `principals.py`, `audit.py`, `authorizer.py`, `scopes.py`, `context.py`, `request_guard.py`, `throttle.py`, `limits.py`, `export.py`, `startup.py`) | CREATE | stdlib-only security package shared by server and CLI |
| `server/manifold_cli/` (`__main__.py`, `admin.py`, `runner.py`, `purge.py`, `init_cmd.py`, `journal.py`, `mcp_client.py`) | CREATE | host command |
| `manifold` | CREATE | repo-root launcher for `python -m manifold_cli` |
| `docker/caddy/Caddyfile.on`, `docker/caddy/Caddyfile.off` | CREATE | TLS switch |
| `docs/tls.md` | CREATE | TLS guide with client steps |
| `server/server.py` | MODIFY | middleware, guards, new tool, ingest and docs authorization |
| `server/wiki_backend/{auth,write,read,log,git,ingest,register,handoff,agent_guide,config,ping,inventory,health}.py` | MODIFY | see tasks |
| `server/tests/` (new files named in tasks; `test_auth.py`, `test_server_smoke.py`, `test_tool_surface.py`, `test_ping.py`, `test_ingest.py`, `test_handoff_tool.py`, `test_write_validation.py`, `test_deploy_files.py`, `test_health.py` edited) | CREATE / MODIFY | tests beside code |
| `docker/Dockerfile`, `docker/docker-compose.yml`, `docker/docker-compose.dev.yml`, `docker/.env.{dev,staging,production}.template` | MODIFY | data volume, no shared token, Caddy |
| `svc_ctl.sh`, `.gitignore` | MODIFY | init-env, admin passthrough, warnings; ignore the data folder |
| `.github/workflows/server.yml` | MODIFY | image job and macOS job |
| `assets/helpers/commands/handoff-close.md`, `assets/helpers/prompts/handoff-close.prompt.md`, `assets/helpers/tools/ingest_doc.py` | MODIFY | S15 wording; credential wording |
| `docs/operations.md`, `docs/quickstart.md`, `docs/concepts.md`, `README.md`, `server/README.md`, `examples/clients/*.json` | MODIFY | documentation |

## Tasks

> **Instructions for the coder:**
> Work tasks in the order listed. For each task: read the named files first,
> implement the described change, run the verify command and the task's
> acceptance check, then update the todo marker `[ ]` → `[x]` and add a
> one-line completion note directly beneath the task header: what changed, the
> command run, the result. If a task is blocked, mark it `[~]` with a note and
> surface it immediately; do not skip ahead. When all tasks are complete, fill
> in the completion summary under the Completion checklist.
> Tests use isolated temporary folders and generated credentials, never real data or real secrets (AGENTS.md "Test isolation"). Stage explicit paths only.

### Task 1 — Verify SQLite on a bind-mounted data folder
**Files:** `experiments/sqlite-bind-mount/` (scratch; never imported by production code)
**Action:** CREATE
**Change:** Write a script that creates a SQLite database in WAL mode and in rollback-journal mode in a folder mounted into a container, with one writer in the container and one on the host, and reports lost writes or lock errors. Run it on macOS (Docker Desktop) and Linux. Record the result in the task note.
**Source:** Concern 8; [INT-1 Constraints: No new service needed][i1-c].
**Acceptance:** The note states the observed result for both systems. Whatever the result, T22 runs the CLI inside the container for Docker deployments; a result that shows host and container sharing is safe only permits a host-direct option later.
**Todo:** [ ]

---

### Task 2 — Add the security store
**Files:** `server/manifold_security/store.py`, `server/manifold_security/migrations/0001_initial.sql`, `server/tests/test_security_store.py`
**Action:** CREATE
**Change:** `open_store(data_dir)` creates the folder with mode 0700 and `manifold.db` with mode 0600, refuses a `data_dir` inside `CONTAINER_WIKI_ROOT`, sets `journal_mode=WAL`, `synchronous=FULL`, `busy_timeout`, `foreign_keys=ON`, and applies numbered `.sql` migrations using `PRAGMA user_version` (refuses a database newer than the code). `0001_initial.sql` creates tables `settings`, `principals`, `credentials`, `roles`, `grants`, `denies`, `component_state`, `usage`, `audit`. Stdlib only. Add `.manifold-data/` to `.gitignore`.
**Source:** [INT-1 Constraints: No new service needed][i1-c]; [INT-1 Constraints: Secrets stay out of the wiki][i1-c].
**Acceptance:** `pytest tests/test_security_store.py` passes: modes 0700/0600, migration from empty and from version 0, refusal inside the wiki root and of a newer version, and no import beyond the standard library.
**Todo:** [ ]

---

### Task 3 — Add the credential module
**Files:** `server/manifold_security/tokens.py`, `server/tests/test_tokens.py`
**Action:** CREATE
**Change:** `issue_credential()` returns `mf_<credential_id>_<secret>` (secret from `secrets.token_urlsafe(32)`), stores only `sha256(secret)` plus `credential_id`, `principal_id`, `expires_at` (optional), `revoked_at`, `label`. `verify(presented)` looks up by id, compares with `hmac.compare_digest`, and returns one of valid, unknown, expired, revoked. The secret is returned once and never stored, logged or exported.
**Source:** [INT-1 S1][i1-s1] (never show in full after first issue); [INT-1 Constraints: Secrets stay out of the wiki][i1-c].
**Acceptance:** `pytest tests/test_tokens.py` passes, including a test that the database file bytes do not contain the secret and that `repr()` of a credential record hides it.
**Todo:** [ ]

---

### Task 4 — Add the settings registry
**Files:** `server/manifold_security/settings.py`, `server/tests/test_settings.py`
**Action:** CREATE
**Change:** One table of known settings with type, bounds and default, read from the `settings` table: `agent_registrations_per_day=5`, `agent_archives_per_day=1`, `purge_hold_days=14`, `throttle_failure_threshold=5`, `throttle_window_seconds=600`, `throttle_base_delay_seconds=1`, `throttle_max_delay_seconds=900`, `allowed_hosts`, `allowed_origins`, `trusted_proxies` (empty), `auth_mode=on`, `tls=off|on`. Unknown keys and out-of-range values are refused with a message naming the allowed range.
**Source:** [INT-1 Constraints: Limits are settings, with defaults][i1-c]; Concern 11.
**Acceptance:** `pytest tests/test_settings.py` passes: defaults as listed, override, out-of-range refusal.
**Todo:** [ ]

---

### Task 5 — Add principals, roles, grants, denies and component state
**Files:** `server/manifold_security/principals.py`, `server/tests/test_principals.py`
**Action:** CREATE
**Change:** Functions to create, list, disable and enable principals (`kind` is `human`, `agent` or `service`; unique `name`); set and unset roles (`reader`, `contributor`, `registrar`, `admin`; refuse `admin` for `agent` and `service`); add and remove grants and denies by `scope` (a component slug or the reserved `_shared`, which no valid slug can equal); a per-principal flag `may_self_grant_on_register` (default off); per-component `authority` (`grants`, `repo-write`, `either`; default `either`); `component_state` (`active`, `archived`, reason, `archived_at`, `purge_after`). Every mutation runs in `BEGIN IMMEDIATE`, commits, and only then returns.
**Source:** [INT-1 Outcome 1 and 2][i1-p]; [INT-1 Constraints: Administrative functions live on the host only][i1-c] (agents never admin); [INT-1 S1][i1-s1]; [INT-1 S14][i1-s14].
**Acceptance:** `pytest tests/test_principals.py` passes, including: admin refused for agent and service; after a mutation returns, a second connection opened from another process-like handle sees it; `_shared` is rejected as a component slug.
**Todo:** [ ]

---

### Task 6 — Add the authentication audit
**Files:** `server/manifold_security/audit.py`, `server/tests/test_audit.py`
**Action:** CREATE
**Change:** `record(event, actor, subject, detail)` writes an `audit` row synchronously for: credential issued, rotated or revoked; role, grant, deny or setting changes; refusals by the authorizer; failed sign-ins (address and a generic reason, never the presented credential); component lifecycle operations; startup notices. `actor` is the principal or `host:<os user>` for the CLI. A filter function serves `audit show`.
**Source:** [INT-1 S4][i1-s4] (refusals recorded, guess never written); [INT-1 S3][i1-s3]; [INT-1 Constraints: Secrets stay out of the wiki][i1-c].
**Acceptance:** `pytest tests/test_audit.py` passes, including a test that a presented credential string never appears in any audit row.
**Todo:** [ ]

---

### Task 7 — Add the authorizer
**Files:** `server/manifold_security/authorizer.py`, `server/tests/test_authorizer.py`
**Action:** CREATE
**Change:** `authorize(principal, capability, scope)` evaluates in this order and returns `allow(via)` or `refuse(reason_code)`: (1) principal active and credential valid; (2) a role grants the capability (contributor implies reader; registrar and admin imply nothing; admin holds no data capability); (3) a deny for (principal, scope) refuses; (4) a grant allows with `via=grant`; (5) a `RepoAuthority` interface, whose default implementation answers "not available", is asked only when the component's `authority` allows it; (6) refuse. Define the capability set: `read`, `write`, `handoff.create`, `handoff.confirm`, `handoff.reject`, `handoff.close` (all on the source component), `handoff.claim`, `handoff.request_review` (target), `component.register`, `component.update`, `component.protected_update` (human registrar only), `component.archive`, `component.restore`, `ingest`. Reads state from the database on every call; no cache.
**Source:** [INT-1 Outcome 2][i1-p]; [INT-1 S2][i1-s2]; [INT-1 S9][i1-s9]; [INT-1 S12][i1-s12]; [INT-1 S15][i1-s15]; [INT-1 Constraints: Revocation inside Manifold is immediate and durable][i1-c].
**Acceptance:** `pytest tests/test_authorizer.py` passes: a deny beats a grant; a grant for the wrong component is refused; an admin-only principal is refused every data capability; the repo arm never allows; a revocation committed by one connection is seen by the next call.
**Todo:** [ ]

---

### Task 8 — Add failing tests that show the page-tool gaps
**Files:** `server/tests/test_path_policy.py`
**Action:** CREATE
**Change:** Against the temporary `wiki_root` fixture only, add tests that call `wiki_write_page` with paths `manifold.yaml`, `wiki/_sidebar.md`, `wiki/CLAUDE.md`, `wiki/log.md`, `wiki/handoffs/acme-api-to-acme-web/x.md`, `../outside.md`, an absolute path and a symlink that leaves the root, and `wiki_read` with `../outside.md` and an absolute path, each expecting a refusal and no file change. Run them, paste the failing output in the task note, and mark them `xfail(strict=True)` until T9.
**Source:** [INT-1 S16][i1-s16]; [INT-1 Constraints: The server writes only where it should][i1-c]; Concern 6.
**Acceptance:** `pytest tests/test_path_policy.py` reports the cases as expected failures with the reasons recorded; no real data is touched.
**Todo:** [ ]

---

### Task 9 — Add the path policy and enforce it in the backends
**Files:** `server/manifold_security/scopes.py`, `server/wiki_backend/write.py`, `server/wiki_backend/read.py`, `server/tests/test_path_policy.py`
**Action:** CREATE / MODIFY
**Change:** `classify(path)` resolves a relative path against the wiki root (refusing absolute paths, `..`, NUL and symlinks that leave it) and returns `(kind, scope)`: `wiki/components/<slug>.md` and `wiki/guides/agents/<slug>.md` give component scope `<slug>`; `wiki/handoffs/**` is `handoff-only`; `wiki/log.md` is `log-only`; `wiki/_sidebar.md`, `wiki/CLAUDE.md` and `manifold.yaml` are `system`; other `wiki/**.md` pages (decisions, architecture, index, guides) give scope `_shared`; anything else is refused. `wiki_write_page` accepts only component or `_shared` kinds; `wiki_read` accepts only `wiki/**` and `raw/**`. Remove the `xfail` marks from T8.
**Source:** [INT-1 S16][i1-s16]; [INT-1 S12][i1-s12]; [INT-1 Constraints: The server writes only where it should][i1-c].
**Acceptance:** `pytest tests/test_path_policy.py tests/test_write_validation.py tests/test_handoff_tool.py -k "not smoke"` passes with T8 cases now plain passes and existing tests unchanged.
**Todo:** [ ]

---

### Task 10 — Replace the shared-token middleware with principal authentication
**Files:** `server/wiki_backend/auth.py`, `server/manifold_security/context.py`, `server/server.py`, `server/tests/test_auth.py`, `server/tests/test_auth_middleware.py`
**Action:** MODIFY / CREATE
**Change:** Replace `TokenAuthMiddleware`, `configured_token`, `check_startup` and `is_authorized` with `PrincipalAuthMiddleware`: read `Authorization: Bearer` or `Basic` (password), call `tokens.verify` against the store on every request, set a `current_principal` context variable, and answer failures with 401 and `WWW-Authenticate` challenges. Errors are generic ("authentication required") except that a revoked or expired credential gets "your access was removed or has expired" (only a holder of the full secret sees this). `/health` stays open and shows detail only to an authenticated reader. The old `MANIFOLD_TOKEN` and `MANIFOLD_TOKEN_FILE` are no longer read (T21 prints the notice). Rewrite `test_auth.py` for the new behavior.
**Source:** [INT-1 S1][i1-s1]; [INT-1 S4][i1-s4] (no revealing errors); [INT-1 S14][i1-s14]; [INT-1 Constraints: Client compatibility][i1-c]; [INT-1 Constraints: Standards, not inventions][i1-c].
**Acceptance:** `pytest tests/test_auth.py tests/test_auth_middleware.py` passes: Bearer and Basic both work; a wrong credential and a missing one return the same body; a revoked credential is refused on the very next request without a restart.
**Rollback:** This removes the shared token (a breaking change for running instances). `git revert` the commit restores the old middleware; instances keep their `MANIFOLD_TOKEN` line in `docker/.env.<env>` because nothing deletes it.
**Todo:** [ ]

---

### Task 11 — Verify that tools see the caller over /mcp and /sse
**Files:** `server/tests/test_principal_propagation.py`, `server/manifold_security/context.py`, `server/server.py`
**Action:** CREATE / MODIFY
**Change:** Using the real-server pattern in `test_server_smoke.py`, add a temporary tool that returns `current_principal`; call it over `/mcp` with two credentials in turn and over `/sse` with two sessions. If FastMCP runs SSE tool calls outside the request context, bind each session id to the principal that opened it and refuse a POST whose credential differs from the session's. Remove the temporary tool; add `principal` (name, kind, roles) to the result of `wiki_ping_tool`.
**Source:** Concern 9; [INT-1 S3][i1-s3]; [INT-1 S2][i1-s2]. Unverified until run: confirm with the FastMCP 4.1.4 source after install.
**Acceptance:** `pytest tests/test_principal_propagation.py tests/test_ping.py` passes: each call is attributed to its own credential on both transports, and a mismatched SSE POST is refused.
**Todo:** [ ]

---

### Task 12 — Add the tool policy table and guard the read tools
**Files:** `server/manifold_security/authorizer.py`, `server/server.py`, `server/tests/test_tool_policy.py`, `server/tests/test_tool_surface.py`
**Action:** MODIFY / CREATE
**Change:** Add `TOOL_POLICY`, mapping every tool name (and `wiki_handoff_tool` action) to a capability, and a `@guarded` wrapper applied to every `@app.tool()`; a tool with no entry is refused. Read tools (`wiki_read_tool`, `wiki_inventory_tool`, `wiki_freshness_tool`, `wiki_onboarding_tool`, `wiki_reconcile_plan_tool`, `wiki_bundle_info_tool`, `wiki_list_helpers_tool`, `wiki_export_helper_tool`, `wiki_export_component_helpers_tool`, handoff `list`) require `read`; `wiki_ping_tool` requires only an authenticated principal. Guard `/docs/**` and `/docs/raw/**` as `read`. Table of the whole policy:

| Tool or route | Requirement |
|---|---|
| read tools above, `/docs` | reader |
| `wiki_write_page_tool`, `wiki_log_append_tool`, `wiki_agent_catalog_tool`, `POST /ingest` | contributor in the page's scope (T13) |
| `wiki_handoff_tool` create, confirm, reject, close | contributor on the source component (T14) |
| `wiki_handoff_tool` claim, request-review | contributor on the target component (T14) |
| `wiki_register_component_tool`, `wiki_component_manage_tool` | registrar (T16, T17) |
| anything administrative | not available over MCP or HTTP |

**Source:** [INT-1 S9][i1-s9]; [INT-1 Constraints: Admin is not data][i1-c]; [INT-1 Constraints: Administrative functions live on the host only][i1-c]; [INT-1 Constraints: Reads][i1-c].
**Acceptance:** `pytest tests/test_tool_policy.py tests/test_tool_surface.py` passes: every registered tool has a policy; an admin-only principal is refused every read and write tool; no tool or route name creates credentials, roles or grants.
**Todo:** [ ]

---

### Task 13 — Guard the writing tools and ingest
**Files:** `server/server.py`, `server/wiki_backend/write.py`, `server/wiki_backend/agent_guide.py`, `server/wiki_backend/ingest.py`, `server/tests/test_write_validation.py`, `server/tests/test_ingest.py`
**Action:** MODIFY
**Change:** `wiki_write_page_tool`: authorize `write` on the scope from `scopes.classify` (component slug or `_shared`); refuse a write that changes the `component` or `owner` frontmatter of a component page, or its `**Repository:**` line. `wiki_log_append_tool`: authorize `write` on the given component, or on `_shared` when none. `wiki_agent_catalog_tool`: authorize `write` on the component. `POST /ingest`: authorize `ingest` on the slug (`raw/shared` maps to `_shared`); a registrar may also ingest to a slug that is not yet registered. An archived component refuses all of these (T17).
**Source:** [INT-1 S10][i1-s10]; [INT-1 S12][i1-s12]; [INT-1 S16][i1-s16]; Concerns 5 and 7.
**Acceptance:** `pytest tests/test_write_validation.py tests/test_ingest.py` passes: a contributor writes its own component page and not another's; only a `_shared` grant writes a decision page; a contributor's attempt to edit `owner` or `repo` in the component page is refused; an unregistered slug is refused for a non-registrar.
**Todo:** [ ]

---

### Task 14 — Enforce the handoff rules
**Files:** `server/wiki_backend/handoff.py`, `server/server.py`, `server/tests/test_handoff_authz.py`, `server/tests/test_handoff_tool.py`
**Action:** MODIFY / CREATE
**Change:** Read `source_component` and `target_component` from the handoff page and authorize: `create` (source from the argument), `confirm`, `reject`, `close` on the source; `claim`, `request-review` on the target; `list` as read. Replace the `wiki_handoff_tool` docstring text "target closes after implementing" with the source-only rule.
**Source:** [INT-1 S2][i1-s2]; [INT-1 S15][i1-s15]; [INT-1 Outcome 2][i1-p]; Concern 3.
**Acceptance:** `pytest tests/test_handoff_authz.py tests/test_handoff_tool.py tests/test_handoff_lifecycle.py` passes: the target's close, and any other principal's confirm, reject or close, return a clear reason and write nothing; the source's close succeeds.
**Todo:** [ ]

---

### Task 15 — Name the credential's principal in commits and the log
**Files:** `server/wiki_backend/git.py`, `server/wiki_backend/log.py`, `server/wiki_backend/{write,ingest,register,handoff,agent_guide}.py`, `server/tests/test_git_root.py`, `server/tests/test_audit.py`
**Action:** MODIFY
**Change:** Add a `principal` argument to `git_commit` that sets `--author "<name> <<principal_id>@principals.manifold.invalid>"` and adds a trailer `Manifold-Principal: <id> (<kind>)`; the committer stays `MANIFOLD_GIT_NAME`. Pass the current principal from every caller (including sidebar and index commits). Change `wiki_log_append` to write `Agent: <principal name>` and keep the component as the subject. Nothing the caller supplies becomes an author.
**Source:** [INT-1 S3][i1-s3]; [INT-1 Outcome 3][i1-p].
**Acceptance:** `pytest tests/test_git_root.py tests/test_audit.py` passes: `git log --format=%an%n%b` shows the credential's principal; a request body that claims another name still shows the real principal; the log line names the principal.
**Todo:** [ ]

---

### Task 16 — Gate component registration and protect the mapping
**Files:** `server/server.py`, `server/wiki_backend/register.py`, `server/wiki_backend/onboarding.py`, `server/tests/test_registrar.py`
**Action:** MODIFY / CREATE
**Change:** `wiki_register_component_tool` requires `component.register`. A reconcile call, or a call whose `repo` or `owner` differs from the registry, requires `component.protected_update` (a human registrar). A new registration gives the registrar no grant, unless an administrator set `may_self_grant_on_register` on that principal, in which case it adds a grant for that slug and audits it. Registration and reconcile write their own log entry attributed to the principal; remove step 4 and the reconcile `next_step` hint that tell the agent to log it. Count registrations for T18.
**Source:** [INT-1 S10][i1-s10]; [INT-1 Constraints: Deleting a component takes deliberate steps][i1-c] (agents cannot change repository or owner); [INT-1 Open questions][i1-oq] (self-grant setting: yes, default off).
**Acceptance:** `pytest tests/test_registrar.py tests/test_onboarding.py` passes: an agent registrar registers; its page write on the new component is refused until a grant exists; with the flag on, one grant is added and audited; an agent's change of `repo` or `owner` is refused; a human registrar's succeeds.
**Todo:** [ ]

---

### Task 17 — Add the component update, archive and restore tool
**Files:** `server/server.py`, `server/wiki_backend/register.py`, `server/wiki_backend/config.py`, `server/wiki_backend/inventory.py`, `server/wiki_backend/ping.py`, `server/tests/test_component_manage.py`, `server/tests/test_tool_surface.py`
**Action:** CREATE / MODIFY
**Change:** Add `wiki_component_manage_tool(action, name, reason="", description="", repo="", owner="")` with `action` of `update`, `archive` or `restore`, following the multi-action pattern of `wiki_handoff_tool`. `archive` refuses an empty reason and any open handoff (source or target, status not completed), naming the handoffs; it records `component_state` with `purge_after = now + purge_hold_days`, writes a log entry, and audits. An archived component refuses writes, handoff creation and ingest (T13, T14). `restore` clears the state. `update` changes the description for any registrar and `repo` or `owner` for a human registrar only. `wiki_inventory` marks each component `status`. Add the tool to `ping` and the tool count (15 becomes 16).
**Source:** [INT-1 S11][i1-s11]; [INT-1 S10][i1-s10]; [INT-1 Outcome 4][i1-p]; [INT-1 Constraints: Deleting a component takes deliberate steps][i1-c].
**Acceptance:** `pytest tests/test_component_manage.py tests/test_tool_surface.py tests/test_ping.py` passes: archive without a reason or with an open handoff is refused with the handoffs named; an archived component rejects a page write and a new handoff; restore re-enables them; no MCP action purges.
**Todo:** [ ]

---

### Task 18 — Enforce the agent registrar limits
**Files:** `server/manifold_security/limits.py`, `server/wiki_backend/register.py`, `server/tests/test_registrar.py`
**Action:** CREATE / MODIFY
**Change:** Count registrations and archives per principal per UTC day in the `usage` table, in the same transaction as the operation; refuse an `agent` or `service` principal beyond `agent_registrations_per_day` (5) or `agent_archives_per_day` (1), saying which limit and when it resets. Humans are not limited. Audit each refusal.
**Source:** [INT-1 S11][i1-s11] (agents never exceed daily limits); [INT-1 Constraints: Limits are settings, with defaults][i1-c].
**Acceptance:** `pytest tests/test_registrar.py -k limit` passes: the sixth registration and the second archive in a day are refused for an agent, allowed after the setting is raised, and unlimited for a human.
**Todo:** [ ]

---

### Task 19 — Add the Host and Origin guard
**Files:** `server/manifold_security/request_guard.py`, `server/server.py`, `server/tests/test_request_guard.py`
**Action:** CREATE / MODIFY
**Change:** Add middleware, placed before authentication, that refuses (421 or 403, no detail) any request whose `Host` is not in `allowed_hosts` (default `127.0.0.1`, `localhost`, `[::1]` with the served port, plus the configured public host) and any request using POST, PUT, PATCH or DELETE that carries an `Origin` not in `allowed_origins` (default: the served origins). Requests with no `Origin` (MCP clients, scripts) pass this check. `/health` is exempt from the Host check only for the container health probe address.
**Source:** [INT-1 S5][i1-s5]; [INT-1 Constraints: Standards, not inventions][i1-c].
**Acceptance:** `pytest tests/test_request_guard.py` passes: wrong Host refused; foreign Origin on POST refused; documented address and origin accepted; no-Origin POST accepted.
**Todo:** [ ]

---

### Task 20 — Add the per-address throttle
**Files:** `server/manifold_security/throttle.py`, `server/server.py`, `server/tests/test_throttle.py`
**Action:** CREATE / MODIFY
**Change:** Count failed authentications per client address in memory. After `throttle_failure_threshold` failures within `throttle_window_seconds`, answer 429 with `Retry-After`, doubling the delay from `throttle_base_delay_seconds` up to `throttle_max_delay_seconds`, and do not check the credential while the delay runs. Never lock a credential. The client address is the socket peer, or the last `X-Forwarded-For` entry only when the peer is in `trusted_proxies` (the Caddy service, T29). Audit each refusal with the address.
**Source:** [INT-1 S4][i1-s4]; [INT-1 Open questions][i1-oq] (lockout answer: per-address growing delay, never lock a credential, trust the forwarded address only from the Caddy service).
**Acceptance:** `pytest tests/test_throttle.py` passes: delay grows and resets after quiet; a correct credential from another address works during it; a spoofed `X-Forwarded-For` from an untrusted peer is ignored; the credential is never in the audit.
**Todo:** [ ]

---

### Task 21 — Add the startup rules and the legacy-token notice
**Files:** `server/manifold_security/startup.py`, `server/server.py`, `server/tests/test_startup.py`, `server/tests/test_offline_clean.py`
**Action:** CREATE / MODIFY
**Change:** At startup (including under `uvicorn server:asgi_app`): open the store, run migrations, and apply these rules. A non-loopback `MANIFOLD_HOST` with no principals refuses to start with a message naming `./manifold init`. `auth_mode=off` is allowed only on loopback and logs a loud warning; request-time middleware also refuses non-loopback peers in that mode. On loopback with no principals and `auth_mode=on`, start with a visible warning and refuse each request with the same message (Concern 4). If `MANIFOLD_TOKEN` or `MANIFOLD_TOKEN_FILE` is set, log that it is no longer accepted and name the host command that creates the first administrator. Add `test_offline_clean.py`, which fails if any server module imports an HTTP client library.
**Source:** [INT-1 S6][i1-s6]; [INT-1 S8][i1-s8]; [INT-1 S13][i1-s13]; [INT-1 Constraints: Safe by default][i1-c]; [INT-1 Constraints: Offline-clean][i1-c]; [INT-1 Constraints: A complete local mode][i1-c].
**Acceptance:** `pytest tests/test_startup.py tests/test_offline_clean.py` passes: each rule has a case; the old token is not accepted and the message names the command.
**Todo:** [ ]

---

### Task 22 — Add the host command skeleton and runner
**Files:** `manifold`, `server/manifold_cli/__main__.py`, `server/manifold_cli/runner.py`, `server/tests/test_cli_runner.py`
**Action:** CREATE
**Change:** `manifold` is a Python launcher (checks Python 3.11 or newer and prints the fix if not) that runs `python -m manifold_cli` from `server/`; stdlib only. Subcommands are `init` and `admin <group> <verb>`. The runner picks where `admin` runs: with `--env <name>` and a Docker environment file, through `./svc_ctl.sh <name> admin ...` (T29), which runs the CLI inside the container so that only one kernel opens the database; with `--data-dir <path>`, directly. Output never contains a stored secret; failures exit non-zero with a message that says what to fix. The `svc_ctl.sh ... admin` route is added in T29 and exercised against a real container in T30; T23 to T26 test the commands directly with `--data-dir`.
**Source:** [INT-1 Constraints: Administrative functions live on the host only][i1-c]; [INT-1 Outcome 1][i1-p]; Concern 8.
**Acceptance:** `pytest tests/test_cli_runner.py` passes with a fake `docker`: runner choice, exit codes, and a check that `import manifold_cli` needs no third-party package.
**Todo:** [ ]

---

### Task 23 — Add the principal and credential commands
**Files:** `server/manifold_cli/admin.py`, `server/tests/test_cli_principals.py`
**Action:** CREATE
**Change:** `admin principal create|list|show|disable|enable`; `admin credential issue|rotate|revoke` (`--expires`, shows the secret once on a TTY or to a `--secret-file` created 0600, never to a log); `admin role set|unset`. Every action records `host:<os user>` in the audit. Revoke and disable print which lever was used.
**Source:** [INT-1 S1][i1-s1]; [INT-1 S14][i1-s14]; [INT-1 Outcome 1][i1-p].
**Acceptance:** `pytest tests/test_cli_principals.py` passes: issue shows the secret once and `show` never does; revoke affects only that credential; `role set admin` on an agent is refused.
**Todo:** [ ]

---

### Task 24 — Add the grant, deny, authority and settings commands
**Files:** `server/manifold_cli/admin.py`, `server/tests/test_cli_grants.py`
**Action:** MODIFY / CREATE
**Change:** `admin grant add|remove`, `admin deny add|remove` (scope is a slug or `_shared`), `admin authority set <component> grants|repo-write|either`, `admin settings list|get|set`, and `admin registrar-flag set <principal> --self-grant on|off`. `grant remove` says whether other routes (a role, another grant) still give access, and advises `deny add` or `disable` to end it.
**Source:** [INT-1 S2][i1-s2]; [INT-1 S14][i1-s14] (never leave access in place without saying so); [INT-1 S12][i1-s12]; [INT-1 Constraints: Limits are settings, with defaults][i1-c].
**Acceptance:** `pytest tests/test_cli_grants.py` passes: out-of-range settings are refused with the range; grant removal output names remaining routes.
**Todo:** [ ]

---

### Task 25 — Add the audit, export and import commands
**Files:** `server/manifold_security/export.py`, `server/manifold_cli/admin.py`, `server/tests/test_cli_export.py`
**Action:** CREATE / MODIFY
**Change:** `admin audit show [--since --principal --event]`; `admin export [--with-hashes] FILE` writes a versioned JSON of principals, roles, grants, denies, component authority and settings (no credentials; hashes only with the flag); `admin import FILE [--dry-run] [--merge|--replace]` validates the version and refuses to overwrite without a flag.
**Source:** [INT-1 Constraints: One portable store][i1-c]; [INT-1 S9][i1-s9] (audit read by admin).
**Acceptance:** `pytest tests/test_cli_export.py` passes: export then import into an empty store reproduces roles and grants; the default export contains no hash and no secret.
**Todo:** [ ]

---

### Task 26 — Add the registry purge command
**Files:** `server/manifold_cli/purge.py`, `server/wiki_backend/config.py`, `server/wiki_backend/register.py`, `server/tests/test_cli_purge.py`
**Action:** CREATE / MODIFY
**Change:** `registry purge <slug> --confirm-slug <slug>`: refuses unless the component is archived and `purge_after` has passed (`purge_hold_days`, default 14), re-checks for open handoffs, prints what it will remove, and requires the slug typed exactly. It removes the component page, `raw/<slug>/`, the agent guide, the sidebar entry and the registry entry (add `remove_from_config` and a sidebar remover beside their adders), then makes one git commit authored `host:<os user>`. Completed handoff pages are kept as history. Put file removal behind one function (`remove_component_files`) so INT-14 can add a GitHub implementation. Not available over MCP.
**Source:** [INT-1 S11][i1-s11]; [INT-1 Constraints: Deleting a component takes deliberate steps][i1-c]; [INT-1 Open questions][i1-oq] (INT-14 handoff).
**Acceptance:** `pytest tests/test_cli_purge.py` passes: purge before the hold, without archive, with an open handoff, or with a mistyped slug is refused with no change; a valid purge leaves a clean `git status` and one commit.
**Rollback:** the purge is one git commit; `git revert <sha>` in the instance restores the files; the database row is re-created by restoring the component.
**Todo:** [ ]

---

### Task 27 — Add the cross-process revocation test
**Files:** `server/tests/test_revocation_smoke.py`
**Action:** CREATE
**Change:** Following `test_server_smoke.py`, start the real server on a temporary instance and data folder, issue two credentials through the CLI in a separate process, confirm both work, revoke one, confirm its next request is refused and the other still works, restart the server, and confirm the revoked one is still refused. Repeat for a deny and a disabled principal.
**Source:** [INT-1 S14][i1-s14]; [INT-1 S1][i1-s1]; [INT-1 Constraints: Revocation inside Manifold is immediate and durable][i1-c].
**Acceptance:** `pytest tests/test_revocation_smoke.py` passes; the test needs no restart between revoke and the refused request.
**Todo:** [ ]

---

### Task 28 — Add the data volume and remove the shared token from the container files
**Files:** `docker/Dockerfile`, `docker/docker-compose.yml`, `docker/docker-compose.dev.yml`, `docker/.env.dev.template`, `docker/.env.staging.template`, `docker/.env.production.template`, `server/tests/test_deploy_files.py`
**Action:** MODIFY
**Change:** Remove `MANIFOLD_TOKEN` from compose and the templates. Add `DATA_DIR` (absolute host path) mounted at `/data`, set `MANIFOLD_DATA_DIR=/data` in the image, keep `read_only: true`, and keep the container user `HOST_UID:HOST_GID` so the data folder is owned by the person. Put the Manifold service on an internal network and stop publishing its port directly (T29 publishes through Caddy).
**Source:** [INT-1 Affected users and systems][i1-aff] (writable data volume under a read-only root); [INT-1 Constraints: No new service needed][i1-c]; [INT-6 Constraints: A writable data volume][i6-c]; [INT-1 S8][i1-s8].
**Acceptance:** `pytest tests/test_deploy_files.py` passes with new cases: no `MANIFOLD_TOKEN` in compose or templates, `read_only: true` kept, a `/data` mount present, the data mount not inside the instance mount.
**Rollback:** `git revert` the commit restores the old compose files; the data folder is only added, never deleted, so it can be left in place.
**Todo:** [ ]

---

### Task 29 — Add Caddy, the TLS switch and the service-script commands
**Files:** `docker/docker-compose.yml`, `docker/caddy/Caddyfile.on`, `docker/caddy/Caddyfile.off`, `svc_ctl.sh`, `server/tests/test_deploy_files.py`
**Action:** CREATE / MODIFY
**Change:** Add a `caddy` service (image pinned by tag and digest, verified current in the task note; read-only root, writable volumes for its data and config) that publishes `${BIND_ADDRESS}:${PORT}` and proxies to `manifold`. `MANIFOLD_TLS=on` mounts `Caddyfile.on` (`tls internal` or provided certificate files; never a public ACME path, to keep the server offline-clean); `off` mounts `Caddyfile.off` (plain). Pass the Caddy network address as `trusted_proxies` and `MANIFOLD_TLS` to the server. In `svc_ctl.sh`: `init-env` stops creating a token and creates `DATA_DIR` (0700); `start` refuses a non-loopback `BIND_ADDRESS` with `MANIFOLD_TLS=off` unless `MANIFOLD_ALLOW_PLAIN_ON_NETWORK=yes`, and then prints a visible warning; warn if the env file still has `MANIFOLD_TOKEN`; add `admin <args>` which runs `python -m manifold_cli admin <args>` in the container (`compose exec` when running, `compose run --rm` otherwise). Verified this session in Caddy docs: `tls internal`, `tls <cert> <key>`, `reverse_proxy` with `trusted_proxies`, and that SSE responses are flushed by default. Unverified: the exact Caddyfile for a plain-HTTP site and for `auto_https`; confirm with the Caddy documentation and the Caddy licence (believed Apache-2.0) in the task note.
**Source:** [INT-1 S7][i1-s7]; [INT-1 Constraints: TLS can be switched on and off][i1-c]; [INT-1 Constraints: Offline-clean][i1-c]; [INT-1 Constraints: Open license][i1-c]; [INT-1 S4][i1-s4] (trusted forwarding).
**Acceptance:** `pytest tests/test_deploy_files.py` passes (both Caddyfiles exist, neither names a public ACME issuer, the server port is not published directly); `./svc_ctl.sh dev config` renders for `MANIFOLD_TLS=on` and `off`; the CI job in T30 passes.
**Todo:** [ ]

---

### Task 30 — Rewrite the CI image job and add a macOS job
**Files:** `.github/workflows/server.yml`
**Action:** MODIFY
**Change:** In the `image` job: create the data folder, issue a credential with `./svc_ctl.sh production admin ...` after the container starts, and assert 401 without a credential, 200 with it, that `MANIFOLD_TOKEN` is refused, the non-root user, `ReadonlyRootfs=true` and the loopback-only published port (kept), and TLS on and off (HTTPS checked against Caddy's exported root certificate, not `-k`). Add a job on `macos-latest` that runs the server tests without Docker (Python 3.12).
**Source:** [INT-1 Affected users and systems][i1-aff] (the CI image check changes); [INT-6 Constraints: Linux and macOS][i6-c]; [INT-1 S8][i1-s8].
**Acceptance:** The workflow passes on a pull request in GitHub Actions (observed; I cannot run it locally), including the macOS job.
**Todo:** [ ]

---

### Task 31 — Add `manifold init`: preflight, state detection and the plan
**Files:** `server/manifold_cli/init_cmd.py`, `server/manifold_cli/journal.py`, `server/tests/test_init.py`
**Action:** CREATE
**Change:** `manifold init [--env NAME] [--instance PATH] [--data-dir PATH] [--yes]`. Preflight: Linux or macOS (`platform.system()`; Windows refused with a message), Python 3.11 or newer, `git`, `docker` and `docker compose`, port free. Detect an existing instance, data folder, environment file or store; if any exists, say what exists and offer repair (create only what is missing, never change credentials, never overwrite content) or stop. Show the full plan (instance folder, data folder, environment file, TLS setting, principals) and wait for a yes; nothing is created before it. Each step reports a clear message that says what to fix.
**Source:** [INT-6 S2][i6-s2]; [INT-6 Constraints: Safe to run twice][i6-c]; [INT-6 Constraints: Linux and macOS][i6-c]; [INT-6 Constraints: Show before creating][i6-c]; [INT-6 Constraints: Clear failure messages][i6-c]; [INT-1 S8][i1-s8] (an existing shared-token instance is adopted through repair).
**Acceptance:** `pytest tests/test_init.py -k "preflight or detect or plan"` passes with fake `git` and `docker` runners: a second run changes nothing without a yes; Windows is refused.
**Todo:** [ ]

---

### Task 32 — Add `manifold init`: create with undo, and the first credentials
**Files:** `server/manifold_cli/init_cmd.py`, `server/manifold_cli/journal.py`, `server/tests/test_init.py`
**Action:** MODIFY
**Change:** After the yes, record every created path in the journal and undo them in reverse order if any step fails. Steps: copy `examples/starter` to the instance folder and make the first commit with `-c user.name -c user.email` flags (no global git config); create the data folder (0700) and the store; write `docker/.env.<env>` (0600, no secret); create the first administrator as a principal with the `admin` role and no credential (Concern 10); create the first agent principal with `reader`, `contributor` and `registrar` roles and grants for the two sample component slugs, issue its credential, show it once and write it only to a 0600 file the person names. No default or shared credential remains.
**Source:** [INT-6 S4][i6-s4]; [INT-6 S1][i6-s1] (no half-created instance); [INT-6 Constraints: Secrets][i6-c]; [INT-1 S1][i1-s1].
**Acceptance:** `pytest tests/test_init.py -k "create or undo or credential"` passes: forcing a failure at each step leaves no created path; the credential never appears in captured output after the first display, in logs or in any file but the one named.
**Todo:** [ ]

---

### Task 33 — Add `manifold init`: start, check and the first handoff
**Files:** `server/manifold_cli/init_cmd.py`, `server/manifold_cli/mcp_client.py`, `server/tests/test_init.py`
**Action:** MODIFY / CREATE
**Change:** Start the service through `./svc_ctl.sh <env> start`, wait for `/health` (bounded wait, message on timeout), check that a request without a credential is refused and the host `admin principal list` works, then use a small stdlib MCP client (`initialize`, `tools/call` over `/mcp`) with the agent credential to register the two sample components, create a handoff between them and read it back. On any failure run the journal undo and `svc_ctl stop`. Print the client steps for Claude Code and VS Code.
**Source:** [INT-6 S1][i6-s1]; [INT-6 S4][i6-s4]; [INT-6 Constraints: Local part is complete without GitHub][i6-c]; Concern 2.
**Acceptance:** `pytest tests/test_init.py` passes against the real server pattern of `test_server_smoke.py` (no Docker); on a Docker machine, `./manifold init --yes` in a temporary folder ends with a healthy server, two components and a handoff read back, and `./manifold init` again changes nothing (observed by the coder, to be covered by the test plan).
**Todo:** [ ]

---

### Task 34 — Write the operations and TLS guides and the upgrade steps
**Files:** `docs/operations.md`, `docs/tls.md`
**Action:** MODIFY / CREATE
**Change:** Replace "The token" in `docs/operations.md` with: principals and credentials, the four roles and the matrix in T12, grants and denies (why a deny, why removing a grant may not end access), the purge hold and procedure, settings and their defaults, export and import, backup of the data folder, and "Upgrade from the shared token" as ordered steps (stop, pull, `./manifold init` repair or `admin principal create`, issue credentials, start, check the notice). Create `docs/tls.md`: the TLS setting, trusting Caddy's local root, and client steps for Claude Code, VS Code and a browser (mark each client's certificate-trust step "unverified" until confirmed by running it, and never advise turning off certificate checks).
**Source:** [INT-1 S7][i1-s7]; [INT-1 S8][i1-s8]; [INT-1 S11][i1-s11]; [INT-1 Constraints: TLS can be switched on and off][i1-c].
**Acceptance:** A person following the TLS guide on a clean machine connects Claude Code, VS Code and a browser over HTTPS (observed by the coder; to be covered by the test plan); every relative link in the two files resolves.
**Todo:** [ ]

---

### Task 35 — Rewrite the quickstart, READMEs, concepts, client examples and helper texts
**Files:** `docs/quickstart.md`, `README.md`, `server/README.md`, `docs/concepts.md`, `examples/clients/claude-code-mcp.json`, `examples/clients/vscode-mcp.json`, `assets/helpers/commands/handoff-close.md`, `assets/helpers/prompts/handoff-close.prompt.md`, `assets/helpers/tools/ingest_doc.py`
**Action:** MODIFY
**Change:** Make `manifold init` the quickstart path and move the manual steps to an "advanced" section. In `server/README.md` remove the shared-token banner, the `MANIFOLD_TOKEN*` rows and the matching "Known limits"; add the new variables (`MANIFOLD_DATA_DIR`, `MANIFOLD_AUTH`, `MANIFOLD_TLS`, allowed hosts, origins, trusted proxies), the tool count (16) and the new tool. In `docs/concepts.md` replace "close lets the target mark a handoff completed" with request-review then confirm, and describe roles. Keep `MANIFOLD_TOKEN` only as the name of the client-side variable holding a person's own credential, and say so. Add the Claude Desktop and claude.ai known limitation with a pointer to [INT-18][i18]. Replace the target-close wording in the two `handoff-close` helper files.
**Source:** [INT-1 S15][i1-s15]; [INT-1 S8][i1-s8]; [INT-1 Constraints: Client compatibility][i1-c]; [INT-6 S1][i6-s1].
**Acceptance:** `pytest tests/test_helpers.py tests/test_example_starter.py tests/test_example_acme.py tests/test_deploy_files.py` passes; `grep -rn "target may also: close" docs assets examples` returns nothing; every relative link in the changed files resolves.
**Todo:** [ ]

---

### Task 36 — Run everything
**Files:** none
**Action:** none
**Change:** Run the full checks and the end-to-end walk-through on Linux and macOS.
**Source:** [INT-1 S13][i1-s13]; [INT-1 Constraints: Open license][i1-c]; [INT-6 S1][i1-s1].
**Acceptance:** The commands in the Completion checklist pass; `pip list` shows no new Python dependency beyond `server/requirements.lock`; a run with no GitHub settings makes no outside request (`test_offline_clean.py`).
**Todo:** [ ]

---

## Completion checklist
- [ ] All tasks marked [x] by the coder
- [ ] Verify command: none found (no lint or type-check); the owner confirms this, and `pytest` below is the gate
- [ ] `cd server && ../.venv/bin/python -m pytest -q` passes clean (no regressions)
- [ ] `python -m pytest bundles/base/tests -q` and `python tools/vendor_web.py --check` pass
- [ ] The CI workflow `server` passes (tests on 3.11 and 3.12, image job, macOS job)
- [ ] The traceability table above still matches the finished work; any omission is recorded below
- [ ] No [~] blocked items outstanding
- [ ] Summary note added by the coder below this line

<!--
  coder: add your completion summary here:
  - Files changed
  - Deviations from the plan, and why ("None." if none)
  - Verification evidence: command and result for each check; anything not run, and why
  - Deferred items and follow-ups
-->

## Open questions
Ranked by how much they change the plan; each names who answers.
1. For [INT-1 S6][i1-s6]: with no principals on a loopback start, is "starts with a warning and refuses every request until `./manifold init`" right, or should it serve openly? (the product owner)
2. The CLI runs inside the container for Docker deployments, because SQLite's WAL is documented as unsafe across hosts or network file systems (unverified for Docker Desktop on macOS). Is that acceptable, subject to T1? (the product owner)
3. The first administrator has no credential (Concern 10). Is that right? Should `init` also create a personal reader or contributor principal for the person? (the product owner)
4. Throttle defaults (5 failures in 10 minutes, delay from 1 second doubling to 15 minutes) and the audit-event list are proposals. Accept or change. (the product owner)
5. A registrar may ingest to an unregistered slug (Concern 7). Accept? (the product owner)
6. Confining `wiki_read` as well as the page-write path (Concern 6) goes beyond S16's text. Accept? (the product owner)
7. The target can no longer close a handoff (Concern 3); is request-review plus the source's confirm the intended path for no-review work, and may the shipped helper texts change? (the product owner)
8. [INT-6 Outcome vs S1][i6-p]: one or two components? The plan uses two (Concern 2). Names of the two sample components (default `example-api` and `example-web`)? (the product owner)
9. Do host-issued credentials for `human` principals expire by default? The plan sets none (mechanism only); INT-7's 12-hour default and 24-hour cap apply to sign-in credentials in that plan. (the product owner)
10. TLS default: `off` when `BIND_ADDRESS` is loopback and `on` otherwise, set by `init-env`? (the product owner)
11. Purge keeps completed handoff pages as history; remove them too? (the product owner)
12. The INT-7 conflict in Concern 1, needed before the INT-7 spike plan. (the product owner)
13. The INT-14 purge handoff: who raises it in INT-14 when that plan is written? (the product owner, with INT-14)
14. Pin the Caddy image tag and digest and confirm its licence (T29). (the coder, reported to the product owner)

[i1]: ../../intent/INT-1-security-baseline.md
[i1-p]: ../../intent/INT-1-security-baseline.md#proposed-outcome
[i1-aff]: ../../intent/INT-1-security-baseline.md#affected-users-and-systems
[i1-c]: ../../intent/INT-1-security-baseline.md#constraints
[i1-oq]: ../../intent/INT-1-security-baseline.md#open-questions
[i1-oos]: ../../intent/INT-1-security-baseline.md#out-of-scope
[i6-oos]: ../../intent/INT-6-installer.md#out-of-scope
[i1-s1]: ../../intent/INT-1-security-baseline.md#s1--each-person-has-their-own-credential
[i1-s2]: ../../intent/INT-1-security-baseline.md#s2--an-agent-can-only-act-for-its-own-component
[i1-s3]: ../../intent/INT-1-security-baseline.md#s3--every-change-names-who-made-it
[i1-s4]: ../../intent/INT-1-security-baseline.md#s4--a-guessing-attack-is-slowed-down-and-noticed
[i1-s5]: ../../intent/INT-1-security-baseline.md#s5--a-request-for-the-wrong-host-or-from-the-wrong-web-page-is-refused
[i1-s6]: ../../intent/INT-1-security-baseline.md#s6--the-server-will-not-open-itself-to-the-network-unprotected
[i1-s7]: ../../intent/INT-1-security-baseline.md#s7--tls-is-a-setting-not-a-research-project
[i1-s8]: ../../intent/INT-1-security-baseline.md#s8--retiring-the-shared-token
[i1-s9]: ../../intent/INT-1-security-baseline.md#s9--the-admin-manages-the-system-but-cannot-read-the-wiki
[i1-s10]: ../../intent/INT-1-security-baseline.md#s10--a-registrar-manages-components
[i1-s11]: ../../intent/INT-1-security-baseline.md#s11--retiring-a-component-takes-deliberate-steps
[i1-s12]: ../../intent/INT-1-security-baseline.md#s12--the-page-that-belongs-to-no-component
[i1-s13]: ../../intent/INT-1-security-baseline.md#s13--it-all-works-without-github
[i1-s14]: ../../intent/INT-1-security-baseline.md#s14--taking-access-away-is-immediate
[i1-s15]: ../../intent/INT-1-security-baseline.md#s15--only-the-source-closes-a-handoff
[i1-s16]: ../../intent/INT-1-security-baseline.md#s16--a-page-can-only-be-written-where-the-caller-may-write
[i6]: ../../intent/INT-6-installer.md
[i6-p]: ../../intent/INT-6-installer.md#proposed-outcome
[i6-c]: ../../intent/INT-6-installer.md#constraints
[i6-oq]: ../../intent/INT-6-installer.md#open-questions
[i6-s1]: ../../intent/INT-6-installer.md#s1--from-nothing-to-a-handoff
[i6-s2]: ../../intent/INT-6-installer.md#s2--run-it-again
[i6-s3]: ../../intent/INT-6-installer.md#s3--create-the-repository-on-github
[i6-s4]: ../../intent/INT-6-installer.md#s4--first-administrator
[i7]: ../../intent/INT-7-github-app.md
[i7-c]: ../../intent/INT-7-github-app.md#constraints
[i7-oq]: ../../intent/INT-7-github-app.md#open-questions
[i14]: ../../intent/INT-14-github-api-store.md
[i18]: ../../intent/INT-18-claude-desktop-access.md
[i19]: ../../intent/INT-19-mcp-authorization-server.md
