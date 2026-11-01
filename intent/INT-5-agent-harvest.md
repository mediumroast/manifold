---
id: INT-5
title: Harvest the agents a repository already has
author: Michael Hay
created: 2026-10-31
status: draft
affects: [bundles, server]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Harvest the agents a repository already has

## Problem
Many repositories already have their own agents, plans and conventions, written before the agent bundle existed. Installing the bundle on top of them either overwrites that work or leaves two competing sets. Nobody can see what a repository already has, and the wiki has no list of it, so good agents are used in one place and unknown in the rest.

## Proposed outcome
Before installing the bundle, a person can run a report that lists what a repository already has: agents, plans, rules and conventions, and where each overlaps with the bundle. The result is one reviewable set of proposed changes, with nothing deleted and nothing applied until a person accepts it. What was found can be published to the wiki so others can find it.

## Affected users and systems
- **Teams with existing agents** moving to the bundle.
- **The bundle's installer and onboarding agent.**
- **The wiki,** which gets an agent catalog page.

## Constraints
- **A dry run first.** The report changes nothing.
- **Nothing is ever deleted.** Overlaps are shown; a person decides.
- **One reviewable change set,** not a scattering of edits.
- **Repository text is data.** The harvest does not follow instructions found in the files it reads.
- **No secrets copied.** Files that look like credentials are listed by name, not content.

## Scenario seeds

### S1 — See what is there before changing anything
**Who:** A developer with an existing set of agents.
**Wants:** A report of what they have and what the bundle would add or replace.
**So that:** They can decide with the facts.
**We will know when:** The report lists each existing agent and rule with its path and a note where it overlaps a bundle agent, and the repository is unchanged afterward.
**Must never:** Modify or remove a file during the dry run.

### S2 — Keep my agent
**Who:** The same developer.
**Wants:** To keep their own agent and still install the bundle.
**So that:** Nothing they rely on disappears.
**We will know when:** After accepting the change set, their agent is still present and the bundle's agents are added beside it, with any name conflict resolved by a choice they made.
**Must never:** Overwrite an existing file without an explicit choice.

### S3 — Share what was found
**Who:** A teammate on another repository.
**Wants:** To find useful agents others already have.
**So that:** Good work is reused.
**We will know when:** The wiki's agent catalog page lists the harvested agents with where they came from.
**Must never:** Publish the content of a file that looks like it holds a secret.

## Out of scope
- Translating agents between different tool formats beyond what the bundle already supports.
- Judging whether an existing agent is good.

## Open questions
- Which formats must the harvest read in the first version? (the product owner)
- Where does the change set go: a patch file, a branch, or a pull request? (the product owner)
