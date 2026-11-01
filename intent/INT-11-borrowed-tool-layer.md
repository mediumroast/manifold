---
id: INT-11
title: A borrowed tool layer for models
author: Michael Hay
created: 2026-10-31
status: draft
affects: [sidecar, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A borrowed tool layer for models

## Problem
When a model helps write an intent or update a page, it needs tools: read a file, list a folder, search the wiki, look at the surrounding repository. Inventing a tool harness is a large job that others have already done and keep improving. A homemade one would also be one more thing to secure. Repository text that a model reads can contain instructions, and a tool layer without safeguards turns that into an attack.

## Proposed outcome
The model features use an existing, well-supported tool set or harness directly, chosen after a short written comparison. The choice is restricted to what the features need: reading, listing and searching inside an allowed folder, and optional web fetch that is off by default. It cannot run commands or write beyond the document being edited. The reasons for the choice are recorded.

## Affected users and systems
- **People using model-assisted features,** who need the model to see the right context.
- **The model sidecar** (INT-10), which hosts the tools.
- **Maintainers,** who prefer to maintain as little tooling as possible.

## Constraints
- **Borrow, do not invent.** Use an existing harness or standard tool set as it is, wrapping it only where a safeguard is needed.
- **Compatible license** (Apache-2.0 compatible).
- **Works with local models** as well as hosted ones.
- **Read-only by default,** restricted to an allowed root; no shell; writes only to the one document being edited.
- **Repository text is data,** never instructions; the layer says so to the model and does not let that text change the tool set.
- **Web access is off by default,** and when on, shows what it fetches.
- **One choice with reasons,** and a stated way to change it later.

## Scenario seeds

### S1 — The comparison is written down
**Who:** The product owner.
**Wants:** To see candidates compared before one is chosen.
**So that:** The choice is deliberate and reviewable.
**We will know when:** The comparison covers license, local-model support, a read-only mode, root restriction and prompt-injection safeguards, and ends with one recommendation and why.
**Must never:** Adopt a candidate without recording why the others were not chosen.

### S2 — The model cannot leave its folder
**Who:** A security reviewer.
**Wants:** The tools to stay inside the allowed root.
**So that:** A model cannot read other files on the host.
**We will know when:** A test asks the tools for a path outside the root, including through symbolic links and `..`, and each request is refused.
**Must never:** Allow a read or write outside the root.

### S3 — Hostile page text does not change behavior
**Who:** A reviewer.
**Wants:** Instructions inside a page to be treated as content.
**So that:** A planted page cannot steer the model into acting.
**We will know when:** A test page that tells the model to delete files or fetch a URL causes no such action.
**Must never:** Run a tool because page text told the model to.

## Out of scope
- Building a new agent runtime.
- Giving models shell access or write access beyond the document.
- The model providers (INT-10).

## Open questions
- Which candidates are on the list? (the product owner)
- Is web fetch needed in the first version at all? (the product owner)
