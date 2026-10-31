<!-- SPDX-License-Identifier: Apache-2.0 -->
# Run claude-code-1: Claude Code

| | |
|---|---|
| Client | Claude Code 2.1.312, terminal |
| Model | Claude Sonnet 5.5 |
| Bundle | v0.1.0 branch, commit `70615bf` (built before the fixes `df663f7` and `e9550a5`) |
| Scope | The whole protocol: installer, planning, execution, bug fixing, test planning and writing, review, scenarios in a quality repository, hold-out, and the dogfood task |
| Result | **58 Pass, 7 Partial, 2 Fail**, of 67 checks |

## What it showed

- The agents behave as written in a real client with a capable model: plans were gated on approval, the coder stopped at the task, the bug-coder wrote the failing test first, the reviewer found the planted weakened assertion and edited nothing, the scenario-writer declined to read the product's code, and the coder declined to read hold-out scenarios and offered "expected versus observed".
- It found real bundle bugs, now fixed: roles that declare `search` had `Bash` denied, so they could not list a folder (F4); the planner and the test roles did not carry every intent constraint into the plan or state their mode (F14, F16); and planners asked questions the repository could answer (F17).
- It found protocol bugs, now fixed: checks that could not fail because new files are untracked (F8, F15), duplicate check ids (F13), and a stale command for listing agents (F2).
- It confirmed a design limit: a tool denial binds the agent, not a subagent it delegates to (F10). The README says so.

## Open at the end of the run

F3 and F7 (protocol wording), F10 (documented), F11 (agent asked, protocol under-specified).

## Files

[`results.md`](results.md) one row per check. [`findings.md`](findings.md) what changed and why.
