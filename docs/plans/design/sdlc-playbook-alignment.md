<!-- SPDX-License-Identifier: Apache-2.0 -->
# Alignment with the AI-native SDLC playbook

**Status:** Active. This document compares Manifold with [*The AI-native SDLC playbook*](https://claude.com/resources/articles/the-ai-native-sdlc-playbook) by Louis Claxton (Anthropic). It is our reading, not the playbook's text, and the playbook is a third-party document, so it is linked, not copied here. The playbook is written around Claude Code; several things it leans on are beta or research preview, and nothing in Manifold depends on them.

## 1. The playbook in one page

A six-stage loop: Plan, Design, Build, Test, Deploy, Maintain. Each stage **ends by committing an artifact** and the next stage **begins by reading it**.

| Stage | Artifact | Human gate |
|---|---|---|
| Plan | `intent.md` (problem, outcome, affected systems, constraints, open questions) | Product owner accepts or closes |
| Design | `spec.md`, with flagged concerns | Product owner routes each concern to its policy owner |
| Build | `plan.md` (files, order, risks, proof), then the diff and tests | Engineer accepts the plan |
| Test | Failing test first, then green; literal command output as evidence | Code owner reviews with evidence attached |
| Deploy | A pull request with review findings | Branch protection and a named release manager |
| Maintain | An incident record, which re-enters as a new intent | Service owner triages |

Principles we take seriously: the chain of commits is the audit trail; skills are advisory while hooks are deterministic; the agent that wrote the code cannot approve it; the agent acts up to a gate and cannot pass it; every artifact has a named source of truth; context files stay small and learn from mistakes.

## 2. Where we converge

| Playbook idea | In Manifold | Strength |
|---|---|---|
| Committed artifacts as the audit trail | Intents, plans, test plans and walkthroughs are files in the repository | Strong |
| Plan before code, reviewable without the conversation | Planner self-check, `PHASE_<N>_PLAN.md`, `approved-plan-before-execution` | Strong |
| The plan stays truthful when implementation departs | The plan is a contract; blocked work is marked and deviations are recorded | Strong |
| Humans at gates | The **Approved by** line, `human-confirms-closure`, `ask-on-ambiguity` | Strong, and seen holding on Sonnet |
| Small context that learns from mistakes | Rules with Rule, Why, Instead and Enforce; a managed `AGENTS.md` block | Strong |
| Test first for bug fixes; never weaken the check | `bug-coder`: failing test first, then the fix; `dont-edit-the-test-to-pass` | Partial: held on Sonnet, failed on a smaller model |
| Verify with evidence | Project-facts discovery; evidence in completion notes | Strong |
| Separation of duties | The read-only `reviewer`; the quality repository | Partial: conventions, not enforcement |

## 3. Where we depart

| Playbook | Manifold | Verdict |
|---|---|---|
| One product, one repository, one intent home | Many repositories, with a shared place for intents and handoffs | Healthy and our reason to exist. The playbook itself says a dedicated intent repository pays off when intent spans many repositories |
| Claude Code first (plan mode, hooks, managed settings) | Tool-neutral: Claude Code, Copilot, Agent Skills; no server for the base bundle | Healthy, but it costs enforcement: hooks are a Claude Code feature, so our rules are advice elsewhere |
| Three documents: intent, spec, plan | One plan per unit of work, with an intent in front | Partly deliberate; an optional spec is later |
| A human product owner reviews AI-drafted artifacts | The planner drafts in an intent mode; the human is the owner and accepts | Aligned if the agent never self-accepts, which is a tested rule |
| Metrics from one git history | Lineage that can span repositories | An opportunity: cross-repository cycle time |
| Narrow report-only subagents (verifier, researcher) | Role agents, plus a read-only reviewer | Gap: no verifier or researcher yet |
| Evals gate changes to context files, skills and hooks | We test rendering automatically and behavior by hand | Gap, and the one most relevant to "ready for real use" (see [testing-protocol.md](testing-protocol.md)) |
| Closing the loop: monitoring writes the next intent | Not before 1.0 | Deliberate |
| Org-wide distribution by plugin marketplace | A per-repository installer with a manifest | Gap for organizations: no layered rule packs or rule owners |

## 4. What has been built from this, and what has not

| Item | State |
|---|---|
| Intent template; planner intent mode with `Source intent` and flagged concerns | Built (v0.1.0) |
| `reviewer` (read-only, never approves) and review template | Built; the reviewer held its role on Sonnet, and on a smaller model it declined for the wrong reason, which led to a stronger rule |
| Bug-coder test first; the test stays | Built; hardened after a live failure |
| "Rules are advice" stated in the README | Built |
| Live-client acceptance protocol | Built, run in both clients |
| Verifier and researcher roles | Planned |
| Claude Code hooks pack | Exploring: Claude-only, touches settings, not yet tried |
| Evals in CI | Planned: needs an API key and budget |
| Organization rule packs, rule owners | Exploring |
| Spec template and mode | Later, after real use of intent mode |
| Intent as a first-class shared artifact, fan-out to one handoff per repository, cross-repository lineage | Design with the server; decided before formats freeze |

## 5. What multi-repository organizations need that the playbook does not cover

1. **An intent home that spans repositories**, as a first-class artifact with an owner and a status.
2. **Fan-out:** one accepted intent producing one handoff per affected component, each planned in its own repository.
3. **Cross-repository lineage:** the intent's identifier carried through handoffs, issues and pull requests, so cycle time per intent is computable.
4. **Ordering and contracts** between repositories: what a plan needs from another and what it provides.
5. **Policy at three layers:** core, organization, repository, with an owner per rule, not tied to one client.
6. **Source of truth per artifact**, with linkage as the minimum bar.
7. **Independent review across repositories**, using the other repository's contracts.
8. **Agent identity:** one identity per role, so permissions can be real.

| Artifact | Source of truth |
|---|---|
| Intent | Its file in the intent home |
| Handoff | Its file, with an issue in the target repository as a projection |
| Plan | `docs/plans/PHASE_<N>_PLAN.md` in the target repository, naming its intent |
| Diff and review | The pull request |
| Rules and agents | The bundle, an organization pack, and repository overrides, with hashes in the manifest |

## 6. Risks

| Risk | Mitigation |
|---|---|
| We copy a vendor's shape instead of ours | Adopt only where it matches a Manifold principle; section 3 records each departure on purpose |
| A reviewer without enforcement is another opinion | Say so; pair with branch protection and, later, hooks |
| Reliance on beta features | None used; every item works with plain files and any client |
