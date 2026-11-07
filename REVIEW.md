# Review instructions

## Passes

Run each pass and tag every finding with its pass:

- **Bugs:** logic errors, broken edge cases, subtle regressions, swallowed errors
- **Security:** injection, authentication and authorization gaps, secrets or personal data in code, logs or errors. Also check these rules from INT-1:
  - Any value a caller supplies that is written into a page, a log, a commit message or frontmatter is **untrusted**: it must be validated or encoded, and one value must never become more than one entry or key.
  - Paths must be confined to the folders the caller may touch: compared case-insensitively, with no `..` and no absolute path that escapes.
  - Authorization must not depend on data the caller can edit (a handoff's source, a principal's roles, a page's frontmatter).
  - Secrets and credentials never appear in code, logs, pages or errors.
- **Compliance:** the change matches the approved plan (file inventory, acceptance lines, recorded deviations) and the intent's constraints
- **Tests:** a bug fix has a failing-first regression test and no existing test was edited to make it pass; the evidence in the completion note can be reproduced

## What Important means here

Reserve **Important** for findings that would break behavior, leak data, breach a policy, or contradict the plan, and for a security fix that has no failing-first test. Style and naming are **Nit**.

## Cap the nits

Report at most **5** nits per review; summarize the rest as a count.

## Project commands

The build, check and test commands are in `AGENTS.md`, section "Project commands"; do not copy them here.

## Do not report

- Generated files and anything the continuous integration already enforces
- Vendored web files that the repository's own vendored-files check covers

## Who approves

Stated in `AGENTS.md`, section "Review process". This file adds no approval rule.
