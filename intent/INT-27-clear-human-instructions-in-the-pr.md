---
id: INT-27
title: Tell the human exactly what to do, and where to write, in the pull request
author: Michael Hay
created: 2026-11-13
status: draft
affects: [bundles/base, docs/templates, docs/process, bundles/base/agents/coordinator.agent.md]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Tell the human exactly what to do, and where to write, in the pull request

## Problem
The owner tried to finish Phase 3 by working through pull request 31 and could not tell what to do. In his words: "Instruction writing is nonexistent or unclear." INT-26 made finishing a phase lighter by moving the human steps into the pull request. It did not make those steps self-explanatory. Gaps seen in that pull request (the template is `bundles/base/templates/PULL_REQUEST_TEMPLATE.md`, installed as `docs/templates/PULL_REQUEST_TEMPLATE.md`, the two files are identical):

1. **The ready-check table never says to replace the word.** The column header reads `State (met / missing)`. The owner did not know that the cell is meant to hold one of those two words in place of the header text.
2. **The ticks say who, not how.** "A tick is a human act", "the tick is yours" and "yours to give" (the "What remains for you" comment, the coordinator's ready-check and CI text, `docs/process/REVIEW_CYCLE.md` ready check item 3) say a human acts. They do not say what to look at first, where to click, or what to do when the thing checked is red.
3. **Name fields have no placeholder.** **Confirmed by** (under "CI on the pushed commit") and **Human confirmation** (under "Ready check") are blank or hold prose. There is nothing to replace, so a name was typed unprompted, with no date format shown.
4. **GitHub's own Approve review is not mentioned.** The ruleset records one approving review as required (`docs/process/BRANCH_RULES.md`, "Approving reviews"). That is a separate act in GitHub's "Review changes" control and is not one of the description's rows. Nothing in the pull request says it exists, or how it relates to the rows and ticks in the description.
5. **Solo repository and the required review.** `docs/process/BRANCH_RULES.md` itself says how the owner's approval is met under the ruleset "is not stated by the ruleset and is not recorded here". Whether GitHub lets the author approve their own pull request, and what to do if it does not, is written nowhere.
6. **The owner's example (CI line).** The line "Run: read by the coordinator with gh run list --commit for exactly this commit ... Confirmed by: Michael Hay on November 13, 2026" is one dense line of agent shorthand. It does not say that the reviewer should open the two links, what counts as success, what to do when a run failed, or what to write and where.

The cost: a human is the gate for every pull request, so a gate whose instructions are not in the pull request is a gate the human has to reverse-engineer each time.

## Proposed outcome
A person who has never read the process documents can open a pull request produced by the coordinator and finish their part by following only the text in the pull request.

1. **The instructions are in the pull request itself.** Each place where a human must act carries, next to it, an **Instructions** block that says what the human must do. The block is not a link to a document and not a comment in the template that is deleted from the finished description.
2. **Each block is clear and complete.** It states what to check and where (the link, the file, the table cell), where to click or write, what a good result looks like, and what to do if the check fails (who to tell and what not to write).
3. **Every place a human writes a name and date has a replaceable slug.** The slug shows the shape of the answer, for example `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>`. The human replaces the whole slug, brackets included. An unreplaced slug is unmistakable and detectable by a script.
4. **State cells say what to write.** Where a table cell expects a word or value from a list, the cell or its instructions name the allowed values and say to replace the placeholder text.
5. **GitHub's Approve review is covered.** The pull request says that GitHub's Approve review is a separate step from the description's rows and ticks, says whether it is needed (it is when the ruleset requires it), where to click, and what to do if GitHub does not allow it.
6. **Lines are readable.** Dense lines are split into numbered sub-items (for example each workflow run on its own line with its link), so a human can check them one by one.

Worked example from the owner, for the CI line. Before:

```
Commit (full hash): 36e31b58e5862a07fb54ff79029c587296ac68a8 (pushed; the head of the branch)
Run: read by the coordinator with gh run list --commit for exactly this commit (each run headSha equals the commit): workflow ci, run 43313444747, completed, success, <link>; workflow server, run 43313444759, completed, success, <link>
Confirmed by: Michael Hay on November 13, 2026
```

After:

```
Commit (full hash): 36e31b58e5862a07fb54ff79029c587296ac68a8 (pushed; the head of the branch)
1. Ran: read by the coordinator with `gh run list --commit` for exactly this commit (each run headSha equals the commit):
   1. workflow ci, run 43313444747, completed, success, <link>;
   2. workflow server, run 43313444759, completed, success, <link>
**Instructions:**
1. Reviewer, please browse to the two links for each CI run above and manually verify they completed successfully.
2. If both completed successfully, type your approval below next to `Confirmed by:`.
3. If one or more failed please inform the coordinator agent to investigate and do not add your name next to `Confirmed by:`.
Confirmed by: <Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>
```

## Affected users and systems
- **The human approver** (the owner in this repository, a second approver in a team repository), who follows the instructions.
- **Agents:** the `coordinator`, which fills in the pull request description and writes the CI result line, and any agent or person who copies the template.
- **Files:** `bundles/base/templates/PULL_REQUEST_TEMPLATE.md` and its installed copy `docs/templates/PULL_REQUEST_TEMPLATE.md`; `bundles/base/agents/coordinator.agent.md` (CI of the exact commit, Ready check); `docs/process/REVIEW_CYCLE.md` and its bundle source (ready check, "Where each fact is recorded"); `docs/process/BRANCH_RULES.md` (the approving-review row; this file is not shipped); the other human-written lines in the templates (plan **Approved by**, **Amendment approved by**, intent **accepted_by**) if the owner decides so (see Open questions).
- **Tools that read the description:** the coordinator's ready check and `/phase-status` (`bundles/base/commands/phase-status.md`, with its script), which must be able to tell a filled field from an unfilled one.
- **Both flavors** (`claude` and `copilot`) and **repositories that install the bundle**.

## Constraints
- **A human keeps the final say.** Instructions tell the human what to do; they never do it. The coordinator never approves, never moves a pull request out of draft, never merges, never ticks, never fills in an approval line (`AGENTS.md` "Plan approval"; coordinator definition; INT-22 "A human decides"; INT-26 "A human keeps the final say").
- **Instructions are in the pull request.** Linking to a process document may add detail but cannot replace the text; the human must be able to act with the pull request alone.
- **Ready still means reviewed.** No ready-check line is dropped or loosened; this changes how it is explained, not what it requires (INT-22, `REVIEW_CYCLE.md` "The ready check").
- **Approval follows the review policy.** The rule in `AGENTS.md` "Review process" and INT-23 stays; a solo repository is not made to look like a team one, and a team's second approver is not weakened.
- **Facts are not duplicated.** The instructions point to the single home of each fact (`REVIEW_CYCLE.md` "Where each fact is recorded"); they do not become a second copy of a decision (INT-26 S4).
- **Shipped text stays generic.** Text installed into other repositories carries no names or history specific to this repository. The example name `M. Kusanagi` is a neutral placeholder, not a real approver.
- **Both flavors from one source**, deterministic build, standard library only for any script (INT-22, INT-26).
- **Concise.** Instructions are short and numbered, in plain words, with no bare internal IDs (INT-26 S9, "Plan length"). The template must stay readable when filled.
- **No outward action without the owner.** Editing a live pull request, the GitHub ruleset or the workflow needs the owner's go-ahead.
- **No unverified claims about GitHub.** What GitHub does about self-approval is not stated until it is read from GitHub's documentation or the repository's settings.

## Scenario seeds

### S1 — I know what to do at each place I must act
**Who:** The owner or a second approver opening a pull request produced by the coordinator.
**Wants:** An **Instructions** block beside each human step, in the pull request, that says what to check, where to click or write and what to do if it fails.
**So that:** Finishing needs no process document, no chat and no guessing.
**We will know when:** Each tickable line, each name field and each table the human fills in has an instructions block in the pull request description; a person who has not read the process documents finishes every step from the description alone.
**Must never:** Leave a human step with no instructions, or put the instructions only in a template comment that is removed from the finished description.

### S2 — The CI line is split and says what to verify
**Who:** The owner confirming CI for the pushed commit.
**Wants:** The owner's worked example above: each workflow run on its own numbered line with its link, then numbered instructions (open the links, check success, write the approval, or tell the coordinator if a run failed), then the name field.
**So that:** The owner can check each run in turn and knows what a pass and a fail mean.
**We will know when:** The coordinator's CI result line for any pushed commit has that shape: one numbered line per run, an **Instructions** block with the pass step and the fail step, and a name slug.
**Must never:** Write the name for the owner, or tell the human to approve when a run is not `completed` with `success`, or lose the full commit hash.

### S3 — Every name and date field has a slug I can replace
**Who:** Anyone writing their name and date into the pull request.
**Wants:** A slug such as `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>` wherever a human's name and date go (CI **Confirmed by**, **Human confirmation**, and any other such field).
**So that:** The field to change is obvious and the answer has a known shape.
**We will know when:** Every human-written field in the pull request template holds a slug that starts with `<Insert` and ends with `>`; after the human replaces it, no `<Insert` text remains in that field.
**Must never:** Leave such a field blank, hold prose instead of a slug, or use different slug shapes that cannot be found by one search.

### S4 — A state cell says what to write
**Who:** The coordinator filling the ready-check table, and the human reading it.
**Wants:** The table to say, in the cell or the instructions under it, that the State cell holds exactly `met` or `missing` and the coordinator replaces the placeholder with one of them.
**So that:** Nobody wonders whether the header text `State (met / missing)` is the answer.
**We will know when:** After the coordinator fills the table, every State cell holds `met` or `missing` and nothing of the header remains; the instructions name both values.
**Must never:** Show a State cell that still reads `met / missing`, or mark a line `met` without evidence in the Evidence cell.

### S5 — The pull request explains GitHub's Approve review
**Who:** The owner who must satisfy the ruleset's one required approving review.
**Wants:** The pull request to say that GitHub's Approve review (the "Review changes" control on the pull request page) is a separate act from the description's rows and ticks, whether it is required, where to click, and what to do if GitHub does not allow it.
**So that:** The merge button is not a surprise, and the owner does not mistake a tick for an approval.
**We will know when:** The description has a numbered instruction for the Approve review that states it is separate, links the "Review changes" place, and says what to do when the control is unavailable (the answer comes from the owner's decision on the open question below).
**Must never:** Claim the tick in the description satisfies the ruleset, or claim GitHub allows or blocks self-approval without it having been read from GitHub's documentation or the repository's settings.

### S6 — An unfilled slug is caught, not merged
**Who:** The coordinator running the ready check, and the owner running `/phase-status`.
**Wants:** A pull request with any `<Insert ...>` slug still unreplaced to show as not ready or open.
**So that:** A missing name or date is found by a check, not by the owner reading carefully.
**We will know when:** The coordinator's report and `/phase-status` list each unreplaced slug by its field name; a pull request whose human fields are all replaced lists none.
**Must never:** Count a field with an unreplaced slug as met, or report the ready check as met while one is present.

### S7 — The agent never fills in the human's part
**Who:** The coordinator or any agent that writes or edits the pull request description.
**Wants:** To write the instructions, the evidence and the slugs, and leave every human field as the slug.
**So that:** The human act stays human (`human-confirms-closure`, "Plan approval").
**We will know when:** In a pull request the coordinator has filled, every human field still holds its slug until a person replaces it; the edit history of the description shows the person, not the agent, replacing it.
**Must never:** Fill a slug, write an approver's name or a date in a human field, tick a box, or write "approved" on a human's behalf.

## Out of scope
- Changing the GitHub ruleset on `main` (including the required review count), the CI workflow or merge settings. That is the owner's act on GitHub.
- Weakening or removing any ready-check line or the human-confirmation requirement.
- Changing the content of the review passes, severity or the reviewer's file (INT-21, INT-23).
- A graphical or GitHub-form UX (INT-24); the instructions are plain text in the description.
- Re-running or amending Phase 3 beyond what the plan for this intent states.
- Deciding the release number or releasing.

## Open questions
- **One slug format for every human field?** What: a single shape for all name-and-date fields, such as `<Insert Name of approver on Date of approval, ex. M. Kusanagi on Jan-01-2027>` with the label changed per field (for example `Name of confirmer on Date of confirmation`). Why: one search finds every unfilled field. Consequence if not: several shapes and gaps in detection. Recommendation: one shape, `<Insert <role> on <date label>, ex. <Name> on <Mon-DD-YYYY>>`, using the owner's date style. Who: the owner. Default: the recommendation.
- **Does the ready check treat an unreplaced `<Insert ...>` as missing?** What: whether the coordinator and `/phase-status` read a leftover slug as the line being missing. Why: S6. Consequence if not: a pull request can look ready with no name. Recommendation: yes, treat any `<Insert` text left in a human field as missing, and make `/phase-status` list it. Who: the owner. Default: the recommendation.
- **Self-approval in a solo repository.** What: the ruleset requires one approving review (`docs/process/BRANCH_RULES.md`), and the owner is the only person. Why: GitHub may refuse an approval from the pull request's author, and nothing says what to do then. Consequence if not decided: the instructions for the Approve review cannot say what to do on failure. This intent does not assert the answer. Recommendation: the planner reads GitHub's documentation and the repository's settings first, and the owner then chooses between documenting the existing route (for example a bypass the owner already holds), a second account, or changing the ruleset, which is the owner's act and out of scope here. Who: the owner, after the planner reads the sources. Default: document what is found and ask.
- **Should the instructions also cover the plan's **Approved by**, the **Amendment approved by** line and the intent's **accepted_by**?** What: the same slug and an instructions block for those lines. Why: they have the same problem, a human writes name and date with no prompt. Consequence if not: the owner is stopped again at the next human line. Recommendation: yes, in the same plan, with the slug in the templates and the agents leaving it as it is; the planner and the `coordinator` still never fill it in. Who: the owner. Default: the recommendation.
- **Where does the instruction text live so it is not deleted?** What: the template's HTML comments are removed from the finished description, so instructions must be visible text, not comments. Why: S1. Recommendation: visible **Instructions** lines in the template, kept in the finished description and deleted by the human only after acting (or left in place). Who: the owner. Default: the recommendation.
- **Do the instructions ship in the bundle for every installing repository, or only in this repository?** Recommendation: ship them in the bundle, worded generically, since every repository that installs the bundle has the same human steps. Who: the owner. Default: the recommendation.
- **Which release carries this?** Recommendation: a separate phase after Phase 3's pull request is merged, so the pull request in hand is not held. Who: the owner. Default: the recommendation.
