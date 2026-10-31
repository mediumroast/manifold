<!-- SPDX-License-Identifier: Apache-2.0 -->
# `manifold.yaml` reference

`manifold.yaml` is at the root of an instance repository. It names the instance, sets a few browser and client details, and is the **registry of components**. It holds no secrets. The server reads it on every request, so a change takes effect without a restart.

```yaml
# Instance settings for this wiki. No secrets belong in this file.
version: 1
name: Acme Engineering Wiki
server_name: manifold

brand:
  accent: "#2c3e50"
  accent_dark: "#42b983"

components:
  - slug: acme-api
    owner: "Platform team"
    repo: "https://example.test/acme/acme-api"
    description: "REST order service: customers, products and orders."
  - slug: acme-web
    owner: "Web team"
    repo: "https://example.test/acme/acme-web"
    description: "Customer-facing storefront."
```

## Keys

| Key | Required | Default | What it does |
|---|---|---|---|
| `version` | yes | | Must be `1`. |
| `name` | no | `Manifold` | The wiki's name: the title and heading of the wiki browser. |
| `server_name` | no | `manifold` | The name of the MCP server. See below. |
| `brand.accent` | no | `#2c3e50` | Accent color of the wiki browser in the light theme, as `#rrggbb`. |
| `brand.accent_dark` | no | `#42b983` | Accent color in the dark theme, as `#rrggbb`. |
| `components` | no | none | The registered components. A list of the entries below. |

Other keys are ignored, so a newer file still loads in an older server.

### A component entry

| Key | Required | What it is |
|---|---|---|
| `slug` | yes | The component's short name. Lowercase ASCII letters and digits, with single dots, hyphens or underscores between them, at most 64 characters (`acme-api`, `billing`, `acme.io`). It becomes a folder name, so there are no slashes, no leading or trailing separators and no spaces. A slug never changes once handoffs refer to it. |
| `owner` | no | A person or team. |
| `repo` | no | The component's repository address. |
| `description` | no | One sentence. |

Each slug may appear once.

## What the registry controls

- **Handoffs.** A handoff can be created only between registered slugs; anything else is refused with the list of registered components.
- **The schema page.** The list under "Valid component slugs" in `wiki/CLAUDE.md` is generated from the registry whenever a component is registered. Do not edit that list by hand.
- **Registration.** `wiki_register_component_tool` adds an entry for you. It edits the file as text, so your comments and the order of keys are kept; if the file is written in a form it cannot edit safely (for example the whole list on one line with items in it), it leaves the file alone, says so, and asks you to add the entry by hand.

You can also edit the file by hand: add an entry under `components` and the component is usable at once. A hand-added component has no wiki page until you register it with `wiki_register_component_tool` (with `reconcile: true` if a page already exists).

## `server_name`

It is the name the server reports to MCP clients and in `wiki_ping_tool`, and it is written into the `tools:` line of the Copilot prompts that `wiki_export_component_helpers_tool` returns (`tools: ['<server_name>/*']`). Set it to the **name you gave the server in your client's configuration**. The examples use `manifold` in both places. If you register the server under a different name in a client, set `server_name` to match so the exported prompts can find its tools.

## Errors

If the file is missing or invalid, the server keeps running but refuses the operations that need it, with a message that says what is wrong ("`version` must be 1", "`components[2]` has an invalid slug", "component `acme-api` is listed twice", "`brand.accent` must be a color like #2c3e50"). `GET /health` reports `manifold.yaml` as `invalid` and returns HTTP 500 until it is fixed.
