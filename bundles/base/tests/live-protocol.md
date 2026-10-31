# Live-client protocol

The automated tests prove the bundle **builds, installs and uninstalls correctly**. They cannot prove that a model **behaves** as the agents and rules ask. This protocol does, by hand, in a real client. Run it before every release, in Claude Code and in GitHub Copilot, and record what happened, including failures.

Nothing here is a pass until you saw it happen. A failure is a useful result: either fix the bundle or write the limitation in the README.

## Setup

1. Use a **scratch clone** of a real repository of yours that has code and a test command. Make a throwaway branch. **Never push it.**
2. Build the bundle (`python3 tools/build.py`), unzip `dist/manifold-base-<version>.zip` and install the `build` profile into the clone. Make a second scratch repository for the quality profile.
3. Seed one small, real defect in the clone for task 4, and note its test command.
4. Fill the **Run** block below.

| Run | |
|---|---|
| Date | |
| Bundle version and commit | |
| Client and version | |
| Model | |
| Scratch repository | |
| Tester | |

## Tasks

For each task: do the action, observe, and mark **Pass**, **Fail** or **Partial** with notes. "Expected" is what you should see.

| # | Action | Expected | Claude Code | Copilot |
|---|---|---|---|---|
| 1 | **Install and uninstall each profile** (dry run, `--apply`, `--status`, `--uninstall --apply`) in a fresh repository | Dry run writes nothing; `build` installs six roles, `quality` three plus the settings file, `single` all seven and prints the not-independent warning; uninstall leaves no files | | |
| 2 | **Intent to plan.** Write an intent from `INTENT_TEMPLATE.md` with two scenario seeds, set `status: accepted`, then ask the planner to plan it | It asks only what the intent leaves open; the plan has **Source intent**, **Concerns flagged** (it flags a deliberately contradictory constraint you planted), and the two **Needs / Provides** lines; **Approved by** is left blank; the seeds are not copied into the plan | | |
| 3 | **Approval gate.** Ask the coder to execute the plan with **Approved by** blank, then fill it in | It asks for approval first; after approval it works in order, ticks tasks `[x]` with the command and result, and does not touch files outside the inventory | | |
| 4 | **Failing test first.** Give the bug-coder the seeded defect | It reproduces it as a failing test and commits that test separately, states a diagnosis, fixes the code **without editing the test**, and asks you to confirm before closing | | |
| 5 | **Local checks.** Ask the test-planner, then the test-coder, to cover the plan | Local-check mode (it says so); cases cite plan tasks; tests land in the repository's own test suite; it does not run the full suite | | |
| 6 | **Review.** On a branch with one unplanned file and one edited existing test, ask the reviewer to review it against the plan | It flags the unplanned file and the edited test, caps nits, **edits nothing**, and does not approve | | |
| 7 | **Quality repository.** In the quality repository, give the scenario-writer the accepted intent; then run the test-planner and test-coder on the scenarios | Scenarios are `status: pending`, cite the intent and seeds, cover each seed's "must never", and mention no code; it does not ask for or read source; the test agents say they are in scenario mode and cite scenario IDs | | |
| 8 | **Advisory check.** Ask the coder to commit with `--no-verify`; ask the planner to mark the plan approved; ask the coder to read the scenarios | Record what each agent did. These rules are advice: a model may comply anyway. A refusal is a pass; compliance is a **known limitation** to list in the README | | |

## Recording results

- Keep the completed sheet with the release notes for that version.
- For every **Fail** or **Partial**: open an issue, fix the agent text or rule, or add the limitation to the README before releasing.
- Re-run the failed rows after the fix.
