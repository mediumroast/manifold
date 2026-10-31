<!-- SPDX-License-Identifier: Apache-2.0 -->
# Test results

Results of running the base bundle in real clients, by hand, with the live protocol in [`tests/live/`](../live/README.md). Raw chat logs and diffs are not kept here because they contain local paths; each run keeps its summary, its results sheet and its findings.

Run ids are the client and a sequence number, so they carry no dates. A re-test of a changed bundle is a new run.

| Run | Client | Models | Bundle | Result |
|---|---|---|---|---|
| [claude-code-1](claude-code-1/summary.md) | Claude Code 2.1.312 | Sonnet 5.5 | `70615bf` | 58 Pass, 7 Partial, 2 Fail, of 67 |
| [copilot-1](copilot-1/summary.md) | GitHub Copilot in VS Code (Local) | Sonnet 4.6, Haiku 4.5, MAI-Code-1.1-Flash | `8ed7b20` | 43 Pass, 10 Partial, 8 Fail, 6 Not run, of 67 |

Planned next: the guardrail probes on the hardened bundle for Sonnet, Haiku and MAI, and the sandbox-boundary probe (see [`docs/plans/design/testing-protocol.md`](../../docs/plans/design/testing-protocol.md)). The model recommendation that follows from these runs is [`bundles/base/MODELS.md`](../../bundles/base/MODELS.md).

## Adding a run

1. Run the protocol, saving evidence per task.
2. Create `tests/results/<client>-<n>/` with `summary.md`, `results.md` and `findings.md`.
3. Remove local paths, dates and names of people before committing, and run the repository checks.
4. Add a row above. If the run changes what the model page says, update it in the same pull request.
