# Contributing

Thanks for helping. This bundle is small on purpose, so changes are reviewed for clarity and generality.

## Ground rules

- Licensed under the **Apache License 2.0**. By contributing you agree your work is licensed the same way.
- Sign off every commit (`git commit -s`) to certify the [Developer Certificate of Origin](https://developercertificate.org/).
- Keep it generic: no company, product or customer names, and no project-specific paths.

## Adding or changing a rule

One rule per file in `rules/core/`, named `<id>.md`. The file needs frontmatter (`id` equal to the file name, `title`, `severity`, `applies_to`, `status`, optional `source`) and three sections: **Rule**, **Why**, **Instead** (and optionally **Enforce**). A rule without a *why* and an *instead* is rejected: a bare "don't" leaves the agent without a next move.

Good rules are things that have actually gone wrong, stated in general terms. Keep the core set small enough to read in one sitting. Retire a rule by setting `status: deprecated`, never by silently deleting it.

## Changing an agent or template

Edit the canonical source in `agents/`, `fragments/` or `templates/`. Do not edit rendered output. Frontmatter must be the first line of every agent file.

One source renders to three formats: Claude agents, Copilot agents and Agent Skills. When text refers to a sibling role, use `{{ref:coder}}` (renders as "`coder` agent" or "`execute-plan` skill") or `{{name:coder}}` (just the name) instead of writing the name, so each format points at its own entry points. The lint rejects unknown roles and any marker left unexpanded, and checks every rendered skill against the Agent Skills specification.

## Before you open a pull request

```bash
python3 tools/build.py --check
python3 -m pytest tests -q
```

Both must pass. The lint checks frontmatter placement, required fields, unresolved placeholders, rule structure and forbidden terms.
