---
title: "Acme Api"
component: "acme-api"
status: active
last_updated: 2026-01-27
owner: "Platform team"
summary: "REST order service: customers, products and orders for the Acme storefront."
---

# Acme Api

## Overview

_Sourced from `raw/acme-api/2026-01-12-acme-api-readme.md`. Synthesise and rewrite this section as needed._

# Acme API

Acme API is the order service behind the Acme storefront. It owns customers, products and
orders, and exposes them as a JSON REST API.

- Language: Python 3.12 with FastAPI
- Storage: PostgreSQL
- Runs as one container behind a load balancer

Start it locally with `make run`; the interactive API documentation is served at `/docs`.


**Repository:** https://example.test/acme/acme-api

## Architecture

_Sourced from `raw/acme-api/2026-01-12-acme-api-architecture.md`. Synthesise and rewrite this section as needed._

# Acme API architecture

The service has three layers.

1. **Routers** validate requests and shape responses. One router per resource.
2. **Services** hold the business rules: pricing, stock checks, order state changes.
3. **Repositories** are the only code that talks to PostgreSQL.

Order state changes go through a single function so every change is checked against the
allowed transitions and written to an audit table.

Background work (confirmation emails, stock reconciliation) runs in a separate worker process
that reads a Postgres-backed job queue.


## API contract

_Sourced from `raw/acme-api/2026-01-12-acme-api-api.md`. Synthesise and rewrite this section as needed._

# Acme API contract

Base path `/v1`. All bodies are JSON. Errors use `{"error": {"code": "...", "message": "..."}}`.

| Method | Path | Purpose |
|---|---|---|
| GET | /v1/products | List products |
| GET | /v1/products/{id} | One product |
| POST | /v1/orders | Create an order |
| GET | /v1/orders/{id} | One order |
| POST | /v1/orders/{id}/cancel | Cancel an order that has not shipped |

An order has `id`, `customer_id`, `lines`, `total_cents`, `currency` and `status`.
Status values are listed in the shared order-status contract.


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

- [`raw/acme-api/2026-01-12-acme-api-readme.md`](../../raw/acme-api/2026-01-12-acme-api-readme.md) — readme document
- [`raw/acme-api/2026-01-12-acme-api-architecture.md`](../../raw/acme-api/2026-01-12-acme-api-architecture.md) — architecture document
- [`raw/acme-api/2026-01-12-acme-api-api.md`](../../raw/acme-api/2026-01-12-acme-api-api.md) — api document
