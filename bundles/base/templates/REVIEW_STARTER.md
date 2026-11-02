# Review instructions

## Passes

Run each pass and tag every finding with its pass:

- **Bugs:** logic errors, broken edge cases, subtle regressions, swallowed errors
- **Security:** injection, authentication and authorization gaps, secrets or personal data in code, logs or errors. Also check these rules:
  - Any value a caller supplies that is written into a page, a log, a commit message or a configuration or frontmatter block is untrusted: it must be validated or encoded, and one value must never become more than one entry or key.
  - Paths must be confined to the folders the caller may touch, compared case-insensitively, with no `..` and no absolute path that escapes.
  - Authorization must not depend on data the caller can edit.
  - Secrets and credentials never appear in code, logs, documents or error messages.
- **Compliance:** the change matches the approved plan (file inventory, acceptance lines, recorded deviations) and the intent's constraints
- **Tests:** a bug fix has a failing-first regression test and no existing test was edited to make it pass; the evidence in the completion note can be reproduced

## What Important means here

Reserve **Important** for findings that would break behavior, leak data, breach a policy, or contradict the plan, and for a security fix that has no failing-first test. Style and naming are **Nit**.

## Cap the nits

Report at most **5** nits per review; summarize the rest as a count.

## Project commands

Fill in from your `AGENTS.md`: how to install, build, check and test this project.

## Do not report

- Generated files and anything the continuous integration already enforces

## Human threshold

A human approves every merge. Name here the kinds of change that need a second person, for example migrations, public interfaces and security-sensitive code.
