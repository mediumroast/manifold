---
title: "Order history endpoint"
type: feature
source_component: acme-web
target_component: acme-api
status: open
priority: medium
created: 2026-01-20
updated: 2026-01-20
blocking: []
blocked_by: []
---

## Summary

Acme Web needs a customer's past orders to show an order history page.

## What needs to happen

1. Add GET /v1/customers/{id}/orders returning the customer's orders, newest first.
2. Support limit and cursor parameters.
3. Update the API contract document.

## Technical details

Response: {"orders": [...], "next_cursor": "..."}. Default limit 20, maximum 100. Orders use the same shape as GET /v1/orders/{id}.

## Implementation notes

_(Target fills this in while working.)_

## Blockers

_(None.)_

## Related handoffs

_(None.)_
