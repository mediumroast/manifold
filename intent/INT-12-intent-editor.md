---
id: INT-12
title: An intent editor with a model as partner
author: Michael Hay
created: 2026-10-31
status: draft
affects: [ui, sidecar, server]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: An intent editor with a model as partner

## Problem
Intents are the start of everything: the plan, the tests and the work all come from them. They are written today in a text editor from a template, by people who may not be used to writing requirements. The first draft is the hardest and the most important. A weak intent produces weak work, and nothing helps the author notice what is missing.

## Proposed outcome
A page in the interface where a person and a model write an intent together. The person edits the text with a live preview. A side panel lets them ask the model to interview them, draft a section, challenge a statement, tighten wording, or suggest scenario seeds. Each suggestion can be accepted or rejected piece by piece. The status of the intent is changed by a person only, and it records which model helped. The result is saved as an intent through the server.

## Affected users and systems
- **Product owners and analysts** who write intents.
- **The interface** (INT-9), **the model sidecar** (INT-10) and **the tool layer** (INT-11).
- **The server,** which stores the intent as a page.

## Constraints
- **A person decides.** The model suggests; nothing is applied without an accept, and status never changes by itself.
- **Works with each supported provider,** including private models, with the same behavior.
- **What leaves is shown** before the first model request of a session.
- **Provenance is recorded** in the intent's own fields (which model helped), not in hidden state.
- **Mandatory for the first interface release:** an intent editor that does not work does not ship.
- **Seeds stay public;** the editor says so and does not help write held-out scenarios.
- **Works when the model is down.** Editing and saving still work without the model.

## Scenario seeds

### S1 — Interview me
**Who:** An analyst with a rough idea.
**Wants:** The model to ask questions that draw out the intent.
**So that:** They produce a complete first draft quickly.
**We will know when:** From a one-line idea, answering the model's questions yields a draft with a problem, outcome, constraints and at least one seed with its observable "we will know when" and "must never".
**Must never:** Fill a section with invented facts the person did not state, without marking them as suggestions.

### S2 — Accept piece by piece
**Who:** An author reviewing suggestions.
**Wants:** To take some changes and reject others.
**So that:** The text stays theirs.
**We will know when:** Accepting one suggested paragraph changes only that paragraph, and rejecting another leaves the text untouched.
**Must never:** Apply a suggestion that was not accepted.

### S3 — Status is human
**Who:** An auditor.
**Wants:** Proof that a person accepted the intent.
**So that:** Approval cannot be faked.
**We will know when:** The status field can be changed to accepted only by a signed-in person, and the intent then shows who and when.
**Must never:** Let the model mark an intent accepted, even if asked.

### S4 — Save without a model
**Who:** A user on a host with no model configured.
**Wants:** To write and save an intent anyway.
**So that:** The editor is not useless offline.
**We will know when:** With the sidecar stopped, editing, preview and save work, and the AI panel says it is unavailable.
**Must never:** Lose the draft because the model failed.

## Out of scope
- Writing the plan or the scenarios.
- Editing other kinds of pages (a general page editor is separate).
- Training a model on intents.

## Open questions
- Does the editor save straight to the instance, or open a pull request, by default? (the product owner)
- How are the model's suggestions stored, if at all, after the session? (the product owner)
