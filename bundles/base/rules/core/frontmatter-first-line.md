---
id: frontmatter-first-line
title: Frontmatter placement
severity: high
applies_to: all
status: active
source: incident
---
## Rule
In any file that uses YAML frontmatter (agent, skill, command, prompt or documentation-site page), the opening `---` must be the very first line. Put license headers, comments and anything else after the closing `---`, or in a separate file.

## Why
Tools treat a file whose frontmatter is not on the first line as having no frontmatter, so its name, description and settings silently stop loading.

## Instead
Declare licensing in `LICENSE`, `NOTICE` or a `REUSE.toml` file, or place a short comment below the frontmatter.

## Enforce
- ci: lint that checks line 1 of every file that is expected to carry frontmatter
