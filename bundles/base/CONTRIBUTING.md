# Contributing

Thanks for helping. This bundle is small on purpose, so changes are reviewed for clarity and generality.

## Ground rules

- Licensed under the **Apache License 2.0**. By contributing you agree your work is licensed the same way.
- Sign off every commit (`git commit -s`) to certify the [Developer Certificate of Origin](https://developercertificate.org/).
- Keep it generic: no company, product or customer names, and no project-specific paths.

## Adding or changing a rule

One rule per file in `rules/core/`, named `<id>.md`. The file needs frontmatter (`id` equal to the file name, `title`, `severity`, `applies_to`, `status`, optional `source`) and three sections: **Rule**, **Why**, **Instead** (and optionally **Enforce**). A rule without a *why* and an *instead* is rejected: a bare "don't" leaves the agent without a next move.

`applies_to` lists roles (`planner`, `coder`, `bug-coder`, `reviewer`, `test-planner`, `test-coder`, `scenario-writer`, `coordinator`) or `all`. Rule text must not use `{{ref:...}}` markers; name roles in plain words.

Good rules are things that have actually gone wrong, stated in general terms. Keep the core set small enough to read in one sitting. Retire a rule by setting `status: deprecated`, never by silently deleting it.

## Changing an agent or template

Edit the canonical source in `agents/`, `fragments/` or `templates/`. Do not edit rendered output. Frontmatter must be the first line of every agent file.

Roles belong to install profiles (`PROFILES` in `tools/build.py`). An agent may refer to a sibling role with `{{ref:...}}` only if every profile that installs the agent also installs that sibling; the lint checks this.

One source renders to three formats: Claude agents, Copilot agents and Agent Skills. When text refers to a sibling role, use `{{ref:coder}}` (renders as "`coder` agent" or "`execute-plan` skill") or `{{name:coder}}` (just the name) instead of writing the name, so each format points at its own entry points. The lint rejects unknown roles and any marker left unexpanded, and checks every rendered skill against the Agent Skills specification.

## Changing the guard hook

`hooks/guard.py` is the pre-tool hook that clients run; it must stay standard library only and written for Python 3.10 or newer (the lint compiles it and rejects any import outside the standard library). `tests/test_guard.py` loads it as a module and checks it three ways: tables of shell commands that must be refused and commands that must pass (including read-only uses such as `2>&1` and a `>` inside a quoted argument), the write limits per agent identity and the protected files, and runs of the script itself the way a client does, with the call as JSON on standard input, asserting the exit code (2 for Claude Code), the deny JSON for Copilot, and the line added to the refusal log. A change to the guard starts with a test that fails for the new case, then the fix, and the same pull request updates the residual-gaps list in the header of `hooks/guard.py` when a limit changes. The hook command written into each agent definition and `hooks/copilot-guard.json` are pinned in `tests/test_bundle.py`. What a client actually runs is not tested here; the capability record for each client says which statements are read from vendor documentation and which are unverified.

## Before you open a pull request

```bash
python3 tools/build.py --check
python3 -m pytest tests -q
```

Both must pass. The lint checks frontmatter placement, required fields, unresolved placeholders, rule structure and forbidden terms.
