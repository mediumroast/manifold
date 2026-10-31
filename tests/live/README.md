<!-- SPDX-License-Identifier: Apache-2.0 -->
# Live protocol

The tooling that runs the base bundle in a real client and judges what it can from the evidence. Results are in [`tests/results/`](../results/README.md); the plan behind it is [`docs/plans/design/testing-protocol.md`](../../docs/plans/design/testing-protocol.md).

| File | What it is |
|---|---|
| `PROTOCOL-claude-code.md`, `PROTOCOL-copilot.md` | The step-by-step run for each client, from installing the client. Generated; do not edit |
| `RESULTS-*.md` | A blank results sheet per client, one row per check |
| `build_protocol.py` | The generator. Edit this, then run `python3 build_protocol.py` (`--results` also resets the blank sheets) |
| `setup.sh <claude\|copilot>` | Builds a fresh `~/manifold-live/<client>/` from nothing (bundle zip, product, quality and dogfood repositories). Running it again is the wipe |
| `lp.sh <client> ready \| reset <repo> \| evidence <label>` | Baseline, per-task reset, and evidence capture |
| `lp_verify.py` | Reads the saved chat logs and repositories and judges the checks it can |
| `fixtures/` | The planted intent, walkthrough, report and review-branch patch |

## What you need

- A Mac or Linux machine with Python 3.8 or newer, git and internet access; the client under test (Claude Code, or VS Code with GitHub Copilot Chat).
- `export MANIFOLD_REPO=<your clone of this repository, on the branch under test>`
- `export PRODUCT_SRC=<a product repository to copy>`

## About the sample product

The fixtures assume a product with the structure the protocol plants into: a Python MCP server under `mcp-server/` with a `wiki_freshness` tool and its tests. The reference runs used a private repository for this, so you cannot reproduce them byte for byte yet. To run the protocol against another product, replace the fixtures (`intent`, `walkthrough`, `review-target.patch`) and the file names in `build_protocol.py` with ones that fit it; the steps and the checks do not depend on that product.

The protocol is run by a person: the agents are driven in the client, and the scripts only save evidence and judge it. It does not run in CI.
