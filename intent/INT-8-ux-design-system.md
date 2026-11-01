---
id: INT-8
title: The UX and design system for Manifold
author: Michael Hay
created: 2026-10-31
status: draft
affects: [docs, ui]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: The UX and design system for Manifold

## Problem
A new interface is planned, but there is no agreed picture of what it should look and feel like. Building screens first would settle the design by accident. The present wiki browser has a style people like, and the maintainers' other product has settings and profile panels that are a good model for configuration controls. Neither is written down as a design that a builder could follow.

## Proposed outcome
A design target that is approved before any interface code is written: the tokens (color, type, spacing), the page patterns for browsing, the panel patterns for settings and profile, the states (empty, loading, error), light and dark themes, and static mockups of the main screens. The design says what is borrowed from existing work and what is original.

## Affected users and systems
- **People who browse and edit the wiki,** and administrators who configure it.
- **The builders of the interface** (INT-9), who work from this design.
- **Anyone applying their own brand,** since brand packs are part of the design.

## Constraints
- **Look first, reuse later.** The existing product's panels are studied and a design is proposed. Nothing from them is copied (no logos, images, fonts or page source) until the owner decides what may be reused and records it.
- **Accessibility.** Readable contrast, keyboard use and visible focus are part of the design, not an afterthought.
- **Light and dark** themes from the start.
- **Offline-clean.** No fonts, icons or scripts fetched from outside.
- **Brand packs.** A deployer can change the logo and colors without editing code.
- **A person approves it.** The design is not final until a person says so.

## Scenario seeds

### S1 — See the target before it is built
**Who:** The product owner.
**Wants:** Mockups of the main screens in both themes.
**So that:** They can accept or change the direction before work starts.
**We will know when:** The design document links static mockups for browse, search, handoff board, intent editor and settings, in light and dark.
**Must never:** Start interface code before the owner approves the design.

### S2 — A settings screen follows a pattern
**Who:** A builder adding a configuration screen.
**Wants:** A documented panel pattern to follow.
**So that:** Every settings screen feels the same.
**We will know when:** A new screen can be built from the documented patterns without inventing new controls.
**Must never:** Copy assets or code from another product that the owner has not cleared.

### S3 — A deployer applies their brand
**Who:** A company administrator.
**Wants:** To set their logo and colors.
**So that:** The product looks like theirs.
**We will know when:** Changing one brand file changes the logo and accent color everywhere, in both themes, and contrast checks still pass.
**Must never:** Allow an uploaded image to run script (images are sanitized).

## Out of scope
- Writing interface code (INT-9).
- Marketing materials and the project website.

## Open questions
- Which parts of the existing product's look may be reused, and in what form? (the product owner)
- Is a design tool needed, or are static HTML mockups enough? (the product owner)
- How many brand packs ship with the first version? (the product owner)
