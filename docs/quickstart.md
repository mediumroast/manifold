<!-- SPDX-License-Identifier: Apache-2.0 -->
# Quickstart: a running Manifold server in about ten steps

You will run the server on your own machine against a small made-up wiki, open it in a browser, connect an AI tool to it, and create a handoff. Then you will start an empty wiki of your own.

**What you need:** git; Docker with Compose (or Python 3.11 or newer, see [Without Docker](#without-docker)); and Python 3 on the command line (the setup script uses it once to make a token).

> **Before you start:** the server has one shared token and no other protection. It listens on your machine's loopback address only. Keep it that way while you try it. See [Known limits](../server/README.md#known-limits).

## 1. Get the code

```bash
git clone https://github.com/mediumroast/manifold.git
cd manifold
```

## 2. Make a wiki to try it on

A wiki ("instance") is a git repository of Markdown pages. Copy the made-up one and make the copy a repository of its own. It must be a copy: the server records every change as a git commit and refuses to do so inside another repository.

```bash
cp -R examples/acme ~/acme-wiki
cd ~/acme-wiki
git init -q && git add -A && git commit -q -m "Start from the Acme example"
cd -
```

(`examples/acme` describes three invented components of an online store, with pages, a log and three handoffs. `examples/starter` is the empty version you will use in step 10.)

## 3. Create the settings file

```bash
./svc_ctl.sh dev init-env
```

This creates `docker/.env.dev` and puts a freshly generated token in it. The file is private to you (mode 600); do not commit it.

## 4. Point it at your wiki

Open `docker/.env.dev` and set `WIKI_ROOT` to the **absolute** path of the copy you made. A leading `~` is not expanded, so write the full path; running `pwd` inside the folder prints it. The line below is only an example:

```
WIKI_ROOT=/home/you/acme-wiki
```

## 5. Start it

```bash
./svc_ctl.sh dev start
```

The first start builds the image, which takes a few minutes. The script first checks that `WIKI_ROOT` is a folder with a `manifold.yaml` in it, and says so if it is not.

## 6. Check that it is healthy

Read the token from your settings file and ask the server:

```bash
TOKEN=$(sed -n 's/^MANIFOLD_TOKEN=//p' docker/.env.dev)
curl -s http://127.0.0.1:8686/health
curl -s -H "Authorization: Bearer $TOKEN" http://127.0.0.1:8686/health
```

The first call, without the token, says only `{"status": "healthy"}`. The second lists the checks: the mount, the two required pages, `manifold.yaml` (`ok (3 components)`), write access and the git repository. If it says `unhealthy`, the message says which check failed; see [Operations](operations.md#when-something-is-wrong).

## 7. Open the wiki in a browser

Go to <http://127.0.0.1:8686/docs/>. The browser asks for a user name and a password: use any user name and the token as the password. You should see the Acme wiki with its components, an architecture page, a decision and three handoffs.

## 8. Connect an AI tool

The server speaks MCP at `http://127.0.0.1:8686/mcp` and wants the token as a bearer header.

**Claude Code:**

```bash
claude mcp add --transport http manifold http://127.0.0.1:8686/mcp \
  --header "Authorization: Bearer $TOKEN"
```

**VS Code (GitHub Copilot):** copy [`examples/clients/vscode-mcp.json`](../examples/clients/vscode-mcp.json) to `.vscode/mcp.json`. VS Code asks for the token once and keeps it out of the file.

For other clients, [`examples/clients/claude-code-mcp.json`](../examples/clients/claude-code-mcp.json) shows the shape: a URL and an `Authorization` header.

Start a session and ask the tool to call `wiki_ping_tool`. It should answer `connected`, with the server name `manifold` and 15 tools.

## 9. Try a handoff

A handoff passes a piece of work from one component's agent to another's. Ask your tool, in plain words, to do this:

> Using the manifold server, list the open handoffs for `acme-api`. Then create a handoff from `acme-cli` to `acme-web` of type `feature`, priority `low`, titled "Show the cli version", with a one-line summary and a one-line description of the work. Then read it back.

Behind the scenes the tool calls `wiki_handoff_tool` with `action: "list"` and then `action: "create"`, and `wiki_read_tool`. Refresh the browser: the new handoff is in the sidebar under *acme-cli → acme-web*, marked open. In `~/acme-wiki`, `git log` shows the server's commits (the page, the sidebar, the log entry), authored as `manifold`.

You can also see the other lifecycle steps on the existing handoffs: one is open, one in progress and one completed. The full lifecycle is in [Concepts](concepts.md#handoffs).

## 10. Start your own wiki

Stop the example and start an empty one.

```bash
./svc_ctl.sh dev stop
cp -R examples/starter ~/my-wiki
cd ~/my-wiki
git init -q && git add -A && git commit -q -m "Start my wiki"
cd -
```

Edit `name` in `~/my-wiki/manifold.yaml`, set `WIKI_ROOT` in `docker/.env.dev` to the absolute path of `~/my-wiki`, and start again:

```bash
./svc_ctl.sh dev start
```

Ask your tool to register your first component (`wiki_register_component_tool` needs a name, a one-sentence description, the repository address and an owner). The component is added to `manifold.yaml`, the sidebar and the home page, and a page is created for it. Register a second, and you can create a handoff between them. The tool `wiki_onboarding_tool` walks an agent through registering a component that already has documents.

## Next

- **Put the agents in your repositories.** The server does not hold the agents; the bundle does. Ask your tool for `wiki_bundle_info_tool`, or read [the bundle's README](../bundles/base/README.md).
- **Install the handoff commands** in a component repository with `wiki_export_component_helpers_tool`. They add `/handoff-create`, `/handoff-pickup`, `/handoff-close` and a few more to Claude Code and Copilot.
- **Back it up.** The server never pushes; see [Operations](operations.md#back-it-up).
- Stop everything with `./svc_ctl.sh dev stop`.

## Without Docker

```bash
python3 -m venv .venv
.venv/bin/pip install -r server/requirements.txt -c server/requirements.lock
export CONTAINER_WIKI_ROOT=$HOME/acme-wiki
export MANIFOLD_TOKEN="$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')"
echo "$MANIFOLD_TOKEN"            # keep it: clients and the browser need it
.venv/bin/python server/server.py
```

Then continue from step 6 with that token (use `TOKEN="$MANIFOLD_TOKEN"` in place of reading the settings file).
