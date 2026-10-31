<!-- SPDX-License-Identifier: Apache-2.0 -->
# Testing protocol

**Status:** Active.

The automated tests (`bundles/base/tests`) prove the bundle **builds, installs and uninstalls correctly**. They cannot prove that a model **behaves** as the agents and rules ask. The live protocol does, by hand, in a real client, and records what it found.

## 1. What is tested, and how

| Layer | What it shows | How |
|---|---|---|
| Automated | The bundle builds reproducibly, lints clean, installs and removes without touching edited files, and each rule and agent carries the text it should | `python3 -m pytest bundles/base/tests` and `python3 bundles/base/tools/build.py --check` |
| Live protocol | The agents behave as written, in a real client with a named model | [`tests/live/`](../../../tests/live/README.md): a step-by-step protocol per client, a script that saves evidence and a reader that judges what it can |
| Model matrix | How much the result depends on the model | Part 8 of the live protocol: short probes of the guardrails, repeated per model |

## 2. The live protocol

One protocol per client (Claude Code, GitHub Copilot in VS Code). It is generated from a single source so both clients get the same inputs. It runs the roles on two scratch repositories (a product and a separate quality repository) and a third scratch copy of this repository:

1. Install the three profiles and check first contact: the agents are visible and know their role.
2. Plan a change; execute an approved plan; fix a bug test-first; plan and write the repository's own tests; review a change that contains a planted problem.
3. Write behavior scenarios in the quality repository, plan and automate one, and audit a report with planted errors.
4. Ask a builder to read hold-out scenarios.
5. Dogfood: run the roles on this repository's own installer.
6. Model checks (the cheap version): the guardrail probes per model, in a run order that stops when the credit budget does.

The tester drives the client; a script saves the repositories, the chat logs and the verdicts it can decide. Each check ends as **Pass**, **Partial**, **Fail** or **Not run**, written by the reviewer of the evidence, not by the tester. Tester slips are recorded and excluded.

## 3. Results

Every run is kept under `tests/results/<run_id>/` (see the [index](../../../tests/results/README.md)): a summary with the client, models and bundle commit; the results sheet; and the findings list. Raw chat logs and diffs stay with the tester because they can contain local paths.

**Run ids** are the client and a sequence number (`claude-code-1`, `copilot-1`), so they carry no dates. A re-test of a changed bundle is a new run, not an edit of an old one.

## 4. Findings

A finding is anything the run showed that is not a plain pass or fail of a check. Each has a cause, a fix (in the bundle, in the protocol or in the client) and a status: *fixed*, *fixed locally*, *open* or *not a bug*. Failures become fixes with a test.

## 5. What a pass does not mean

- One run by hand is not a statistic. A model that passed once can fail the next time.
- A pass is for a version of the client, the model and the bundle. The summary names all three.
- The Copilot SDK target was looked at once; the results are for the Local target.
- Rules remain advice. The protocol shows how often a model follows them, not that it must.

## 6. Model policy

The recommendation, with the evidence behind it, is [`bundles/base/MODELS.md`](../../../bundles/base/MODELS.md). It is updated from the results folder after each run and must not claim a contrast that no run produced.

## 7. Open protocol work

- Re-run the guardrail probes on the hardened bundle (Sonnet, Haiku, MAI) and add the runs.
- Run the boundary probe: whether a client sandbox setting that denies reads to the quality path holds when the model ignores the rule.
- Add the Claude Code model matrix; only Copilot has one.
- Move the protocol runs into CI where they can run unattended (needs an API key and a budget).
