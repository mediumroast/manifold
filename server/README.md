<!-- SPDX-License-Identifier: Apache-2.0 -->
# Manifold server

An MCP server that gives AI agents and people one shared place to keep what a group of repositories needs to know about each other: component pages, architecture notes, decisions, and **handoffs**, the units of work one component's agent passes to another's. It serves one *instance*, a git repository of Markdown pages, over HTTP.

> **Security.** Every request except `GET /health` needs a credential issued to a person, agent or service, and every change in git names who made it. There is no setting that turns this off: with no principal in the store the server starts, warns and refuses every request. Administration (credentials, roles, grants, settings, purge) happens only on the host, never over MCP or HTTP. TLS is a setting served by a Caddy container; see the [TLS guide](../docs/tls.md). Claude Desktop and claude.ai cannot connect yet (a known limitation, [INT-18](../intent/INT-18-claude-desktop-access.md)). See [Known limits](#known-limits).

## What it does

- **MCP over HTTP** for Claude Code, VS Code (GitHub Copilot) and other MCP clients: 16 tools to read and write pages, run the handoff lifecycle, register, update and archive components and install helper files.
- **Per-principal access.** Four additive roles (reader, contributor, registrar, admin) plus per-component grants and denies decide what each credential may do; the page tools write only where the caller may.
- **Etag-checked writes.** A write names the version it started from; a stale write is refused, so two agents cannot silently overwrite each other.
- **Everything is a git commit,** authored by the principal behind the credential. The server never pushes.
- **A wiki browser** at `/docs/`, served by the server itself with no outside requests.
- **A document ingest endpoint** (`POST /ingest`) so a script can file a document under `raw/<component>/` without an agent reading it.

The agents, rules and document templates themselves are not part of the server. They live in [`bundles/`](../bundles/base/README.md) and are installed into a component repository by the bundle's installer; the server only says which bundles it carries and how to install them (`wiki_bundle_info_tool`).

## Run it

**With Docker (recommended):** run `./manifold init` from the repository root; see the [quickstart](../docs/quickstart.md). It builds the image, starts the server and Caddy, creates a first administrator, you and a first agent, and a first handoff. By hand:

```bash
cp -R examples/starter ~/my-wiki && (cd ~/my-wiki && git init -q && git add -A && git commit -q -m "Start my wiki")
./svc_ctl.sh dev init-env          # writes docker/.env.dev and a private data folder
# edit docker/.env.dev: set WIKI_ROOT to the absolute path of ~/my-wiki
./svc_ctl.sh dev admin principal create me --kind human     # then: role set, grant add, credential issue
./svc_ctl.sh dev start
```

**Directly, without Docker** (Python 3.11 or newer, git):

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -c server/requirements.lock
export CONTAINER_WIKI_ROOT=$HOME/my-wiki MANIFOLD_DATA_DIR=$HOME/.manifold-data     # the data folder must be outside the wiki
./manifold admin --data-dir "$MANIFOLD_DATA_DIR" --wiki-root "$CONTAINER_WIKI_ROOT" principal create me
# ... role set, grant add, credential issue --secret-file FILE
.venv/bin/python server/server.py
```

It listens on `127.0.0.1:8686` and does not reload, with no TLS: keep it on loopback or put it behind the Caddy setup. Started with a `MANIFOLD_HOST` that is not loopback and no principal, it refuses to start and names `./manifold init`.

## Configuration

The instance's own settings are in its `manifold.yaml`; see [manifold.yaml reference](../docs/manifold-yaml.md). The server process reads these environment variables:

| Variable | Default | What it does |
|---|---|---|
| `CONTAINER_WIKI_ROOT` | `/workspace` | Path of the instance repository. The container image sets it to `/workspace`, where compose mounts your instance. |
| `MANIFOLD_DATA_DIR` | `/data` | The folder of the security store (`manifold.db`: principals, hashed credentials, roles, grants, audit). Must be outside the instance; mode 0700. The container image sets `/data`. |
| `MANIFOLD_STORE_JOURNAL_MODE` | `wal` (the container image sets `delete`) | SQLite journal mode of the store. `delete` is for a data folder shared between two container processes on a bind mount (Docker Desktop), where `wal` fails. |
| `PORT` | `8686` | Port to listen on. |
| `MANIFOLD_HOST` | `127.0.0.1` (the container image sets `0.0.0.0`) | Address to listen on. |
| `MANIFOLD_PUBLIC_ADDRESS` | none | The address the deployment exposes the server on, for the rule "no principal yet: refuse to start on a non-loopback address". The compose files set it to `BIND_ADDRESS`, because inside the container the server listens on `0.0.0.0` behind Caddy. Falls back to `MANIFOLD_HOST`. |
| `MANIFOLD_TLS` | `off` | `off` or `on`: whether Caddy serves HTTPS (the starting value of the `tls` setting). |
| `MANIFOLD_ALLOWED_HOSTS` | none | Extra `Host` values accepted, comma separated (the starting value of `allowed_hosts`). |
| `MANIFOLD_ALLOWED_ORIGINS` | none | Extra `Origin` values accepted for requests that change things (`allowed_origins`). |
| `MANIFOLD_TRUSTED_PROXIES` | none | Addresses or networks whose `X-Forwarded-For` is trusted (`trusted_proxies`); the compose files set the Caddy network. |
| `MANIFOLD_INGEST_MAX_BYTES` | `1048576` | Largest document `/ingest` accepts. |
| `MANIFOLD_GIT_NAME`, `MANIFOLD_GIT_EMAIL` | `manifold`, `manifold@localhost` | The committer of the commits the server makes (the author is the principal). |
| `MANIFOLD_RELOAD` | off | Set to `1` to reload on code changes. For development only. |
| `MANIFOLD_ASSETS_DIR` | the repository's `assets/` | Where the core assets are. Rarely needed. |
| `MANIFOLD_BUNDLES_DIR` | the repository's `bundles/` | Where the bundles are. Rarely needed. |

`MANIFOLD_TLS`, `MANIFOLD_ALLOWED_*` and `MANIFOLD_TRUSTED_PROXIES` only give a starting value; a value set on the host (`admin settings set`) wins. All other limits and options are settings in the store, listed in [Operations](../docs/operations.md#limits-and-settings). The old `MANIFOLD_TOKEN` and `MANIFOLD_TOKEN_FILE` are **no longer read**; the server logs that they are ignored. (In client examples and helper scripts `MANIFOLD_TOKEN` is still the name of the variable that holds *your own* credential.)

The compose files add `WIKI_ROOT` (the host path of your instance), `DATA_DIR` (the host path of the data folder), `BIND_ADDRESS` (the host address the port is published on, `127.0.0.1` by default), `TLS_NAMES`, `ALLOWED_HOSTS` and `ENVIRONMENT`; see the `docker/.env.*.template` files.

## Endpoints

| Path | What | Credential needed |
|---|---|---|
| `/mcp` | MCP over Streamable HTTP. Use this one. | yes |
| `/sse`, `/messages/` | MCP over SSE, for clients that only speak it. A session belongs to the principal that opened it. | yes |
| `/ingest` | `POST` JSON `{component, content, doc_type?, filename?}`; writes `raw/<component>/<date>-<component>-<name>.md`. Needs a grant on the component (a registrar may file the first documents of a new one). | yes |
| `/docs/` | The wiki browser. A browser asks for a user name (anything) and a password (your credential). Needs the reader role. | yes |
| `/docs/raw/` | The instance's `raw/` folder, as files. | yes |
| `/health` | Health of the mounted instance. Without a credential it returns only `{"status": ...}`; with one, the individual checks. HTTP 200 when healthy, 500 when not. | no |

A client sends its credential as `Authorization: Bearer <credential>`. A wrong or missing credential gets `401` with the same body; a request for the wrong `Host` gets `421`; a changing request from a foreign `Origin` gets `403`; repeated bad credentials from one address get `429` with `Retry-After`. [`examples/clients/`](../examples/clients) has configuration for Claude Code and VS Code.

## Tools

| Tool | What it does |
|---|---|
| `wiki_ping_tool` | Confirms the connection; returns the server name, the tool list and who the server thinks you are (name, kind, roles). Call it first. |
| `wiki_onboarding_tool` | The registration protocol; with a component name, a pre-flight scan of what exists. |
| `wiki_register_component_tool` | Registers a component (adds it to `manifold.yaml`, the sidebar, the home page and the schema's slug list), or reconciles an existing page from raw documents (human registrar). Writes its own log entry. |
| `wiki_component_manage_tool` | Updates (description; repository and owner for a human registrar), archives (needs a reason, no open handoff) and restores a component. There is no purge here: that is host-only. |
| `wiki_reconcile_plan_tool` | For a registered component: a ready-to-run plan to bring its page up to date and install its agents. |
| `wiki_handoff_tool` | The whole handoff lifecycle: `create`, `claim`, `close`, `request-review`, `confirm`, `reject`, `list`. Only the source closes, confirms or rejects. |
| `wiki_read_tool` | Reads a page (under `wiki/` or `raw/`) and returns its content and etag. |
| `wiki_write_page_tool` | Creates or updates a component page or a shared page where the caller has a grant; an update needs the etag from the read. |
| `wiki_log_append_tool` | Appends an entry to the operation log, naming the calling principal. |
| `wiki_inventory_tool` | Lists the components (with their status), handoffs and pages. |
| `wiki_freshness_tool` | Reports component pages that are older than their raw source documents. |
| `wiki_bundle_info_tool` | Lists the agent bundles the server carries and the steps to install one. |
| `wiki_agent_catalog_tool` | Publishes a component's installed agents as a guide page in the wiki. |
| `wiki_list_helpers_tool`, `wiki_export_helper_tool`, `wiki_export_component_helpers_tool` | The handoff slash commands and the ingest script, as files to write into a component repository. |

No tool or route creates credentials, roles or grants.

## Develop and test

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements-dev.txt -c server/requirements.lock
cd server && ../.venv/bin/python -m pytest -q
```

The suite includes smoke tests that start the real server and use it as a client does, and a revocation test that changes credentials with the host command in another process while the server runs. It needs the repository's `assets/`, `examples/` and `bundles/`; tests that need a folder or Docker that is absent skip. The server needs Python 3.11 or newer (the container image uses 3.12). `requirements.lock` pins the exact versions that were tested; refresh it with the steps at the top of `requirements.txt`.

| Module | Role |
|---|---|
| `wiki_backend/config.py` | `manifold.yaml`: loading, validation, the component registry |
| `wiki_backend/auth.py`, `guard.py`, `actor.py` | Principal authentication (and the sign-in throttle), the tool and route guard, the acting principal |
| `wiki_backend/handoff.py`, `read.py`, `write.py`, `log.py` | Handoffs, page reads and etag-checked writes, the log |
| `wiki_backend/register.py`, `onboarding.py`, `inventory.py`, `freshness.py` | Registration and the checks around it |
| `wiki_backend/ingest.py`, `git.py`, `health.py` | `/ingest`, commits, health checks |
| `wiki_backend/assets.py`, `helpers.py`, `web.py`, `bundles.py`, `agent_guide.py` | Core assets with instance overrides, helper export, the wiki browser, bundle info, the agent catalog |
| `manifold_security/` | The security store (SQLite, standard library only), credentials, principals, roles, grants, the authorizer and tool policy, audit, settings, limits, path policy, the Host/Origin guard, the throttle, the startup rules, export |
| `manifold_cli/` | The host command: `admin ...`, `init` |

## Known limits

- **Claude Desktop and claude.ai cannot connect.** They need an authorization flow the server does not have ([INT-18](../intent/INT-18-claude-desktop-access.md), [INT-19](../intent/INT-19-mcp-authorization-server.md)).
- **No sign-in with GitHub and no repository permission** as a second route to write access yet; the authority setting per component exists and its repository arm answers "not available".
- **Reads are not limited per component.** Any signed-in reader reads everything.
- **The non-loopback start rule depends on the environment.** The "no principal yet: refuse to start" check uses `MANIFOLD_PUBLIC_ADDRESS` or `MANIFOLD_HOST`; starting `uvicorn` directly with another `--host` and neither set cannot be detected (the server still refuses every request until a principal exists).
- **One connection per process to the store.** A second open of the store's file in the same process breaks immediate revocation under the `wal` journal mode; the code avoids it (see `manifold_security/store.py`).
- **The server never pushes.** Changes exist in the instance's local history until you push them; see [Operations](../docs/operations.md#export-import-and-backup).
- **The Linux and CI parts are observed in CI, not on a developer machine,** for the first release of this security work.
