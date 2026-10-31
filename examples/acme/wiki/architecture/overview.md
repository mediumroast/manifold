---
title: "Acme system overview"
last_updated: 2026-01-14
---

# Acme system overview

## System overview

```
  customer browser        support staff terminal
        |                          |
   [acme-web]                  [acme-cli]
        \                        /
         \                      /
          +------[acme-api]----+
                     |
                 PostgreSQL
```

## Component responsibilities

### [acme-api](../components/acme-api.md)
Owns customers, products and orders. The only component that reads or writes the database.

### [acme-web](../components/acme-web.md)
The storefront. Renders pages and calls Acme API; it keeps no data of its own.

### [acme-cli](../components/acme-cli.md)
A thin client over Acme API for support staff.

## Communication patterns

Everything goes through the REST API of Acme API. Clients do not talk to each other.

## Shared infrastructure

One PostgreSQL instance, owned by Acme API. A load balancer in front of Acme API and Acme Web.

## Data flows

Checkout: Acme Web posts an order to Acme API, which checks stock, takes payment through the
payment provider, sets the status and returns the order. Order status values are defined in
the shared [order status contract](../../raw/shared/2026-01-27-order-status-contract.md).

## Open architecture questions

- Should order events be published for other systems, or is polling enough?
