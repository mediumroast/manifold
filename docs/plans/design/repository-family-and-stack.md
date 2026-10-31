<!-- SPDX-License-Identifier: Apache-2.0 -->
# Repository family and stack

**Status:** Proposed. This describes the shape of what comes after the base bundle. It is a plan, not a commitment, and has no dates.

## 1. Principle

**Tool repositories are public and generic; an organization's own data lives in its own repository, created by the tools from a template.** Tools never contain the data they manage.

## 2. The family

| Repository | Role | Required |
|---|---|---|
| `manifold` (this one) | The tools: agent bundle, server, interface, installer and command line | Yes |
| An **instance repository** | One per deployment: the pages, intents and handoffs the server is backed by, its configuration and optional brand assets. Created from a template by `manifold init` | Yes, for the server |
| A **quality repository** | Behavior scenarios, their automation and human test notes, for one organization or product group | Optional |
| A **scenario engine** | A generic kit that turns scenarios into automated tests, with local or hosted models | Optional; only with a quality repository |
| Component repositories | The code being coordinated; they receive the bundle | n/a |

Not proposed yet, to avoid multiplying repositories early: separate SDK repositories (clients speak MCP, which is already the SDK surface) and a separate automations repository. Workflows start inside the templates and are split out only when two repositories need the same one.

## 3. The instance repository

Holds a configuration file (components, storage, change policy, authentication), the pages (components, handoffs, decisions, guides, intents), immutable raw source material, optional theme overrides and a deployment folder that runs the published image against this repository. Secrets never live in it. The server is single-tenant: one instance repository per server.

## 4. The technology choice

**Python core and a Deno/Fresh/Preact frontend.** The reasons, from a spike that ran the options locally and read-only:

- The server speaks the Model Context Protocol over the web-standard transport, and the tool contract must not change under users.
- The interface needs more than static documentation tooling gives, including the intent editor.
- A single toolchain is attractive, but a rewrite must not be forced while the project is public.

The alternative, a TypeScript backend on Deno, is kept as a parked option. To keep a later move a port and not a rewrite, the Python core keeps a few seams: a storage interface with a local git and a GitHub API implementation, an authentication interface, tools defined as plain functions behind the MCP layer, and a contract test suite that any backend must pass. The decision is revisited only at a checkpoint where the seams hold and a concrete need exists.

## 5. Questions that stay open

- Whether the deployment folder belongs inside the instance repository.
- When the scenario engine is genericized and published.
- How a quality repository's credentials are separated from the product's in practice.
