---
title: "Use REST for the order service"
status: accepted
date: 2026-01-14
components: [acme-api, acme-web, acme-cli]
supersedes: ""
---

# Use REST for the order service

## Status

Accepted.

## Context

Three clients (web, command line, and later a mobile app) need the same order data. The team
is small and already runs HTTP services.

## Decision

Acme API exposes a JSON REST API under `/v1`. Clients use it directly; there is no gateway.

## Consequences

Easy: any HTTP client works, the API documents itself, caching is straightforward.
Harder: clients that need several resources make several calls; breaking changes need a
version path and a handoff to every client.

## Alternatives considered

- GraphQL: flexible for clients, but a new runtime and a new set of skills for a small team.
- gRPC: efficient, but the browser client would need a proxy.
