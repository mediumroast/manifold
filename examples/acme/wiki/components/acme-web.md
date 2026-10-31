---
title: "Acme Web"
component: "acme-web"
status: active
last_updated: 2026-01-27
owner: "Web team"
summary: "Customer-facing storefront: browse, check out and follow an order."
---

# Acme Web

## Overview

_Sourced from `raw/acme-web/2026-01-12-acme-web-readme.md`. Synthesise and rewrite this section as needed._

# Acme Web

Acme Web is the customer-facing storefront: browse products, check out, and follow an order.

- Server-rendered pages with a small amount of client-side script
- Talks to Acme API only; it has no database of its own
- Deployed as static assets plus one Node process


**Repository:** https://example.test/acme/acme-web

## Architecture

_To be completed. Describe the internal design: key modules, patterns, and tech stack. Update this section from `raw/acme-web/` source documents._

## API contract

_To be completed. List endpoints, schemas, and data models. Mark breaking changes clearly. Update from `raw/acme-web/` source documents._

## Integration points

_To be completed. Describe how this component communicates with other components. Link each component name to its wiki page once known._

## Implementation status

| Area | Status | Notes |
|---|---|---|
| Initial registration | ✅ Done | 2026-01-14 |
| Raw source docs | ✅ Embedded | See Sources section |
| Architecture documented | ⬜ Review embedded content | |
| API contract documented | ⬜ Review embedded content | |

## Changelog

- **2026-01-27** - Order status values renamed to `placed` and `confirmed` (see the completed handoff).
- **2026-01-14** — Component registered.

## Known issues

_None recorded at registration._

## Deployment

_To be completed. Document how the component runs, required environment
variables, dependencies, and health checks._

## Sources

- [`raw/acme-web/2026-01-12-acme-web-readme.md`](../../raw/acme-web/2026-01-12-acme-web-readme.md) — readme document
