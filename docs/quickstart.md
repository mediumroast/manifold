<!-- SPDX-License-Identifier: Apache-2.0 -->
# Quickstart: a running, protected Manifold server in one command

You will run one command that sets everything up on your own machine: a wiki of your own, a server that refuses everyone without a credential, a credential for you and one for a first agent, two sample components and a first handoff, read back. Then you will connect an AI tool.

**What you need:** Linux or macOS; git; Docker with Compose, running; Python 3.11 or newer. Nothing is sent outside your machine and no GitHub account is needed.

> **Before you start:** there is no shared password any more. Every person and every agent has a credential of their own, and the server refuses every request without one. By default the server is reachable on your machine only (`127.0.0.1`). To let other people reach it, see [TLS](tls.md).

## 1. Get the code

```bash
git clone https://github.com/mediumroast/manifold.git
cd manifold
```

## 2. Run `./manifold init`

```bash
./manifold init
```

It checks your machine (platform, Python, git, Docker, the port), looks for anything that already exists, and then **shows you the whole plan and waits for a yes** before creating anything:

- the instance (your wiki, a git repository of its own, beside the checkout: `manifold-instance`),
- the data folder (the security store; private to you),
- the settings file `docker/.env.production`,
- three principals: an **administrator** (runs the host command, cannot read the wiki), **you** (can read, and write to the two sample components and the shared pages) and a **first agent** (can also register components),
- a credential for you and one for the agent, each written to a file that only you can read. **They are shown nowhere else and cannot be shown again.**

After your yes it builds and starts the server (the first time takes a few minutes), checks that a request with no credential is refused, acts as the first agent to register `example-api` and `example-web`, creates a handoff between them, reads it back, and checks that your credential can read it but cannot register components. If any step fails, it removes everything that run created and says what to fix.

Useful options: `--instance PATH`, `--data-dir PATH`, `--port N`, `--name YOURNAME`, `--person-secret-file FILE`, `--agent-secret-file FILE`, `--env dev|staging|production`, and `--yes` for scripts. Run it again whenever you like: it detects what exists, offers to create only what is missing, and **changes nothing without your yes** and never touches a credential.

## 3. Look at it

Open <http://127.0.0.1:8686/docs/> (or the port you chose). The browser asks for a user name and a password: use any user name and the contents of **your credential file** as the password. You will see the two components and the first handoff.

## 4. Connect an AI tool

The server speaks MCP at `http://127.0.0.1:8686/mcp` and wants your credential as a bearer header. `./manifold init` printed the exact steps at the end; in short:

**Claude Code:** copy [`examples/clients/claude-code-mcp.json`](../examples/clients/claude-code-mcp.json) to `.mcp.json` in your component repository and start Claude Code with the variable set (`MANIFOLD_TOKEN` is only the *name* of the variable that holds your own credential):

```bash
MANIFOLD_TOKEN="$(cat /path/to/your/credential-file)" claude
```

**VS Code (GitHub Copilot):** copy [`examples/clients/vscode-mcp.json`](../examples/clients/vscode-mcp.json) to `.vscode/mcp.json`. VS Code asks for the credential once and keeps it out of the file.

Claude Desktop and claude.ai are **not supported yet**; they need an authorization flow the server does not have ([INT-18](../intent/INT-18-claude-desktop-access.md)).

Start a session and ask the tool to call `wiki_ping_tool`. It should answer `connected`, with the server name `manifold`, 16 tools and **you** as the principal.

## 5. Try a handoff

A handoff passes a piece of work from one component's agent to another's. Your credential reads everything, but writes only where you have a grant; the first agent's credential created the sample handoff. Ask your tool, in plain words:

> Using the manifold server, list the open handoffs. Then read the one from `example-api` to `example-web`.

To write as yourself, ask your tool to create a handoff from `example-web` to `example-api`: you hold a grant on both. Behind the scenes it calls `wiki_handoff_tool` with `action: "create"`. In your instance, `git log` shows each commit with **the principal that made it** as the author. The full lifecycle (claim, request review, the *source* confirms or closes) is in [Concepts](concepts.md#handoffs).

## 6. Make it yours

Register your own components with `wiki_register_component_tool` (needs the registrar role: use the first agent, or give yourself the role with `./svc_ctl.sh production admin role set YOURNAME registrar`), and give people and agents credentials with the host command; see [Operations](operations.md#people-agents-and-credentials).

## Next

- **Put the agents in your repositories.** The server does not hold the agents; the bundle does. Ask your tool for `wiki_bundle_info_tool`, or read [the bundle's README](../bundles/base/README.md).
- **Install the handoff commands** in a component repository with `wiki_export_component_helpers_tool`. They add `/handoff-create`, `/handoff-pickup`, `/handoff-close` and a few more to Claude Code and Copilot.
- **Back it up.** The server never pushes; see [Operations](operations.md#export-import-and-backup).
- Stop everything with `./svc_ctl.sh production stop` (or the environment you chose).

## Advanced: by hand

`./manifold init` does these steps; do them yourself if you prefer.

```bash
cp -R examples/starter ~/my-wiki                 # or examples/acme for a filled-in example
cd ~/my-wiki && git init -q && git add -A && git commit -q -m "Start my wiki" && cd -
./svc_ctl.sh dev init-env                        # creates docker/.env.dev and a private data folder
# edit docker/.env.dev: set WIKI_ROOT to the ABSOLUTE path of ~/my-wiki
./svc_ctl.sh dev admin principal create me --kind human
./svc_ctl.sh dev admin role set me contributor
./svc_ctl.sh dev admin grant add me _shared
./svc_ctl.sh dev admin credential issue me --secret-file /data/me.secret    # lands in DATA_DIR, mode 0600
./svc_ctl.sh dev start
curl -s http://127.0.0.1:8686/health                                         # {"status":"healthy"}
curl -s -H "Authorization: Bearer $(cat .manifold-data/dev/me.secret)" http://127.0.0.1:8686/health   # the checks
```

Without credentials the server still starts, but refuses every request and logs that no principal exists.

### Without Docker

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -c server/requirements.lock
export CONTAINER_WIKI_ROOT=$HOME/my-wiki MANIFOLD_DATA_DIR=$HOME/.manifold-data     # the data folder must be outside the wiki
./manifold admin --data-dir "$MANIFOLD_DATA_DIR" --wiki-root "$CONTAINER_WIKI_ROOT" principal create me
./manifold admin --data-dir "$MANIFOLD_DATA_DIR" --wiki-root "$CONTAINER_WIKI_ROOT" role set me contributor
./manifold admin --data-dir "$MANIFOLD_DATA_DIR" --wiki-root "$CONTAINER_WIKI_ROOT" credential issue me --secret-file ./me.secret
.venv/bin/python server/server.py
```

This serves plain HTTP on `127.0.0.1:8686` with no Caddy in front; keep it on loopback. Use the journal mode your file system allows (`MANIFOLD_STORE_JOURNAL_MODE=delete` if the data folder is on a shared or network mount).
