# Review instructions
<!--
  Template for the review policy of a repository.
  Copy this file to REVIEW.md at the repository root and edit it. The reviewer agent
  reads it before every review. Findings never approve or block a change on their
  own: a human approves, informed by the findings. Delete these comments when done.
-->

## Passes

Run each pass and tag every finding with its pass:

- **Bugs:** logic errors, broken edge cases, subtle regressions, swallowed errors
- **Security:** injection, authentication and authorization gaps, secrets or personal data in code, logs or errors
- **Compliance:** the change matches the approved plan (file inventory, acceptance lines, recorded deviations) and the intent's constraints
- **Tests:** a bug fix has a failing-first regression test and no existing test was edited to make it pass; the evidence in the completion note can be reproduced

## What Important means here

Reserve **Important** for findings that would break behavior, leak data, breach a policy, or contradict the plan. Style and naming are **Nit**.

## Cap the nits

Report at most **5** nits per review; summarize the rest as a count.

## Do not report

- Generated files and anything the continuous integration already enforces
- <!-- add paths or topics specific to this repository -->

## Human threshold

<!-- Who must approve before merge, and which kinds of change need a second person (for example migrations, public interfaces, security-sensitive code). -->
