---
title: "Cancel returns 500 for an order that already shipped"
type: bug
source_component: acme-cli
target_component: acme-api
status: in-progress
priority: high
created: 2026-01-20
updated: 2026-01-22
blocking: []
blocked_by: []
---

## Summary

POST /v1/orders/{id}/cancel answers 500 instead of a clear error when the order has shipped.

## What needs to happen

1. Return 409 with code `order_not_cancellable` when the status is shipped or delivered.
2. Add a test for each status.

## Technical details

Reproduce with an order in `shipped`: the state-change function raises an unhandled exception.

## Implementation notes

_(Target fills this in while working.)_

## Blockers

_(None.)_

## Related handoffs

_(None.)_
