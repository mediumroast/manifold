<!-- SPDX-License-Identifier: Apache-2.0 -->
# Operations

How to run the server day to day. For first use, see the [quickstart](quickstart.md).

## The service script

`svc_ctl.sh` drives the containers. It takes an environment (`dev`, `staging` or `production`) and a command:

```bash
./svc_ctl.sh <environment> init-env   # create docker/.env.<environment> from its template, with a new token
./svc_ctl.sh <environment> start      # build if needed, start in the background
./svc_ctl.sh <environment> status
./svc_ctl.sh <environment> logs
./svc_ctl.sh <environment> health     # check the mounted instance without starting the server
./svc_ctl.sh <environment> restart    # recreate the service
./svc_ctl.sh <environment> rebuild    # pull the base image, rebuild from scratch, recreate
./svc_ctl.sh <environment> stop
./svc_ctl.sh <environment> shell      # a shell inside the container
```

The three environments differ only in their settings file and in what is mounted: **`dev` also mounts the server's source over the image and reloads on change**, for working on the server itself. `staging` and `production` run the image as built: no source mount, no reload, read-only root file system, all capabilities dropped. Use `dev` to try things and `production` (or `staging`) for a wiki people rely on. Each environment has its own `docker/.env.<environment>`, its own token and its own instance path.

## Settings

`docker/.env.<environment>` holds `WIKI_ROOT` (the absolute host path of the instance), `PORT`, `ENVIRONMENT`, `BIND_ADDRESS` and `MANIFOLD_TOKEN`. The file holds a secret and is created readable by you only; `.gitignore` and `.dockerignore` keep it out of git and out of the image, but do not add it to a repository by hand or copy it into another one. `MANIFOLD_GIT_NAME`, `MANIFOLD_GIT_EMAIL` and `MANIFOLD_INGEST_MAX_BYTES` are passed through to the server when you add them to the file; the other server variables ([server README](../server/README.md#configuration)) need a line in `docker/docker-compose.yml` as well.

## The token

Everything except `GET /health` needs the token.

- **Rotate it:** put a new value in the `MANIFOLD_TOKEN=` line (at least 24 characters; `python3 -c 'import secrets; print(secrets.token_urlsafe(32))'` makes a good one), run `restart`, and give the new value to every client and every person who uses the browser. There is one token, so rotating it signs everybody out.
- **Treat it as a password.** Anyone with it can read and write the whole wiki. Do not put it in a repository, a chat or a screenshot.
- **From a file instead:** the server also reads the token from the file named by `MANIFOLD_TOKEN_FILE` (for a container secret). The compose file provided here requires `MANIFOLD_TOKEN`, so using a secret file means adapting that file.

## Network and TLS

The port is published on `127.0.0.1` only, so only the machine itself can reach it. That is the safe default. To let other people reach it:

1. Keep `BIND_ADDRESS=127.0.0.1`.
2. Put a reverse proxy on the same machine in front of it that terminates TLS and forwards to `127.0.0.1:8686`. The proxy must not buffer responses: the `/mcp` and `/sse` endpoints stream.
3. Give the token only to the people who should have full access.

The server has no TLS of its own, and without it the token crosses the network in clear text. Do not set `BIND_ADDRESS` to a public or shared address without something in front that provides TLS. The [known limits](../server/README.md#known-limits) list what is still missing.

## Back it up

The instance is a git repository, and **the server commits to it but never pushes**. Until you push, the only copy of the history is on that machine's disk. Add a remote and push on a schedule you trust:

```bash
cd ~/my-wiki
git remote add origin <the address of a private repository>
git push -u origin HEAD
```

Then repeat `git push` regularly, for example from a scheduled job. A copy of the folder is equally a backup. The server writes only inside the instance, so the instance folder (plus your `docker/.env.*` files, which hold the tokens) is everything that needs saving.

Do not pull into the instance while the server is running unless nobody is writing: the server commits to whatever branch is checked out.

## Update the server

```bash
git pull                              # in your clone of manifold
./svc_ctl.sh <environment> rebuild
```

Then check `./svc_ctl.sh <environment> health`. The instance is untouched by an update. If a new version asks for a change to `manifold.yaml` or the schema page, its release notes will say so.

To update the **agents and handoff commands** in a component repository, run the bundle's installer again (it keeps files you edited), and ask a tool to run `/manifold-update`, which fetches the current handoff commands from the server.

## When something is wrong

| What you see | Likely cause | What to do |
|---|---|---|
| `svc_ctl.sh` says `WIKI_ROOT ... is not a folder` or `No manifold.yaml in ...` | `WIKI_ROOT` is still the placeholder, has a `~`, or is not an instance | Set it to the absolute path of a folder with `manifold.yaml` |
| Compose says `set MANIFOLD_TOKEN in the environment file` | The `MANIFOLD_TOKEN=` line is empty (for example an older settings file) | Add a token, or delete the file and run `init-env` |
| `/health` says `unhealthy` | A failed check | Call it with the token: `checks` names the one: `wiki_root` (mount missing), `wiki/CLAUDE.md` or `wiki/log.md` (page missing), `manifold.yaml` (missing or invalid), `wiki writable` (the container's user cannot write the instance folder) |
| `401` from a client, or the browser keeps asking | Wrong or missing token | Check the header is `Authorization: Bearer <token>`; in the browser the user name is ignored and the password is the token |
| The server refuses to start: `Refusing to listen on ... without authentication` | A non-loopback address with no token | Set `MANIFOLD_TOKEN` |
| The server refuses to start: `The token is too short` | Fewer than 24 characters | Use a longer one |
| Changes are not committed (`committed: false`, "not a git repository" or "inside another git repository") | The instance folder is not the top level of its own repository | Run `git init` in the instance folder; do not nest it in another repository |
| Files in the instance are owned by root, or `wiki writable` fails | The container's user does not match the folder's owner | `svc_ctl.sh` runs the container as your user; if you start compose yourself, set `HOST_UID` and `HOST_GID` |
| A write answers `conflict` | The page changed since it was read | Read it again and redo the change; this is working as intended |
| `/ingest` answers `413` | The document is larger than the limit | Raise `MANIFOLD_INGEST_MAX_BYTES` or split the document |
| Port already in use | Another program has 8686 | Change `PORT` in the settings file and restart |

## What is not covered yet

Per-person sign-in, per-component permissions, rate limiting, an audit trail, TLS, and Host or Origin checks are not part of the server yet. The [known limits](../server/README.md#known-limits) and the [roadmap](../ROADMAP.md) say what is planned.
