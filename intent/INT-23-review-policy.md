---
id: INT-23
title: Is a review policy file needed, and what should it say
author: Michael Hay
created: 2026-11-02
status: draft
affects: [bundles/base]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Is a review policy file needed, and what should it say

## Problem
The bundle's `reviewer` agent reads a repository-level `REVIEW.md`, written from `REVIEW_TEMPLATE.md`: the passes, what counts as Important, the nit cap, what not to report, and a **Human threshold** line (who must approve, and which changes need a second person). Draft PR #27 now carries a root `REVIEW.md` and a bundle starter, `bundles/base/templates/REVIEW_STARTER.md`.

That file was not something the owner asked for as such. Its Human threshold line says a second person must approve changes to `server/manifold_security/`, `server/wiki_backend/auth.py`, `docker/`, `bundles/base/` and accepted intents. The planner and coder agents invented that rule, and this repository has one maintainer, so there is no second person to satisfy it. A rule that cannot be met is worse than none: it is either ignored (and teaches that rules can be ignored) or it blocks every change.

The wider question is whether the thinking behind `REVIEW.md` is still needed at all. INT-21 puts the review in a written procedure with a `REVIEW_PLAN_X.md` output, and INT-22 adds a coordinator that checks a review happened before a PR is ready. Part of what `REVIEW.md` holds may now belong there, part may still need a home, and part may be unneeded.

The owner keeps `REVIEW.md` in PR #27 for now. This intent is about what to decide next, not about removing it.

## Proposed outcome
A decision, with reasons, recorded through the normal intent -> plan cycle, on four questions:

1. **Is a `REVIEW.md` needed at all?** Options (not a decision):
   - **A. Keep it as the repository's review policy**, as the template intends: a short file the reviewer reads before every review.
   - **B. Fold its content into the review procedure** (INT-21): the passes, severity meanings and nit cap become part of the reviewer's definition and the `REVIEW_PLAN_X.md` template, and the repository has no separate file.
   - **C. Keep a minimal file** with only the parts that differ per repository (what not to report, extra paths of concern, the approval rule) and move the defaults into the reviewer.
   - **D. Drop the policy file** and let the intent, the plan and the rules carry everything; the reviewer uses its built-in defaults.
2. **What should it contain, if kept?** Which of passes, severity meanings, nit cap, do-not-report list and human threshold belong in it, and what is left to the reviewer's defaults.
3. **Who approves, in a solo repository versus a team?** Options:
   - **Solo:** the owner approves everything; the review (INT-21) and its recorded findings are the second look, and the file says so. No "second person" is named.
   - **Team:** named roles or paths need a second approver, written by the owner, never invented by an agent.
   - **Either:** the file states which mode the repository is in, and the agents apply the rule for that mode.
4. **Who may write or change the policy?** The owner decides the approval rule. An agent may draft a policy as a proposal, but never states a rule as if it were agreed (the same line as for acceptance and approval).

The intent is resolved when the owner picks an option for each question, the bundle and PR #27's follow-up reflect the choice in both agent flavors, and a rule that cannot be met by the people in the repository no longer exists.

## Affected users and systems
- **The owner**, who decides the approval rule and whether the file stays.
- **The `reviewer` agent**, which reads `REVIEW.md` (or its replacement), and the **coordinator** (INT-22), which checks the human threshold before marking a PR ready.
- **Bundle contents:** `bundles/base/templates/REVIEW_TEMPLATE.md`, the starter `REVIEW_STARTER.md`, `reviewer.agent.md`, `build.py`, `install.py`, the bundle tests and docs.
- **The root `REVIEW.md`** in repositories that install the bundle, including this one (as carried by PR #27).
- **Both agent flavors.**

## Constraints
- **Both flavors.** Whatever is decided applies to the `claude` and the `copilot` flavors.
- **Not in PR #27.** The change is not added to PR #27 or to branch `claude/sub-agents-access-e9e255`. PR #27 keeps its `REVIEW.md` until the owner decides otherwise; any later change to it is a separate action.
- **No invented authority.** No agent states a rule about who approves, or who counts as a second person, that the owner did not give.
- **Solo repositories must work.** A repository with one maintainer can complete a cycle with no unmeetable rule.
- **Teams must be able to add a rule.** The design leaves room for a second-approver rule where there is a team.
- **Consistency with INT-21 and INT-22.** The decision must not duplicate or contradict the review procedure or the coordinator's ready check.
- **Existing installs stay valid.** A repository with an existing `REVIEW.md` keeps working whichever option is chosen.
- **Concise.** The result is short; it follows the "plans stay concise" rule.

## Scenario seeds

### S1 — A solo repository has no rule it cannot meet
**Who:** The sole maintainer of a repository that uses the bundle.
**Wants:** A review policy that they can satisfy.
**So that:** Their cycles end instead of waiting for an approver who does not exist.
**We will know when:** The repository's policy (or its absence, by the chosen option) names the owner as the approver, and a review cycle completes with nothing waiting on a second person.
**Must never:** Require an approver who is not in the repository, or leave a rule that every change breaks.

### S2 — A team can state its second-approver rule
**Who:** An owner of a repository with several maintainers.
**Wants:** To say which areas need a second person.
**So that:** Sensitive changes get a second look.
**We will know when:** The policy has a place to name the areas and the approver roles, written by the owner, and the reviewer and coordinator report when the rule applies to a change.
**Must never:** Let an agent add or change the rule on its own.

### S3 — The reviewer still knows what to look for
**Who:** The `reviewer` running on a change in a repository with no policy file (or a minimal one).
**Wants:** Sensible defaults.
**So that:** A review does not depend on a file being present.
**We will know when:** The review states which policy it used (file, or built-in defaults) and still covers the passes, severity meanings and nit cap.
**Must never:** Stop for lack of a policy, or invent a human threshold.

### S4 — The decision is traceable
**Who:** A later maintainer wondering why the repository has (or lacks) a `REVIEW.md`.
**Wants:** The reason.
**So that:** They do not undo it by accident.
**We will know when:** The plan that resolves this intent records the option chosen for each of the four questions and who decided.
**Must never:** Change the file with no record of the owner's decision.

## Out of scope
- The review procedure and `REVIEW_PLAN_X.md` (INT-21) and the coordinator's duties (INT-22), except where this decision touches them.
- Editing or removing PR #27's `REVIEW.md` before the owner decides.
- Branch protection, CODEOWNERS and hosted review settings.
- Changing the review passes themselves.

## Open questions
- Which option (A-D) for question 1? (the product owner)
- If a file stays, which of its sections are required? (the product owner)
- Should the file declare its mode (solo or team), or should the agents infer it? (the product owner)
- Should CODEOWNERS, or a similar hosted setting, carry the team rule instead of a file the agents read? (the product owner)
- What happens to `REVIEW_STARTER.md` in the bundle under each option? (the product owner)
