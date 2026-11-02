---
id: INT-18
title: Claude Desktop and claude.ai can use a Manifold server
author: Michael Hay
created: 2026-11-01
status: draft
affects: [server, docker, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Claude Desktop and claude.ai can use a Manifold server

## Problem
Claude Code and VS Code (GitHub Copilot) connect to a Manifold server from the user's own machine, so a server on a private network works for them. Claude Desktop and claude.ai custom connectors connect from Anthropic's cloud instead. A server on a private network or on localhost is not reachable that way, so people who work mainly in those clients cannot use the wiki, handoffs or onboarding. The security baseline (INT-1) deliberately leaves this out for the first company.

## Proposed outcome
A person using Claude Desktop or claude.ai can connect to a Manifold server and act as their own principal, with a path that is documented, tested, and does not weaken the protections in INT-1. The guide says which setup to choose for a private network and which for a reachable server.

## Affected users and systems
- **People who use Claude Desktop or claude.ai** with a team's Manifold server.
- **Administrators,** who choose how the server is exposed.
- **The server, the compose setup and the operations guide.**

## Constraints
- **Nothing is promised that has not been tested** in the clients themselves.
- **No weaker protection.** Every option keeps individual credentials, TLS and the host and origin checks from INT-1. An option that needs a shared credential for everyone on a plan is not acceptable for people.
- **Private by default.** Exposing the server to the internet is a deliberate, documented act with a visible warning.
- **Known options to evaluate:** a small local bridge on the user's machine that speaks to the server; or a reachable endpoint that allows only Anthropic's published address ranges; or the clients' own OAuth connection once INT-19 exists.
- **Open license, no vendor lock.** Anything added must be Apache-2.0 compatible.

## Scenario seeds

### S1 — A private-network team uses Claude Desktop
**Who:** A person on a team whose Manifold server is on a private network.
**Wants:** To read the wiki and file a handoff from Claude Desktop.
**So that:** They are not forced to switch clients.
**We will know when:** Following the guide on a clean machine, the person sees the server's tools in Claude Desktop and a handoff they create appears under their own identity.
**Must never:** Require the server to be open to the whole internet, or share one credential among several people.

### S2 — A reachable server is not an open server
**Who:** An administrator who exposes a server for claude.ai.
**Wants:** Only the intended clients and people to get in.
**So that:** Exposure does not publish the wiki.
**We will know when:** A request from outside the allowed ranges or without a valid credential is refused and logged, and the guide says how to check this.
**Must never:** Start listening publicly without protection or without a visible warning.

## Out of scope
- Claude Code and VS Code, which already work (INT-1).
- Acting as an MCP authorization server (INT-19), except as one option to evaluate.
- Building a graphical client.

## Open questions
- Is a local bridge acceptable to the first company, or is a reachable endpoint required? (the product owner)
- Do the Team and Enterprise plans of the clients allow a credential per person, or only a shared one? (answered by a spike)
- Which of the clients' connection behaviors has been tested rather than read from documentation? (answered by a spike)
