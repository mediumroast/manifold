<!-- SPDX-License-Identifier: Apache-2.0 -->
# Operations

How to run the server day to day. For first use, see the [quickstart](quickstart.md); for HTTPS, the [TLS guide](tls.md).

## The service script

`svc_ctl.sh` drives the containers. It takes an environment (`dev`, `staging` or `production`) and a command:

```bash
./svc_ctl.sh <environment> init-env   # create docker/.env.<environment> from its template (and the data folder)
./svc_ctl.sh <environment> start      # build if needed, start in the background
./svc_ctl.sh <environment> status
./svc_ctl.sh <environment> logs
./svc_ctl.sh <environment> health     # check the mounted instance without starting the server
./svc_ctl.sh <environment> restart    # recreate the service
./svc_ctl.sh <environment> rebuild    # pull the base image, rebuild from scratch, recreate
./svc_ctl.sh <environment> stop
./svc_ctl.sh <environment> shell      # a shell inside the container
./svc_ctl.sh <environment> admin ...  # the host command, run inside the container (see below)
```

The three environments differ only in their settings file and in what is mounted: **`dev` also mounts the server's source over the image and reloads on change**, for working on the server itself. `staging` and `production` run the image as built: no source mount, no reload, read-only root file system, all capabilities dropped. Use `dev` to try things and `production` (or `staging`) for a wiki people rely on. Each environment has its own `docker/.env.<environment>`, its own data folder and its own instance path.

Two containers run: **manifold** (the server, on a network with no route out; nothing publishes its port) and **caddy** (publishes `BIND_ADDRESS:PORT` on the host and forwards to the server; it serves plain HTTP or HTTPS, see [TLS](tls.md)).

## Settings

`docker/.env.<environment>` holds `WIKI_ROOT` (the absolute host path of the instance), `DATA_DIR` (the absolute host path of the data folder), `PORT`, `ENVIRONMENT`, `BIND_ADDRESS`, `MANIFOLD_TLS`, `TLS_NAMES` and `ALLOWED_HOSTS`. It holds no secret; it is created readable by you only, and `.gitignore` and `.dockerignore` keep it out of git and out of the image. `MANIFOLD_GIT_NAME`, `MANIFOLD_GIT_EMAIL` and `MANIFOLD_INGEST_MAX_BYTES` are passed through to the server when you add them to the file; the other server variables ([server README](../server/README.md#configuration)) need a line in `docker/docker-compose.yml` as well.

The **data folder** (`DATA_DIR`, mounted at `/data`) holds the security store `manifold.db` (people, agents, hashed credentials, roles, grants, the audit trail) and Caddy's files. It is owned by you, mode 0700, and must be outside the instance repository: credentials never go into git. `svc_ctl.sh` refuses to start if it is inside the instance.

## People, agents and credentials

Everyone who uses the server is a **principal**: a `human`, an `agent` or a `service`, with a name. A principal signs in with a **credential** of its own (`mf_<id>_<secret>`), sent as `Authorization: Bearer <credential>`; a browser asks for it as the password (any user name). The server stores only a hash, so a credential is **shown once, when it is issued, and cannot be shown again**; if it is lost, issue a new one and revoke the old one.

All administration happens on the host, with the host command, never over MCP or HTTP:

```bash
./svc_ctl.sh production admin principal create ana --kind human
./svc_ctl.sh production admin role set ana contributor
./svc_ctl.sh production admin credential issue ana --label laptop --secret-file /data/ana.secret
```

Inside the container a secret file must be under `/data`; on the host it is then in your `DATA_DIR`, mode 0600. Move it where the client reads it and delete it from there. `--expires 30d` sets an expiry for one credential; there is none by default. From a Python checkout without Docker, `./manifold admin --data-dir <folder> --wiki-root <instance> ...` does the same; in Docker `./manifold admin --env production ...` hands the command to `svc_ctl.sh`.

| To do this | Run |
|---|---|
| list or inspect | `admin principal list`, `admin principal show <name>` (never shows a secret) |
| replace a credential | `admin credential rotate <credential id> --secret-file ...` |
| take one credential away | `admin credential revoke <credential id>` (it says what still works) |
| take a person or agent away entirely | `admin principal disable <name>` (all its credentials stop at once; `enable` restores) |
| see who did what | `admin audit show [--since 7d] [--principal ana] [--event credential.]` |

Taking access away is **immediate**: the next request is refused, with no restart. It is also **durable**, because the state is in the store, not in memory. Failed sign-ins are slowed down per address (5 failures in 10 minutes, then a delay that doubles from 1 second to 15 minutes) and written to the audit with the address, never the credential; a credential is never locked, so an attacker cannot lock a person out.

## Roles, grants and denies

A principal has any of four roles. They add up.

| Role | May do | Notes |
|---|---|---|
| `reader` | read every page, the inventory, the wiki browser | reading is not limited per component in this version |
| `contributor` | everything a reader may, plus write pages, append to the log, ingest documents and work handoffs, **on the components it has a grant for** (and `_shared`, for pages that belong to no component) | a role alone writes nothing: it needs a grant |
| `registrar` | register, update, archive and restore components | an agent registrar is limited (below); only a **human** registrar may change a component's repository or owner, or reconcile |
| `admin` | nothing over MCP or HTTP: run the host command | cannot be given to an agent or service; holds no access to the wiki's content |

A **grant** (`admin grant add ana acme-api`) lets a contributor write to one component; `_shared` stands for the pages that belong to no component (decisions, architecture, guides). A **deny** (`admin deny add ana acme-api`) refuses writes there whatever else the principal holds, and wins over a grant. Why a deny: removing a grant (`admin grant remove`) takes away one route, and the command tells you which routes remain (the reader and contributor roles still read everything; a component whose authority is `either` or `repo-write` will later accept repository permission too). To end writes in one place, add a deny; to end everything, disable the principal or revoke its credentials.

Only the **source** of a handoff closes it (the component that asked for the work). The target claims it and requests review; the source confirms or rejects.

By default a registrar who registers a component gets **no** grant on it; `admin registrar-flag set <name> --self-grant on` makes a registration also grant that principal write access to the new component (audited). Agents that register or archive are limited per UTC day (5 registrations, 1 archive by default); humans are not.

## Archiving and purging a component

A registrar archives a component with `wiki_component_manage_tool(action="archive", name=..., reason=...)`. It needs a reason and no open handoff (the refusal names them). An archived component refuses page writes, new handoffs and document ingest, and can be restored the same way (`action="restore"`). It is held for `purge_hold_days` (14 by default). **Removing it for good is host-only**, never over MCP:

```bash
./svc_ctl.sh production admin registry purge acme-api --confirm-slug acme-api
```

It refuses unless the component is archived, the hold has passed and no handoff involving it is open; without `--confirm-slug` it prints what it would remove and changes nothing. It removes the page, the agent guide, `raw/<slug>/`, the registry entry, the sidebar links and the grants and denies, in one git commit authored by `host:<your user>`. Completed handoff pages are kept as history, and git history keeps everything, so `git revert` of that commit in the instance brings the files back.

## Limits and settings

All limits are settings with defaults, changed on the host: `admin settings list`, `admin settings set <key> <value>`, `admin settings unset <key>`. Out-of-range values are refused with the range.

| Setting | Default | Meaning |
|---|---|---|
| `agent_registrations_per_day` | 5 | components an agent or service may register per UTC day |
| `agent_archives_per_day` | 1 | components an agent or service may archive per UTC day |
| `purge_hold_days` | 14 | days an archived component is held before a purge |
| `throttle_failure_threshold` | 5 | failed sign-ins per address within the window before delays start |
| `throttle_window_seconds` | 600 | the window |
| `throttle_base_delay_seconds` | 1 | the first delay |
| `throttle_max_delay_seconds` | 900 | the longest delay |
| `allowed_hosts` | (empty) | extra `Host` values accepted besides `127.0.0.1`, `localhost` and `[::1]` on the served port |
| `allowed_origins` | (empty) | extra `Origin` values accepted for requests that change things |
| `trusted_proxies` | (empty; the container files set the Caddy network) | addresses whose `X-Forwarded-For` is trusted |
| `tls` | `off` | whether Caddy serves HTTPS (set by `MANIFOLD_TLS` in the settings file) |

`allowed_hosts`, `allowed_origins`, `trusted_proxies` and `tls` start from the environment variables `MANIFOLD_ALLOWED_HOSTS`, `MANIFOLD_ALLOWED_ORIGINS`, `MANIFOLD_TRUSTED_PROXIES` and `MANIFOLD_TLS` that the compose file sets; a value stored with `admin settings set` wins. **There is no setting, flag or variable that turns authentication off.** A server with no principal refuses every request until one exists, and refuses to start at all when it is published on an address other than loopback.

A request for the wrong `Host`, or a `POST`, `PUT`, `PATCH` or `DELETE` carrying an `Origin` that is not one of the served origins, is refused before the credential is looked at.

## Export, import and backup

`admin export <file>` writes one JSON file: principals, roles, grants, denies, per-component authority and settings. It contains **no credentials and no hashes** unless you add `--with-hashes` (then credentials keep working after an import on another host; keep that file as private as the data folder). `admin import <file>` into an empty store loads it; into a store that already has principals it needs `--merge` or `--replace`; `--dry-run` shows what would change. The whole file is checked before anything is written.

To **back up**, save the instance (below) and the data folder, or an export plus the instance. Copy the data folder only while the service is stopped (`stop`), or use `admin export --with-hashes` while it runs; do not copy `manifold.db` by itself from a running server.

The instance is a git repository, and **the server commits to it but never pushes**. Until you push, the only copy of the history is on that machine's disk. Add a remote and push on a schedule you trust:

```bash
cd ~/my-wiki
git remote add origin <the address of a private repository>
git push -u origin HEAD
```

Then repeat `git push` regularly, for example from a scheduled job. Every commit names the principal behind the credential (the author and a `Manifold-Principal` line). Do not pull into the instance while the server is running unless nobody is writing: the server commits to whatever branch is checked out.

## Update the server

```bash
git pull                              # in your clone of manifold
./svc_ctl.sh <environment> rebuild
```

Then check `./svc_ctl.sh <environment> health`. The instance is untouched by an update. If a new version asks for a change to `manifold.yaml` or the schema page, its release notes will say so. The host command (`admin ...`) runs from the same image, so rebuild before using a new command.

To update the **agents and handoff commands** in a component repository, run the bundle's installer again (it keeps files you edited), and ask a tool to run `/manifold-update`, which fetches the current handoff commands from the server.

### Upgrade from the shared token

Older versions protected everything with one shared `MANIFOLD_TOKEN`. It is no longer accepted: after the upgrade the server refuses every request until principals exist, and it logs a notice saying so. In order:

1. `./svc_ctl.sh <environment> stop`.
2. `git pull` in your clone of manifold (the image is rebuilt when you start in step 5).
3. Create the first principals. Easiest: `./manifold init --env <environment>`. It finds your existing settings file and instance, **adds only the settings that are missing** (`DATA_DIR`, `MANIFOLD_TLS`, ...), keeps the old `MANIFOLD_TOKEN` line untouched, creates the data folder, an administrator, a principal for you and a first agent, and starts the server. Or by hand: add `DATA_DIR=<an absolute path outside the instance>` to the settings file, then `./svc_ctl.sh <environment> admin principal create <name>`, `admin role set`, `admin grant add`, `admin credential issue` as above.
4. Issue a credential for every person and every agent that used the token (`admin credential issue <name> --secret-file /data/<name>.secret`) and give each one theirs. Clients that sent the shared token as `Authorization: Bearer <token>` now send their own credential in the same header; in the examples and helper scripts the variable `MANIFOLD_TOKEN` is just the name of the variable that holds *your own* credential.
5. `./svc_ctl.sh <environment> start`. The log says `MANIFOLD_TOKEN ... is no longer accepted` if the old variable is still set; delete the `MANIFOLD_TOKEN=` line from `docker/.env.<environment>` (`start` warns about it too).
6. Check: a request with no credential gets `401`, one with a credential gets `200`, the old token value gets `401`.

## When something is wrong

| What you see | Likely cause | What to do |
|---|---|---|
| `svc_ctl.sh` says `WIKI_ROOT ... is not a folder` or `No manifold.yaml in ...` | `WIKI_ROOT` is still the placeholder, has a `~`, or is not an instance | Set it to the absolute path of a folder with `manifold.yaml` |
| `svc_ctl.sh` says `DATA_DIR is not set` or `inside the instance repository` | An older settings file, or a data folder in git | Set `DATA_DIR` to an absolute path outside the instance |
| `svc_ctl.sh` says `BIND_ADDRESS ... with MANIFOLD_TLS=off` | Plain HTTP on an address the network can reach | Set `MANIFOLD_TLS=on` ([TLS](tls.md)), or bind `127.0.0.1` |
| `/health` says `unhealthy` | A failed check | Call it with a credential: `checks` names the one: `wiki_root` (mount missing), `wiki/CLAUDE.md` or `wiki/log.md` (page missing), `manifold.yaml` (missing or invalid), `wiki writable` (the container's user cannot write the instance folder) |
| `401` from a client, or the browser keeps asking | Wrong, missing, revoked or expired credential | The header is `Authorization: Bearer <credential>`; in the browser the user name is ignored and the password is the credential. `your access was removed or has expired` means a correct credential that was revoked, expired or whose principal is disabled |
| `421` | The `Host` header is not one the server accepts | Reach it by `127.0.0.1`, `localhost` or `[::1]` on the served port, or add the name to `ALLOWED_HOSTS` |
| `403` on a write | The origin is foreign, or the principal lacks the role or grant | `admin principal show <name>`; the error says which |
| `429` | Too many failed sign-ins from that address | Wait the `Retry-After` seconds; a correct credential from another address is unaffected |
| The server refuses to start: `no principal exists yet` | Published on a non-loopback address before the first administrator | `./manifold init`, or `admin principal create`, then start |
| The server logs `No principals exist` | Empty store (this is normal on a first start on loopback) | It refuses every request until the first principal is created: `./manifold init` |
| Changes are not committed (`committed: false`, "not a git repository" or "inside another git repository") | The instance folder is not the top level of its own repository | Run `git init` in the instance folder; do not nest it in another repository |
| Files in the instance are owned by root, or `wiki writable` fails | The container's user does not match the folder's owner | `svc_ctl.sh` runs the container as your user; if you start compose yourself, set `HOST_UID` and `HOST_GID` |
| A write answers `conflict` | The page changed since it was read | Read it again and redo the change; this is working as intended |
| `/ingest` answers `413` | The document is larger than the limit | Raise `MANIFOLD_INGEST_MAX_BYTES` or split the document |
| Port already in use | Another program has 8686 | Change `PORT` in the settings file and restart |

## What is not covered yet

Sign-in with GitHub, repository permission as a second way to get write access, an MCP authorization server and access from Claude Desktop and claude.ai are not part of the server yet. The [known limits](../server/README.md#known-limits) and the [roadmap](../ROADMAP.md) say what is planned.
