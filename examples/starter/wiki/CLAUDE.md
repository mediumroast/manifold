# Wiki Schema

This file defines the structure, rules, and taxonomies for this wiki.
Read this file before performing any wiki operation.

> **New component?** Call `wiki_onboarding_tool()` first, then read this file.

---

## Component taxonomy

Valid component slugs:

The list above is generated from `manifold.yaml`. Edit the registry there (or register a
component with `wiki_register_component_tool`), not this list.

Use these slugs exactly in all frontmatter fields and handoff directory names.
Component slugs are immutable: changing one breaks every reference to it.

---

## wiki/components/{component}.md

**Purpose:** Current state of a component. Always reflects the latest known state.

**Required frontmatter:**
```yaml
---
title: "{Component display name}"
component: "{slug}"
status: active | deprecated | experimental
last_updated: YYYY-MM-DD
owner: "{name or team}"
summary: "{one sentence description}"
---
```

**Required sections:**
1. `## Overview` - What this component does and why it exists
2. `## Architecture` - Internal design: key modules, patterns, tech stack
3. `## API contract` - Endpoints, schemas, data models. Mark breaking changes clearly
4. `## Integration points` - How this component talks to other components
5. `## Implementation status` - What is done, in progress, planned. Use a status table
6. `## Changelog` - Reverse-chronological list of meaningful changes
7. `## Known issues` - Technical debt, limitations, open questions
8. `## Deployment` - How it runs, environment variables, dependencies, health checks
9. `## Sources` - The raw documents the page was written from, with relative links

**Maintenance rules:**
- When a handoff is completed, update the relevant component page.
- Set `last_updated` to today's date on every write.
- Every `## Changelog` entry carries a date and what changed.

---

## wiki/handoffs/{source}-to-{target}/{type}-{id}.md

**Purpose:** A unit of work passed from one component's agent to another. This is the
inter-component message queue.

**Naming convention:**
- `{type}` is one of `feature`, `bug`, `breaking-change`, `integration-spec`.
- `{id}` is a short kebab-case identifier, for example `order-history`.
- Full example: `wiki/handoffs/web-to-api/feature-order-history.md`

**Required frontmatter:**
```yaml
---
title: "{Human-readable description of the work}"
type: feature | bug | breaking-change | integration-spec
source_component: "{slug}"
target_component: "{slug}"
status: open | in-progress | needs-review | completed | blocked | wont-fix
priority: critical | high | medium | low
created: YYYY-MM-DD
updated: YYYY-MM-DD
blocking: []           # handoffs that depend on this one
blocked_by: []         # handoffs this one depends on
---
```

**Required sections:** Summary, Context, What needs to happen, Technical details,
Integration spec, Implementation notes (the target fills this in), Blockers, Related handoffs.

**Status transitions:**
```
open -> in-progress -> needs-review -> completed
open -> blocked -> in-progress -> completed
any -> wont-fix
```

Never delete a handoff; close it as `completed` or `wont-fix`. When the status changes,
update the `updated` field, append to `wiki/log.md`, and, on completion, update the target
component's page.

---

## wiki/architecture/overview.md

**Purpose:** How the components fit together: responsibilities, communication patterns,
shared infrastructure, key data flows, and open questions.

---

## wiki/decisions/{YYYY-MM-DD}-{slug}.md

**Purpose:** Architecture Decision Records. A permanent record of significant choices.

**Required frontmatter:**
```yaml
---
title: "{Decision title}"
status: proposed | accepted | superseded | deprecated
date: YYYY-MM-DD
components: []          # which components this affects
supersedes: ""          # slug of the decision this replaces, if any
---
```

**Required sections:** Status, Context, Decision, Consequences, Alternatives considered.

---

## wiki/log.md

**Purpose:** Append-only audit log of wiki operations. Never edit earlier entries.

```
## YYYY-MM-DD | {operation} | {title}

- Agent: {component slug or human}
- Summary: {one sentence}
- Pages affected: {list of wiki paths}
```

Operations: `init`, `ingest`, `register`, `create-handoff`, `update-handoff`,
`complete-handoff`, `update-component`, `create-adr`, `reconcile-component`, `lint`.

---

## wiki/index.md

**Purpose:** The wiki home page. Keep it current: components, open handoffs, recent
decisions, recent changes.

---

## Linking conventions

All links are paths relative to the file that contains them, so they work in any Markdown
renderer. Never use absolute URLs for links inside the repository.

- Component page to component page: `[billing](./billing.md)`
- Component page to a raw document: `[readme](../../raw/billing/2026-01-12-billing-readme.md)`
- Handoff to a component: `[billing](../../components/billing.md)`
- Every component name in an `## Integration points` table links to its page.

---

## Raw documents

Raw source documents live under `raw/` at the repository root.

- `raw/{component}/` holds documents that describe only that component (readme,
  architecture, API). Update them whenever the component changes.
- `raw/shared/` holds documents used by two or more components, such as a shared contract.
  A change to a shared document should produce a handoff to every component that depends on it.

Naming: `{YYYY-MM-DD}-{slug-description}.md`. The date prefix is how `wiki_freshness_tool`
tells whether a page is stale.

---

## General rules

1. Read this file before any wiki operation.
2. Check `wiki_inventory_tool` before creating a page, to avoid duplicates.
3. Write with the current etag so concurrent edits are not overwritten.
4. Log every operation.
5. Dates are ISO 8601.
