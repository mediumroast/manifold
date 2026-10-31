# Wiki operation log

Append-only. Never edit previous entries.

---

## 2026-01-12 | init | Repository initialized

- Agent: human
- Summary: Created the Acme example wiki.
- Pages affected: all

## 2026-01-14 | register | acme-api

- Agent: acme-api
- Summary: Registered acme-api from its raw docs
- Pages affected: wiki/components/acme-api.md

## 2026-01-14 | register | acme-web

- Agent: acme-web
- Summary: Registered acme-web from its raw docs
- Pages affected: wiki/components/acme-web.md

## 2026-01-14 | register | acme-cli

- Agent: acme-cli
- Summary: Registered acme-cli from its raw docs
- Pages affected: wiki/components/acme-cli.md

## 2026-01-20 | create-handoff | acme-api

- Agent: acme-api
- Summary: Created feature handoff from acme-web: Order history endpoint
- Pages affected: wiki/handoffs/ (new handoff from acme-api)

## 2026-01-20 | create-handoff | acme-api

- Agent: acme-api
- Summary: Created bug handoff from acme-cli: Cancel returns 500 for an order that already shipped
- Pages affected: wiki/handoffs/ (new handoff from acme-api)

## 2026-01-20 | create-handoff | acme-web

- Agent: acme-web
- Summary: Created breaking-change handoff from acme-api: Order status values renamed
- Pages affected: wiki/handoffs/ (new handoff from acme-web)

## 2026-01-22 | update-handoff | acme-api

- Agent: acme-api
- Summary: Claimed handoff: Cancel returns 500 for an order that already shipped — status: in-progress
- Pages affected: wiki/handoffs/ (acme-api)

## 2026-01-22 | update-handoff | acme-web

- Agent: acme-web
- Summary: Claimed handoff: Order status values renamed — status: in-progress
- Pages affected: wiki/handoffs/ (acme-web)

## 2026-01-27 | complete-handoff | acme-web

- Agent: acme-web
- Summary: Completed handoff: Order status values renamed
- Pages affected: wiki/handoffs/ (acme-web)

## 2026-01-27 | update-component | acme-api

- Agent: acme-api
- Summary: Recorded the order status rename on the acme-api and acme-web pages
- Pages affected: wiki/components/acme-api.md
