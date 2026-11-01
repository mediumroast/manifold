---
id: INT-1
title: Security baseline for the Manifold server
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docker, docs, ci]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Security baseline for the Manifold server

## Problem
The server has one shared token. Anyone who holds it can read and write everything in the wiki, as anyone. Nothing records who did what, a leaked token can only be replaced for everybody at once, and the token travels in clear text on any network without TLS. Nothing stops a person or agent from filing a handoff on behalf of a component it has nothing to do with.

That is acceptable for one person on a laptop. It is not acceptable once a small team shares one server on a private network, which is the first real use planned. The wiki is read into other agents' context, so a forged or altered handoff is a way to steer another team's agent. The risk is bigger than outsiders getting in: it is that nobody can prove who wrote what.

## Proposed outcome
A small team can run one server on a shared host and trust four things about it:

1. **Everyone has their own identity.** Each person, agent or service is a separate principal with its own credential, which the server keeps only as a hash. An administrator creates, rotates and revokes credentials with a command on the host. One can be revoked without touching anyone else, and without a restart.
2. **Writes are limited to what the caller is responsible for.** There are four additive roles: reader, contributor, registrar and admin. A contributor can write only for the components it has been granted (and for the shared pages, if granted). Handoffs follow the lifecycle: only the source side creates, confirms, rejects or closes; only the target side claims or requests review. A grant can be overridden by an explicit deny.
3. **Every change says who made it.** The history and the log name the person or agent behind each change, and that name comes from the credential, never from what the caller claims.
4. **Systems management is separate from data.** Administrators manage principals, roles, settings and TLS from the host; the admin role gives no access to wiki data through the server. The registrar role manages component registrations (create, change, archive, restore) and nothing else.

In addition, the server is hard to misuse by accident: it refuses to listen beyond the local machine without protection, refuses requests addressed to the wrong host or from an unexpected web origin, slows down repeated failed sign-ins, and can serve over TLS with a switch to turn it on or off. This works with no GitHub and no outside service, and that is a permanent, supported mode. A later intent (INT-7) adds GitHub sign-in on top of the same principals, roles and checks, with no change to the tools.

## Affected users and systems
- **Administrators** of a shared instance, working on the host: create, rotate and revoke credentials, set roles, grants and denies, turn TLS on or off, read the authentication audit.
- **Registrars** (people or agents), who create, change, archive and restore component registrations.
- **People and agents** that use the wiki through MCP clients, the wiki browser, or `POST /ingest`.
- **The server** (`server/`): authentication, authorization, audit, request checks, the security store, and the settings that drive them.
- **The container setup, CI and documentation** (`docker/`, `.github/workflows/`, `docs/`, `server/README.md`): secure defaults, a writable data volume (the image runs with a read-only root filesystem), a TLS setup, and the operations guide. The CI image check that asserts today's token behavior changes with this intent.
- **Instances already in use** with the shared token: they move to individual credentials in one step (see S8).

## Constraints
- **Safe by default.** A new install is protected without extra steps; turning protection off is a deliberate, loud act and is refused on any address other than the local machine.
- **Secrets stay out of the wiki.** Credentials are never stored in the instance repository, never written to the log or the git history, and never shown in full after creation. At rest the server keeps only hashes. The server holds no third-party secrets (a person's or agent's Anthropic key, a personal access token) and returns no secret through any tool.
- **Client compatibility.** Claude Code and VS Code (GitHub Copilot) keep working with a header they already support. A browser keeps working with the standard sign-in prompt. Claude Desktop and claude.ai are a known limitation: they connect from Anthropic's cloud and cannot reach a server on a private network. A later intent (INT-18) addresses it.
- **No new service needed.** The server needs no external identity provider, database server or network service. Its security data lives in one SQLite file in a data directory that is never inside the instance repository, readable only by the server's user.
- **A complete local mode.** With no GitHub App configured the server is fully usable and fully protected, permanently. All principals come from the host command.
- **One portable store.** Principals, roles, grants, denies and settings can be exported to and imported from a JSON file. The export never contains credentials, and contains hashes only when asked.
- **Admin is not data.** The admin role cannot read or write wiki pages, handoffs or raw documents through the server. (Someone with access to the host's disk can still read the files; protecting against them is out of scope.)
- **Administrative functions live on the host only,** not in MCP tools or HTTP routes, so a compromised agent cannot create credentials or widen its access. A principal that is an agent or a service can never hold the admin role.
- **The server writes only where it should.** A caller can write only to wiki pages in the scope it has authority for. Through the page tool it can never write the component registry, the generated sidebar and schema pages, or repository internals, and it cannot write a handoff page except through the handoff tool. Paths that leave the wiki folder are refused. Closing this gap is part of this intent, not a separate fix.
- **Revocation inside Manifold is immediate and durable.** A change made inside Manifold (revoking a credential, removing a grant, adding a deny, disabling a principal) takes effect on the very next request, is saved before it is reported as done, and survives a restart. A change made on GitHub is covered by INT-7.
- **Deleting a component takes deliberate steps.** Archiving needs a reason and no open handoffs; a hold period follows (14 days by default); permanent removal is a host action that needs the component's name typed. Agents can archive, within limits; they cannot purge or change a component's repository or owner.
- **Limits are settings, with defaults.** Agent registrars default to 5 registrations and 1 archive per day; the purge hold period, the failed-sign-in thresholds and the other numbers in this intent are administrator settings, and the numbers here are only the defaults.
- **TLS can be switched on and off.** The server can serve over TLS even when run locally or on a private network, and an administrator can turn it off. The shipped path is a Caddy service in the compose setup. Turning TLS off on any address other than the local machine is allowed only as a deliberate act with a visible warning.
- **Standards, not inventions.** Follow the current MCP authorization guidance and common web practice for token handling, host and origin checks, and TLS.
- **Offline-clean.** In local mode the wiki browser and the server make no outside requests.
- **Open license, no vendor lock.** Anything added must be Apache-2.0 compatible.
- **Reads.** Per-component read limits are not needed in the first version: any signed-in caller may read. (To be confirmed; see open questions.)
- **Priority.** This intent alone is the first shared-host milestone. It comes before the shared host is used by more than one person, and before the sign-in pieces of the new UI.

## Scenario seeds

### S1 — Each person has their own credential
**Who:** An administrator of a shared instance.
**Wants:** To give each team member and each agent its own credential with a command on the host, and to revoke one without affecting the rest.
**So that:** A lost laptop or a departed colleague is dealt with in minutes and nobody else is interrupted.
**We will know when:** After revoking one credential, that holder's next request is refused and every other holder's requests still work, with no server restart.
**Must never:** Show a credential in full after it is first issued, store it in the instance repository, or let a revoked credential keep working.

### S2 — An agent can only act for its own component
**Who:** An agent that is responsible for one component.
**Wants:** To create handoffs from, and claim handoffs for, its own component.
**So that:** The wiki's record of who asked whom for what can be trusted.
**We will know when:** The same agent's attempt to create a handoff from a different component, or to confirm, reject or close a handoff it did not create, is refused with a clear reason, and nothing is written.
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

### S7 — TLS is a setting, not a research project
**Who:** An administrator putting the server on a private network, or running it locally.
**Wants:** To turn TLS on or off with a setting, using the Caddy service in the compose setup, with the client steps for Claude Code, VS Code and a browser.
**So that:** Credentials do not cross the network in clear text, and a local trial is not blocked by certificates.
**We will know when:** Following the guide on a clean machine gives an HTTPS address that each listed client connects to; turning the setting off gives a plain address that works on the local machine; and the guide says what to do about certificates each client does not trust.
**Must never:** Tell people to turn off certificate checks in a client, or let TLS be turned off on a shared address without a visible warning.

### S8 — Retiring the shared token
**Who:** An administrator of an instance that uses the single shared token today.
**Wants:** To move to individual credentials with a short, documented set of steps.
**So that:** No instance keeps accepting a secret that everybody knows.
**We will know when:** After the upgrade the shared token is no longer accepted, the server says so when it starts and names the host command that creates the first administrator, and the guide lists the steps in order so the gap in access is minutes.
**Must never:** Silently keep accepting the old token, or start on a shared address with no principals and no protection.

### S9 — The admin manages the system but cannot read the wiki
**Who:** An administrator holding only the admin role.
**Wants:** To create principals, set roles and grants, and read the authentication audit.
**So that:** Systems management never needs access to the team's content.
**We will know when:** The same principal, calling any read or write tool through MCP or HTTP, is refused with a clear reason, and nothing is returned or written.
**Must never:** Let the admin role read wiki data through the server, or let an agent hold it.

### S10 — A registrar manages components
**Who:** A person or an agent holding the registrar role.
**Wants:** To register a component and change its description.
**So that:** Components can be kept in order without making that principal an administrator.
**We will know when:** The registrar's registration succeeds; its attempt to write a page or create a handoff for that component is refused unless it was granted access; an agent registrar's attempt to change the component's repository or owner is refused; and an ordinary contributor cannot change them even by editing the component page or the registry file.
**Must never:** Let a registrar gain contributor access to a component it registered without a grant or an explicit setting made by an administrator.

### S11 — Retiring a component takes deliberate steps
**Who:** A registrar.
**Wants:** To retire a component that is no longer used.
**So that:** A mistake or a misbehaving agent cannot erase a team's record in one call.
**We will know when:** Archiving without a reason, or with an open handoff, is refused and names the handoffs; an archived component rejects new writes, can be restored, and cannot be permanently removed through MCP; permanent removal happens only from the host after the hold period.
**Must never:** Let an agent permanently remove a component, or let an agent exceed its daily limits.

### S12 — The page that belongs to no component
**Who:** A person writing a decision, guide or intent page.
**Wants:** A clear rule for who may write pages that belong to no single component.
**So that:** Shared pages are neither open to everyone nor stuck.
**We will know when:** A principal with the shared grant can write a decision page; a principal with only a component grant cannot.
**Must never:** Let a component contributor change a shared page by accident.

### S13 — It all works without GitHub
**Who:** An administrator of a company that does not use GitHub, or works offline.
**Wants:** Full protection with no GitHub App and no outside requests.
**So that:** GitHub is never required to use Manifold safely.
**We will know when:** On a clean install with no GitHub settings, every other scenario passes and the server makes no outside request.
**Must never:** Switch a protection off because GitHub is not configured.

### S14 — Taking access away is immediate
**Who:** An administrator.
**Wants:** To revoke a credential, remove a grant, add a deny or disable a principal.
**So that:** Access ends when the administrator says it ends.
**We will know when:** The very next request from that holder after the command reports success is refused with a message that says access was removed, still refused after a server restart, and other holders are unaffected.
**Must never:** Report success before the change is saved, let a restart bring back removed access, or leave access in place through another route without saying so.

### S15 — Only the source closes a handoff
**Who:** An agent for the target component of a handoff.
**Wants:** To finish the work and ask for review.
**So that:** The component that asked is the one that decides the work is done.
**We will know when:** The target's attempt to close the handoff is refused with a clear reason; the source's close succeeds.
**Must never:** Let the target side close a handoff.

### S16 — A page can only be written where the caller may write
**Who:** A contributor for one component.
**Wants:** To write pages for its own component.
**So that:** It cannot overwrite the component registry, the sidebar, a handoff page outside the handoff tool, or anything outside the wiki folder.
**We will know when:** An attempt to write to the registry, a generated page, a handoff path, a path with `..`, or another component's pages is refused with a clear reason, and nothing is written.
**Must never:** Let the page tool reach any file outside the pages the caller has authority for.

## Out of scope
- Signing in through GitHub (INT-7) or any company identity provider.
- Claude Desktop and claude.ai access (INT-18).
- Acting as an MCP authorization server (INT-19).
- Per-component read permissions, finer than "any signed-in caller may read".
- An admin screen in the new UI (that comes with the UI).
- Encrypting the wiki content at rest.
- Holding third-party secrets (model keys, personal access tokens) on behalf of users.
- Webhook receivers and any other inbound network endpoint beyond the server's own.
- Protecting a host that is already compromised, or the people who hold admin access, or someone with access to the host's disk.
- Supply-chain work beyond pinning dependencies by hash in the lock file.
- Keeping the old shared token working beside individual credentials.

## Open questions
- What lockout behavior should the shared host use? Recommendation: slow down repeated failures per address with a growing delay, never lock a credential (credentials are long random values, so locking one would only let an attacker lock out its owner), and trust the forwarded address only from the Caddy service. (the product owner, once the choice is explained)
- Should per-component read limits be in the first version after all, given the wiki is read into agent context? (the product owner, with the company that will use it)
- When content moves to GitHub (INT-14) and the server has no local checkout, how does the host-only purge reach the content? (the product owner, with INT-14)
- May an administrator turn on the per-principal setting that lets an agent registrar receive a grant on the component it registers? The default is off. (the product owner)
