<!-- SPDX-License-Identifier: Apache-2.0 -->
# Plans

How Manifold is planned and developed, in the open. Two kinds of document live here:

- **`design/`** holds the long-lived design documents: what we are building and why. They change by pull request and carry a status.
- **`PHASE_<N>_PLAN.md`** (in this folder) are execution plans written by the `planner` agent for a unit of work, approved by a person before the `coder` starts. They follow `bundles/base/templates/PHASE_PLAN_TEMPLATE.md`. The first ones will appear when this repository starts to use its own agents.

Plans are proposals until a person marks them approved. Nothing here has dates; the [roadmap](../../ROADMAP.md) carries status.

## Design documents

| Document | Status | What it answers |
|---|---|---|
| [development-plan.md](design/development-plan.md) | Active | How Manifold is developed, in what order, and how this repository uses its own agents |
| [testing-protocol.md](design/testing-protocol.md) | Active | How the bundle is tested in real clients, where the results are kept, and how a model is judged |
| [sdlc-playbook-alignment.md](design/sdlc-playbook-alignment.md) | Active | Where Manifold follows the AI-native SDLC playbook, where it departs, and what is missing |
| [independent-verification.md](design/independent-verification.md) | Partly built | Why the builder does not test itself, and the quality repository |
| [repository-family-and-stack.md](design/repository-family-and-stack.md) | Proposed | The repositories around Manifold, and the technology choice for the server and interface |

## Test results

Run summaries are in [`tests/results/`](../../tests/results/README.md).
