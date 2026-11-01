---
id: INT-19
title: Manifold as an MCP authorization server
author: Michael Hay
created: 2026-11-01
status: draft
affects: [server, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Manifold as an MCP authorization server

## Problem
Clients get a Manifold credential today by running a command and pasting a token into a header. That works for Claude Code and VS Code but is manual, expires on a schedule the person has to track, and does not fit clients that expect to sign in through their own connection screen. The current MCP authorization guidance expects a server to advertise how to sign in, accept dynamic client registration, and issue tokens meant for it alone. Manifold does none of that, and a GitHub token is issued to the GitHub App, not to Manifold, so GitHub cannot play that role directly.

## Proposed outcome
A Manifold server can act as an authorization server for MCP clients. A client finds out how to sign in, registers itself, sends the person to sign in (with GitHub, when INT-7 is configured), and receives a short-lived credential made for this server, which it can refresh. The static header remains supported. Nothing changes for the principals, roles and checks of INT-1.

## Affected users and systems
- **People and agents** using MCP clients that support a sign-in flow.
- **Administrators,** who turn the feature on or off.
- **The server and the operations guide.**
- **INT-18,** which may use this for Claude Desktop and claude.ai.

## Constraints
- **Standards, not inventions.** Follow the MCP authorization guidance in force when the plan is written, including protected-resource metadata, authorization-server metadata, PKCE, and tokens bound to this server. The guidance has changed between revisions and rests on a draft standard, so the plan re-checks it first.
- **Optional.** With the feature off, the server behaves as in INT-1. Local mode keeps working without GitHub.
- **Tested in the real clients** (Claude Code, VS Code, and Claude Desktop where reachable) before anything is promised about them.
- **No GitHub token kept.** The person's GitHub token proves identity once and is discarded (INT-7).
- **Credentials are Manifold's own,** short-lived, revocable at once, and shown to the holder only as the client needs them.
- **Redirect addresses** are limited to the local machine or HTTPS.
- **Open license, no vendor lock.** Anything added must be Apache-2.0 compatible.

## Scenario seeds

### S1 — Connect without pasting a token
**Who:** A person with access to the instance repository.
**Wants:** To add the Manifold server to a client and sign in once.
**So that:** They do not copy a token by hand.
**We will know when:** After approving the sign-in, the client lists the server's tools, and the history shows the person's GitHub account as the author of their changes.
**Must never:** Hand the client more than the reader role at sign-in, or keep the person's GitHub token.

### S2 — A token for another service is refused
**Who:** A client holding a token issued for a different service.
**Wants:** To use it against Manifold.
**So that:** A token stolen elsewhere is useless here.
**We will know when:** The request is refused with a clear reason and nothing is read or written.
**Must never:** Accept a token that was not issued for this server.

### S3 — Turning it off leaves the header path working
**Who:** An administrator.
**Wants:** To turn the sign-in flow off.
**So that:** A smaller attack surface is one setting away.
**We will know when:** With the flow off, the sign-in endpoints are gone and tokens issued by the host command still work.
**Must never:** Leave the endpoints answering when the flow is off.

## Out of scope
- GitHub sign-in itself (INT-7) and the roles and checks (INT-1).
- Company identity providers other than GitHub.
- An admin screen in the new UI.

## Open questions
- Which of the clients' sign-in behaviors (registration, redirect addresses) work against such a server? (answered by a spike)
- Does this ship before or after INT-18, given that Claude Desktop may need it? (the product owner) Answer: We are building in the open and will ship when the product owner believes there is enough function to warrant it. That may be after 18 or before depending on the build status.
- Which revision of the MCP authorization guidance applies when the plan is written? (answered at planning)
