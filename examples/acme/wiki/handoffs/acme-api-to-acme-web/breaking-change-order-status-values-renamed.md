---
title: "Order status values renamed"
type: breaking-change
source_component: acme-api
target_component: acme-web
status: completed
priority: high
created: 2026-01-20
updated: 2026-01-27
blocking: []
blocked_by: []
---

## Summary

Acme API now reports `placed` and `confirmed` instead of `pending` and `paid`.

## What needs to happen

1. Update every place Acme Web compares or displays an order status.
2. Show the new labels on the order page.
3. Confirm when deployed.

## Technical details

Old to new: pending -> placed, paid -> confirmed. Other values are unchanged. The old values are no longer returned.

## Implementation notes

Updated all status comparisons and labels in the storefront; deployed to production.

## Blockers

_(None.)_

## Related handoffs

_(None.)_
