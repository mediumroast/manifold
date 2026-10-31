---
title: "Acme Engineering Wiki"
last_updated: 2026-01-27
---

# Acme Engineering Wiki

Shared knowledge base for the Acme components. Read `wiki/CLAUDE.md` before performing any wiki operation.

---

## Components

| Component | Status | Wiki page | Summary |
|---|---|---|---|
| acme-api | active | [wiki/components/acme-api.md](components/acme-api.md) | REST order service: customers, products and orders for the Acme storefront. |
| acme-web | active | [wiki/components/acme-web.md](components/acme-web.md) | Customer-facing storefront: browse, check out and follow an order. |
| acme-cli | active | [wiki/components/acme-cli.md](components/acme-cli.md) | Command-line client for support staff. |

---

## Open handoffs

| Target | Priority | Status | Type | Handoff |
|---|---|---|---|---|
| acme-api | high | in-progress | bug | [Cancel returns 500 for an order that already shipped](handoffs/acme-cli-to-acme-api/bug-cancel-returns-500-for-an-order-that-alr.md) |
| acme-api | medium | open | feature | [Order history endpoint](handoffs/acme-web-to-acme-api/feature-order-history-endpoint.md) |

---

## Recent decisions

| Date | Decision |
|---|---|
| 2026-01-14 | [Use REST for the order service](decisions/2026-01-14-use-rest-for-orders.md) |

---

## Recent changes

| Date | Operation | Summary |
|---|---|---|
| 2026-01-27 | complete-handoff | Order status values renamed; acme-web updated |
| 2026-01-22 | update-handoff | Two handoffs claimed |
| 2026-01-20 | create-handoff | Three handoffs created |
| 2026-01-14 | register | Registered acme-api, acme-web and acme-cli |
| 2026-01-12 | init | Repository initialized |
