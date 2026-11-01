---
id: INT-1
title: Security baseline for the Manifold server
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docker, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Security baseline for the Manifold server

## Problem
The server has one shared token. Anyone who holds it can read and write everything in the wiki, as anyone. Nothing records who did what, a leaked token can only be replaced for everybody at once, and the token travels in clear text on any network without TLS. Nothing stops a person or agent from filing a handoff on behalf of a component it has nothing to do with.

That is acceptable for one person on a laptop. It is not acceptable once a small team shares one server on a private network, which is the first real use planned. The wiki is read into other agents' context, so a forged or altered handoff is a way to steer another team's agent. The risk is bigger than outsiders getting in: it is that nobody can prove who wrote what.

## Proposed outcome
A small team can run one server on a shared host and trust three things about it:

1. **Everyone has their own identity.** Each person, agent or service signs in with its own credential. One can be revoked or rotated without touching anyone else.
2. **Writes are limited to what the caller is responsible for.** A caller can act only for the components it has been given. Handoffs follow the same rule as the lifecycle: only the source side creates, confirms or rejects; only the target side claims or requests review.
3. **Every change says who made it.** The history and the log name the person or agent behind each change, and that name comes from the credential, never from what the caller claims.

In addition, the server is hard to misuse by accident: it refuses to listen beyond the local machine without protection, refuses requests addressed to the wrong host or from an unexpected web origin, slows down repeated failed sign-ins, and can be put behind TLS by following one documented path. The design leaves room to add a company identity provider later without rewriting the tools.

## Affected users and systems
- **Administrators** of a shared instance: create, rotate and revoke credentials, set which components each may act for, turn on TLS.
- **People and agents** that use the wiki through MCP clients, the wiki browser, or `POST /ingest`.
- **The server** (`server/`): authentication, authorization, audit, request checks, and the settings that drive them.
- **The container setup and documentation** (`docker/`, `docs/`, `server/README.md`): secure defaults, a documented TLS setup, the operations guide.
- **Instances already in use** with the shared token: they need a way forward that does not lock people out.

## Constraints
- **Safe by default.** A new install is protected without extra steps; turning protection off is a deliberate, loud act and is refused on any address other than the local machine.
- **Secrets stay out of the wiki.** Credentials are never stored in the instance repository, never written to the log or the git history, and never shown in full after creation. At rest the server keeps only hashes.
- **Client compatibility.** Claude Code and VS Code (GitHub Copilot) keep working with a header they already support. A browser keeps working with the standard sign-in prompt.
- **No new service needed to start.** The first version needs no external identity provider, database or network service beyond what the server uses today.
- **Standards, not inventions.** Follow the current MCP authorization guidance and common web practice for token handling, host and origin checks, and TLS.
- **Offline-clean.** The wiki browser and the server keep making no outside requests.
- **Open license, no vendor lock.** Anything added must be Apache-2.0 compatible.
- **Reads.** Per-component read limits are not needed in the first version: any signed-in caller may read. (To be confirmed; see open questions.)
- **Priority.** This comes before the shared host is used by more than one person, and before the sign-in pieces of the new UI.

## Scenario seeds

### S1 — Each person has their own credential
**Who:** An administrator of a shared instance.
**Wants:** To give each team member and each agent its own credential, and to revoke one without affecting the rest.
**So that:** A lost laptop or a departed colleague is dealt with in minutes and nobody else is interrupted.
**We will know when:** After revoking one credential, that holder's next request is refused and every other holder's requests still work, with no server restart.
**Must never:** Show a credential in full after it is first issued, store it in the instance repository, or let a revoked credential keep working.

### S2 — An agent can only act for its own component
**Who:** An agent that is responsible for one component.
**Wants:** To create handoffs from, and claim handoffs for, its own component.
**So that:** The wiki's record of who asked whom for what can be trusted.
**We will know when:** The same agent's attempt to create a handoff from a different component, or to confirm a handoff it did not create, is refused with a clear reason, and nothing is written.
**Must never:** Let a caller act for a component it has not been given, or widen its own access.

### S3 — Every change names who made it
**Who:** A reviewer reading the history after something looks wrong.
**Wants:** To see which credential made each change.
**So that:** They can tell who changed a handoff or page without guessing.
**We will know when:** Each change in the git history and the log carries the identity of the credential used, and a caller who claims to be someone else in the request still shows up under its own identity.
**Must never:** Record a name supplied by the caller as the author, or leave a change anonymous.

### S4 — A guessing attack is slowed down and noticed
**Who:** An administrator watching a shared server.
**Wants:** Repeated failed sign-ins from one place to be slowed down and recorded.
**So that:** Guessing a credential is not practical and the attempt leaves a trace.
**We will know when:** After a run of wrong credentials, further attempts are refused for a while, the refusals appear in the log, and a correct credential still works from elsewhere.
**Must never:** Reveal in an error message whether a user or a credential exists, or write the guessed credential to the log.

### S5 — A request for the wrong host or from the wrong web page is refused
**Who:** A person with the wiki open in a browser next to other web pages.
**Wants:** Their local server to be unreachable from other pages and hostile names.
**So that:** A web page they happen to open cannot read or change their wiki through their own browser.
**We will know when:** A request with an unexpected host name or an unexpected origin is refused, while the documented address and origin work.
**Must never:** Let a page from another origin make a state-changing request to the server.

### S6 — The server will not open itself to the network unprotected
**Who:** Someone starting the server on a shared host.
**Wants:** A clear refusal if protection is missing or weak.
**So that:** A mistake in a settings file does not publish the wiki.
**We will know when:** Starting with no credentials, or with a short or default credential, on any address other than the local machine fails with a message that says what to fix, and the same start on the local machine works with a visible warning.
**Must never:** Start listening on a shared address with protection off because a setting was left empty.

### S7 — TLS is a documented step, not a research project
**Who:** An administrator putting the server on a private network.
**Wants:** One documented way to serve it over TLS, with the client steps for Claude Code, VS Code and a browser.
**So that:** Credentials do not cross the network in clear text.
**We will know when:** Following the guide on a clean machine gives an HTTPS address that each listed client connects to, and the guide says what to do about certificates each client does not trust.
**Must never:** Tell people to turn off certificate checks in a client.

### S8 — Moving an existing instance off the shared token
**Who:** An administrator of an instance that uses the single shared token today.
**Wants:** To move to individual credentials without the team losing access in the middle.
**So that:** Adopting the new protection does not cost an outage.
**We will know when:** The guide takes an instance from one shared token to individual credentials in steps, the old token keeps working until the administrator turns it off, and the server says when it is still in use.
**Must never:** Silently keep accepting the old token after it has been turned off.

## Out of scope
- Signing in through a company identity provider (single sign-on). The design must leave room for it; building it is a later intent.
- Per-component read permissions, finer than "any signed-in caller may read".
- A user-management interface in the new UI (that comes with the UI).
- Encrypting the wiki content at rest.
- Protecting a host that is already compromised, or the people who hold admin access.
- Supply-chain work beyond pinning dependencies by hash in the lock file.

## Open questions
- Who issues and revokes credentials in the first version: a command-line tool run on the host, or a tool call by an administrator over MCP? (the product owner)
- Is a person's access and an agent's access the same kind of credential, or do agents get a narrower kind? (the product owner)
- Should per-component read limits be in the first version after all, given the wiki is read into agent context? (the product owner, with the company that will use it)
- Is TLS in front of the server (a documented proxy) enough for the first version, or must the server also be able to terminate TLS itself? (the product owner)
- What is the acceptable lockout behavior for the shared host: per credential, per address, or both? (the product owner)
- How long is the old shared token allowed to coexist with individual credentials during a move? (the product owner)
