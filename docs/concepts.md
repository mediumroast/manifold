<!-- SPDX-License-Identifier: Apache-2.0 -->
# Concepts

## The problem the server solves

A group of repositories (a web front end, an API, a command-line tool) each has its own AI coding agent, and each agent only sees its own repository. When the front end needs a new API field, someone has to carry that request across. The Manifold server is the shared place where that happens: components are described once, work is passed between them as **handoffs**, and every change is recorded.

## An instance

An **instance** is one git repository of Markdown pages that the server is pointed at. One server serves exactly one instance. The instance holds:

| Path | What |
|---|---|
| `manifold.yaml` | The instance's settings and its component registry. See [the reference](manifold-yaml.md). |
| `wiki/` | The pages people and agents read and write: components, handoffs, architecture, decisions, the log, the home page, the sidebar, and the schema page `wiki/CLAUDE.md` that every agent reads first. |
| `raw/` | Source documents the pages were written from, in `raw/<component>/` for one component's documents and `raw/shared/` for documents used by two or more. File names start with a date, which is how the freshness check works. |

An instance is created by copying [`examples/starter`](../examples/starter) (empty) or [`examples/acme`](../examples/acme) (a filled-in example) and making the copy a git repository of its own. The server only commits in a repository whose top level is the instance folder. The instance belongs to you: it can be private, and the Manifold project never sees it.

## Components

A **component** is one of the things the instance coordinates, usually one repository. It has:

- an entry in the registry (`manifold.yaml`): a short name called a *slug* (`acme-api`), an owner, a repository address and a one-sentence description;
- a page, `wiki/components/<slug>.md`, with an overview, architecture, API contract, integration points, implementation status, changelog, known issues and deployment notes.

A handoff can only be created between registered components. Registering is one tool call (`wiki_register_component_tool`): it adds the registry entry, creates the page, adds the component to the sidebar and the home page, and updates the list of valid slugs in the schema page. The list in `wiki/CLAUDE.md` is generated from the registry; edit the registry, not the list.

## Handoffs

A **handoff** is a Markdown page, `wiki/handoffs/<source>-to-<target>/<type>-<id>.md`, that asks the target component to do something. It has a type (`feature`, `bug`, `breaking-change` or `integration-spec`), a priority, a status, and sections for the summary, context, what needs to happen, technical details, the integration spec, implementation notes, blockers and related handoffs.

The people (or agents) on each side move it along with `wiki_handoff_tool`:

```
   source: create ──► open
   target: claim  ──► in-progress
   target: request-review ──► needs-review
   source: confirm ──► completed          source: reject ──► in-progress (feedback added to Blockers)
   (source may also: close ──► completed)
```

- `create` and `claim` are the first two steps. `request-review` says the work is done and ready for the source to check.
- The source then either `confirm`s (completed) or `reject`s with feedback, which sends it back to in-progress.
- **Only the source closes a handoff.** The component that asked for the work is the one that says it is done: `close` is the source's shortcut to completed, for work it accepts without a review step. The target never closes; when there is no review to ask for, it still calls `request-review` and the source confirms. The server refuses any other combination, with the reason, and writes nothing.
- Nothing is ever deleted. A handoff that will not be done is closed as `wont-fix` by editing its status.

Each step updates the page's `updated` date, the sidebar (a symbol in front of the title shows the state: ○ open, ◉ in progress, ◑ needs review, ✓ completed) and the log. A handoff that finishes should also update the target component's page; the schema page says so.

The handoff commands are also available to people in their editors: `wiki_export_component_helpers_tool` returns slash commands for Claude Code (`.claude/commands/`) and Copilot (`.github/prompts/`): `/handoff-create`, `/handoff-pickup`, `/handoff-close`, `/handoff-update`, `/handoff-confirm`, `/handoff-reject` and `/manifold-update`, which refreshes them.

## People, agents and roles

Everyone who uses the server is a **principal** with a credential of their own: a person (`human`), an agent or a service. Four roles say what a principal may do, and they add up:

- **reader**: read everything (pages, inventory, the wiki browser). A reader writes nothing.
- **contributor**: a reader who can also write pages, append to the log, ingest documents and work handoffs, **only on the components it has a grant for**, and on `_shared` (the pages that belong to no component). A deny on a component beats a grant.
- **registrar**: registers, updates, archives and restores components. An agent that is a registrar is limited per day; changing a component's repository or owner is for a human registrar only.
- **admin**: administers the system from the host with the host command, and is refused every read and write over MCP and HTTP. An admin cannot read the wiki, and an agent can never be an admin.

Every change in git names the principal behind the credential, whatever the request claims. Taking a credential away is immediate. The details and the commands are in [Operations](operations.md#people-agents-and-credentials).

## Pages, etags and the log

Every page read returns an **etag**, a fingerprint of the content. A write of an existing page must give the etag it was based on. If the page has changed since, the write is refused with a `conflict` and the current etag, and the agent reads again and redoes its change. This is what lets several agents write to one wiki without overwriting each other.

Every operation is also appended to `wiki/log.md`, which is append-only, and committed to git. The git history of the instance is the full record of who changed what and when.

The sidebar (`wiki/_sidebar.md`) and the home page (`wiki/index.md`) are maintained by the server as components and handoffs come and go. They are navigation, not a source of truth: the registry and the pages are.

## Freshness

Raw documents carry a date in their file names. `wiki_freshness_tool` compares each component page's `last_updated` with the dates of its own raw documents and of the shared ones, and lists the pages that are older. It is how an instance notices that a source document changed and a page was not rewritten.

## The server and the bundles

Two pieces work together but are separate:

- **The bundle** ([`bundles/base`](../bundles/base/README.md)) holds the agents, rules and document templates, and installs into a repository with its own installer. It works with no server at all.
- **The server** holds the shared memory: components, handoffs, decisions, the log. It does not hold agents. Its `wiki_bundle_info_tool` says which bundles it carries and how to install one, and `wiki_agent_catalog_tool` publishes a component's installed agents to the wiki so people can find them.

A repository can use the bundle alone, the server alone, or both. With both, the agents the bundle installs are the ones that read the schema page, claim handoffs and write pages through the server.

## What the server does not do

- It does not call a language model. Agents and tools do that; the server stores and serves.
- It does not push to a git remote. You decide when and where the instance is pushed ([back it up](operations.md#export-import-and-backup)).
- It does not serve more than one instance, and it does not yet sign people in through GitHub or accept access from Claude Desktop or claude.ai (**a known limitation**: those clients need an authorization flow the server does not have; the work is planned as [INT-18](../intent/INT-18-claude-desktop-access.md); see also the [known limits](../server/README.md#known-limits)).
- It sends no telemetry and makes no outgoing request.
