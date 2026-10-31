<!-- SPDX-License-Identifier: Apache-2.0 -->
# Independent verification

**Status:** Partly built. The quality profile, scenario-writer, scenario template, satisfaction report and quality settings ship in v0.1.0. Separate credentials, the scenario engine and a home for this project's own quality repository do not exist yet.

## 1. The problem

When the AI that writes code also writes the tests that judge it, tests can be rewritten to match the code, or the code can pass them trivially. A green run then says little. The remedy borrowed from published software-factory practice (Dan Shapiro's [five levels](https://www.danshapiro.com/blog/2026/01/the-five-levels-from-spicy-autocomplete-to-the-software-factory/), StrongDM's [factory principles](https://factory.strongdm.ai/principles)) is to judge behavior with **scenarios** that live outside the code, are written from the intent and not from the implementation, and work like a hold-out set. The measure is **satisfaction**: the fraction of observed paths through the scenarios that likely satisfy the user, not a boolean.

Where Manifold stops short of those sources: people still write intents, approve scenarios and plans, and review. The target is the point where human time moves from code to intent, scenarios and approvals.

## 2. Two layers of testing

| Layer | Lives in | Written by | Judges |
|---|---|---|---|
| Unit and integration checks | The product repository | `test-planner` and `test-coder` in local-check mode, from the phase plan | That the code does what the plan says |
| Behavior scenarios and their automation | A separate quality repository | `scenario-writer`, then `test-planner` and `test-coder` in scenario mode | That the product does what the user needs, as seen from outside |

## 3. Four separations

Documentation can ask for some of them; the rest needs infrastructure.

| Axis | Requirement | Today |
|---|---|---|
| Place | Scenarios live in a different repository | Convention and the `quality` install profile |
| Identity | Build agents cannot read the quality repository; quality agents cannot push to product repositories | Separate credentials. **Not provided by the bundle** |
| Context | Different sessions; the quality side does not inherit the builder's conversation | Agent definitions and rules |
| Visibility | The builder sees results, not scenarios | A rule, backed by repository permissions where available |

**What the live runs showed.** The hold-out rule held on Sonnet and failed on two smaller models, which read the scenarios through the shell with no prompt. In the tested setup the client's sandbox did not block those reads. So visibility is real only with a boundary the model cannot cross: deny reads to the quality path in the client's sandbox settings, or keep the quality repository on another account or machine. The bundle README says so, and the protocol has a probe to test the boundary.

## 4. Failures the builder may see

A quality run can report a failure to the builder without revealing the scenario. The settings choose how much is shown, from the scenario's identifier only, to a described failure (expected versus observed), to full text. The default is **described**. A scenario that was disclosed is marked as disclosed in the report and replaced.

## 5. The satisfaction report

One report per run: the thresholds used (they come from `.manifold/quality-settings.json`), a row per seed with scenarios, trajectories and the satisfied fraction, the overall figure, the failures, any disclosed scenarios, and a verdict. The gate is `report-only` until something can enforce a required check. The live protocol includes an audit of a report with planted errors; the test-planner found all three on Sonnet.

## 6. Roles by install profile

| Profile | Roles |
|---|---|
| `build` | planner, coder, bug-coder, reviewer, test-planner, test-coder (local-check mode) |
| `quality` | scenario-writer, test-planner, test-coder (scenario mode) |
| `single` | all of them in one repository, with a warning that verification is then not independent |

## 7. Next

- A quality repository for this project, and the scenario-to-test engine as a separate, generic kit.
- Layered credentials and one identity per role.
- Re-run the hold-out probe on the hardened bundle and with a sandbox boundary ([testing-protocol.md](testing-protocol.md)).
