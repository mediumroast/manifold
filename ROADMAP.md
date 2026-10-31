<!-- SPDX-License-Identifier: Apache-2.0 -->
# Roadmap

manifold helps people and AI agents work together on software across many repositories: it keeps plans, decisions and cross-repository handoffs in one place, and gives agents consistent roles, rules and documents to work from. This roadmap lists the major milestones. It has no dates, and it will change as we learn.

**Status key:** Done · In progress · Planned · Exploring

## How we release

- **Small releases, in the open.** Each milestone leaves something that works.
- **Formats freeze before the first server release.** Directory layout, page formats and handoff fields are fixed once, before the server is public. After that, changes are additive, and breaking changes come with a migration.
- **Humans stay at the gates.** Agents draft; people accept intents, accept plans and confirm fixes.

## 0.1.0 — The agent bundle  *(In progress)*

Role agents, rules, document templates and an installer that works in any repository, with no server.

- Seven role agents for Claude Code and GitHub Copilot, plus an experimental Agent Skills rendering: planner (with an intent mode), coder, bug-coder (failing test first), reviewer, test-planner, test-coder and scenario-writer
- A library of rules, each with the reason behind it and what to do instead
- Templates for intents (with scenario seeds), plans, test plans, walkthrough notes, scenarios and reviews
- Install profiles: `build` for product repositories, `quality` for a separate repository of behavior scenarios, and `single` to start in one repository (with a warning that verification is then not independent)
- Quality settings with numerical thresholds as defaults you can change
- A deterministic installer that shows what it will do first and never overwrites your edits
- This roadmap

## First UI release — Server and interface  *(In progress)*

The server, security baseline and web interface, ready together.

Already in the repository, not yet released:

- The server: a component registry, handoffs with etag-checked writes, onboarding, bundle information and helper export, and a log of every operation
- A shared-token check, loopback by default, and health checks. This is a stopgap, not the security baseline below
- A wiki browser served by the server itself, with no outside requests
- Container files, a made-up example wiki and an empty starter wiki

- Run from nothing to a working instance with one registered component and a handoff, with `manifold init` creating your instance repository from a template
- Authentication and TLS by default
- A web interface to browse, search and review
- **An intent editor**: a human and an AI write the intent together in markdown, with a model of your choice, including local models
- Frozen formats for components, handoffs, intents and quality components

## Storage

- A storage interface with a local git implementation  *(Planned)*
- A GitHub API implementation, so the server needs no checkout  *(Planned)*

## Collaboration

- Optional projection of a handoff into a GitHub issue in the target repository  *(Planned)*
- Change policies: direct commits, automatic pull requests, or pull requests that wait for review  *(Planned)*
- A review queue in the interface, and lineage across repositories from intent to handoff to pull request  *(Planned)*

## Independent verification

- Behavior scenarios kept in a separate quality repository, derived from the intent's scenario seeds, so the AI that builds the code does not write the tests that judge it  *(Planned)*
- An optional quality repository kit: a template plus a generic scenario-to-test engine that works with local or hosted models  *(Planned)*
- Satisfaction reports per scenario seed  *(Exploring)*

## 1.0

- Hardening, a documented upgrade path, packaged releases  *(Planned)*
- Sign-in through an identity provider  *(Planned)*

## Later

- Break an accepted intent down into a GitHub Project  *(Exploring)*
- Onboarding that harvests the plans, agents and conventions a repository already has  *(Planned)*
- Layered rule packs for an organization, with named owners  *(Exploring)*
- Optional enforcement hooks for tools that support them  *(Exploring)*
- Behavioral clones of services a component depends on, built from integration specs  *(Exploring)*
- An add-on bundle for wiki and handoff workflows  *(Exploring)*

## Not planned

- Hosting manifold as a service
- Telemetry of any kind
- Replacing your git host
