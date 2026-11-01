---
id: INT-3
title: Test data sets, real and synthetic
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, examples, tests]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Test data sets, real and synthetic

## Problem
The only test content is one small made-up instance with three components. It is too tidy. Real wikis have dotted names, duplicate pages, stale pages, long pages, odd characters, and text written to fool an AI reader. A server that has only been tried on tidy data will fail in front of real data. Real data would be a better test, but real company content cannot be put in a public repository.

## Proposed outcome
There is a generator that builds instances of any size from a fixed seed, and a small set of curated instances for the messy cases. Tests and demos can ask for "a medium instance" or "an instance with hostile text" and get the same one every time. A written rule says what real data may be used, who must give permission, and how it is scrubbed, so the answer is never improvised.

## Affected users and systems
- **Maintainers and test authors** (server tests, contract tests, the future UI).
- **Anyone trying the product**, who gets bigger and more realistic example instances.
- **The owners of any real data** offered as a source.

## Constraints
- **Nothing real enters a public repository without written permission from its owner and a scrub that has been checked.** Until then, only synthetic data is committed.
- **Deterministic.** The same seed always produces the same instance, byte for byte.
- **Small enough to commit,** or generated on demand when large.
- **Covers the awkward cases:** dotted and similar slugs, a page with no frontmatter, duplicates, stale pages, very long pages, non-English text, and content that contains instructions aimed at an AI.
- **No personal data,** even fake data that looks like a real person's.

## Scenario seeds

### S1 — Ask for an instance by size
**Who:** A test author.
**Wants:** A small, medium or large instance with one call.
**So that:** Tests do not each invent their own data.
**We will know when:** The same call twice produces identical trees, and the large one still passes the server's health check.
**Must never:** Produce a different tree for the same seed.

### S2 — Hostile text is in the set
**Who:** A security-minded reviewer.
**Wants:** Pages that contain instructions meant to steer an AI agent.
**So that:** Tests can check that such text is treated as content.
**We will know when:** A test loads those pages, and the server returns them as plain page content without acting on them.
**Must never:** Include text that is harmful beyond being a test string.

### S3 — A real source is scrubbed before use
**Who:** An owner who offers real content for testing.
**Wants:** A checked procedure to remove names, hosts and secrets.
**So that:** Something real-shaped can be used without exposing anything.
**We will know when:** The scrubbed set passes the forbidden-terms scan, the owner has signed off in writing, and the record of that is in the repository.
**Must never:** Commit the original, or a scrub nobody checked.

## Out of scope
- Performance benchmarking.
- Contract tests (INT-2 covers them).
- Generating content with a language model.

## Open questions
- Will the new company or the maintainers' other products offer real data, and under what terms? (the product owner)
- What sizes are "small", "medium" and "large"? (the product owner)
- Should the large set be committed, generated in CI, or fetched? (the product owner)
