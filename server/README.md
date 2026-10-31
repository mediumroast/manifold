<!-- SPDX-License-Identifier: Apache-2.0 -->
# Manifold server

An MCP server that gives AI agents and people one shared place to keep what a group of repositories needs to know about each other: component pages, architecture notes, decisions, and **handoffs**, the units of work one component's agent passes to another's. It serves one *instance*, a git repository of Markdown pages, over HTTP.

> **Security: there is one shared token and nothing else yet.**
> Anyone who has the token can read and write everything in the wiki. There is no per-person sign-in, no permissions per component, no rate limiting, no audit trail and no TLS. Do not expose this server to a network you do not control, and put a TLS-terminating proxy in front of it before sending the token over any network you do not fully trust. Per-person sign-in, permissions and TLS are the next planned work. See [Known limits](#known-limits).

## What it does

- **MCP over HTTP** for Claude Code, VS Code (GitHub Copilot) and other MCP clients: 15 tools to read and write pages, run the handoff lifecycle, register components and install helper files.
- **Etag-checked writes.** A write names the version it started from; a stale write is refused, so two agents cannot silently overwrite each other.
- **Everything is a git commit.** The server commits each change in the instance repository. It never pushes.
- **A wiki browser** at `/docs/`, served by the server itself with no outside requests.
- **A document ingest endpoint** (`POST /ingest`) so a script can file a document under `raw/<component>/` without an agent reading it.

The agents, rules and document templates themselves are not part of the server. They live in [`bundles/`](../bundles/base/README.md) and are installed into a component repository by the bundle's installer; the server only says which bundles it carries and how to install them (`wiki_bundle_info_tool`).

## Run it

**With Docker (recommended):** follow the [quickstart](../docs/quickstart.md). In short:

```bash
cp -R examples/starter ~/my-wiki && (cd ~/my-wiki && git init -q && git add -A && git commit -q -m "Start my wiki")
./svc_ctl.sh dev init-env          # writes docker/.env.dev with a generated token
# edit docker/.env.dev: set WIKI_ROOT to the absolute path of ~/my-wiki
./svc_ctl.sh dev start
```

**Directly, without Docker** (Python 3.11 or newer, git):

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -c server/requirements.lock
CONTAINER_WIKI_ROOT=$HOME/my-wiki \
MANIFOLD_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')" \
  .venv/bin/python server/server.py
```

It listens on `127.0.0.1:8686` and does not reload. The token is optional on loopback (the server warns that authentication is off); it is required on any other address.

## Configuration

The instance's own settings are in its `manifold.yaml`; see [manifold.yaml reference](../docs/manifold-yaml.md). The server process reads these environment variables:

| Variable | Default | What it does |
|---|---|---|
| `CONTAINER_WIKI_ROOT` | `/workspace` | Path of the instance repository. The container image sets it to `/workspace`, where compose mounts your instance. |
| `PORT` | `8686` | Port to listen on. |
| `MANIFOLD_HOST` | `127.0.0.1` (the container image sets `0.0.0.0`) | Address to listen on. Anything other than loopback requires a token. |
| `MANIFOLD_TOKEN` | none | The shared secret: at least 24 characters. When set, every path except `GET /health` requires it. |
| `MANIFOLD_TOKEN_FILE` | none | Path of a file that holds the token (for container secrets). `MANIFOLD_TOKEN` wins if both are set. |
| `MANIFOLD_INGEST_MAX_BYTES` | `1048576` | Largest document `/ingest` accepts. |
| `MANIFOLD_GIT_NAME`, `MANIFOLD_GIT_EMAIL` | `manifold`, `manifold@localhost` | The author of the commits the server makes. |
| `MANIFOLD_RELOAD` | off | Set to `1` to reload on code changes. For development only. |
| `MANIFOLD_ASSETS_DIR` | the repository's `assets/` | Where the core assets are. Rarely needed. |
| `MANIFOLD_BUNDLES_DIR` | the repository's `bundles/` | Where the bundles are. Rarely needed. |

The compose files add `WIKI_ROOT` (the host path of your instance), `BIND_ADDRESS` (the host address the port is published on, `127.0.0.1` by default) and `ENVIRONMENT`; see the `docker/.env.*.template` files.

## Endpoints

| Path | What | Token needed |
|---|---|---|
| `/mcp` | MCP over Streamable HTTP. Use this one. | yes |
| `/sse`, `/messages/` | MCP over SSE, for clients that only speak it. | yes |
| `/ingest` | `POST` JSON `{component, content, doc_type?, filename?}`; writes `raw/<component>/<date>-<component>-<name>.md`. | yes |
| `/docs/` | The wiki browser. A browser asks for a user name (anything) and a password (the token). | yes |
| `/docs/raw/` | The instance's `raw/` folder, as files. | yes |
| `/health` | Health of the mounted instance. Without the token it returns only `{"status": ...}`; with it, the individual checks. HTTP 200 when healthy, 500 when not. | no |

A client sends the token as `Authorization: Bearer <token>`. [`examples/clients/`](../examples/clients) has configuration for Claude Code and VS Code.

## Tools

| Tool | What it does |
|---|---|
| `wiki_ping_tool` | Confirms the connection; returns the server name and the tool list. Call it first. |
| `wiki_onboarding_tool` | The registration protocol; with a component name, a pre-flight scan of what exists. |
| `wiki_register_component_tool` | Registers a component (adds it to `manifold.yaml`, the sidebar, the home page and the schema's slug list), or reconciles an existing page from raw documents. |
| `wiki_reconcile_plan_tool` | For a registered component: a ready-to-run plan to bring its page up to date and install its agents. |
| `wiki_handoff_tool` | The whole handoff lifecycle: `create`, `claim`, `close`, `request-review`, `confirm`, `reject`, `list`. |
| `wiki_read_tool` | Reads a page and returns its content and etag. |
| `wiki_write_page_tool` | Creates or updates a page; an update needs the etag from the read. |
| `wiki_log_append_tool` | Appends an entry to the operation log. |
| `wiki_inventory_tool` | Lists the components, handoffs and pages. |
| `wiki_freshness_tool` | Reports component pages that are older than their raw source documents. |
| `wiki_bundle_info_tool` | Lists the agent bundles the server carries and the steps to install one. |
| `wiki_agent_catalog_tool` | Publishes a component's installed agents as a guide page in the wiki. |
| `wiki_list_helpers_tool`, `wiki_export_helper_tool`, `wiki_export_component_helpers_tool` | The handoff slash commands and the ingest script, as files to write into a component repository. |

## Develop and test

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements-dev.txt -c server/requirements.lock
cd server && ../.venv/bin/python -m pytest -q
```

The suite includes a smoke test that starts the real server and uses it as a client does. It needs the repository's `assets/`, `examples/` and `bundles/`; tests that need a folder that is absent skip. The server needs Python 3.11 or newer (the container image uses 3.12). `requirements.lock` pins the exact versions that were tested; refresh it with the steps at the top of `requirements.txt`.

| Module (`wiki_backend/`) | Role |
|---|---|
| `config.py` | `manifold.yaml`: loading, validation, the component registry |
| `auth.py` | The shared token and its middleware |
| `handoff.py`, `read.py`, `write.py`, `log.py` | Handoffs, page reads and etag-checked writes, the log |
| `register.py`, `onboarding.py`, `inventory.py`, `freshness.py` | Registration and the checks around it |
| `ingest.py`, `git.py`, `health.py` | `/ingest`, commits, health checks |
| `assets.py`, `helpers.py`, `web.py`, `bundles.py`, `agent_guide.py` | Core assets with instance overrides, helper export, the wiki browser, bundle info, the agent catalog |

## Known limits

These are the gaps the next work closes. Until then:

- **One secret for everyone.** No per-person identity, no per-component permission, and no way to revoke one person's access except by changing the token for all.
- **No rate limiting.** The 24-character minimum is the only protection against guessing.
- **No audit trail** beyond the git history and the log.
- **No TLS.** On a shared network the token travels in clear text unless something in front terminates TLS.
- **No Host or Origin validation.**
- **The bind-address rule is enforced through `MANIFOLD_HOST` only.** Starting `uvicorn` directly with another `--host` bypasses it.
- **The server never pushes.** Changes exist in the instance's local history until you push them; see [Operations](../docs/operations.md#back-it-up).
- **The container image has not been built by the project's own checks yet.** The compose files were validated, and the build steps were run outside Docker, but treat a first `docker compose up` as a test.
