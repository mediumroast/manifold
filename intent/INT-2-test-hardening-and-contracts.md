---
id: INT-2
title: Test hardening and contract tests for the server
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, ci]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: Test hardening and contract tests for the server

## Problem
The server has a good set of unit tests and one smoke test, but they were written to protect a move, not to protect the product. The write paths, failure handling and the HTTP layer have thin coverage. Nothing pins down what each MCP tool promises its callers, so a refactor or a change of library could alter a tool's behavior and every test would still pass. The next pieces of work (a refactor, a new store, a new UI, a model sidecar) all depend on that promise staying put.

## Proposed outcome
The tools' behavior is written down as tests that outlive the code: for every tool, a recorded request and response that the server must keep reproducing, plus the official MCP conformance checks for the protocol itself. Gaps in the write paths and in error handling are closed. When a change breaks a promise to callers, a test says which tool and which field.

## Affected users and systems
- **Maintainers and contributors**, who need to change the server without fear.
- **Authors of clients** (the UI, the model sidecar, other MCP clients) who rely on tool names, arguments, results and errors.
- **The server's tests and the CI workflow.**

## Constraints
- **No network and no real git remote in the tests.** They run offline and finish in a time a contributor will tolerate on a laptop.
- **Recorded responses contain no real data.** They use the fictional example instance only.
- **A change to a recorded response is a visible, reviewed decision**, not an automatic update.
- **Only the entry module imports the web framework.** The rest of the server stays testable without it, and a test enforces the rule.
- **Flaky tests are not tolerated.** A test that fails at random is fixed or removed.
- **Python versions.** Tests run on the versions the server supports.

## Scenario seeds

### S1 — A changed tool result is caught
**Who:** A contributor who changes how a tool builds its result.
**Wants:** To be told right away if a caller-visible field changed.
**So that:** Clients are not broken by an accident.
**We will know when:** Renaming a field in one tool's result makes exactly that tool's contract test fail, naming the field.
**Must never:** Let a contract test pass because it was regenerated automatically in the same run.

### S2 — The protocol conformance checks pass
**Who:** A maintainer releasing a version.
**Wants:** Proof that the server speaks MCP correctly.
**So that:** Any compliant client connects.
**We will know when:** The official conformance suite runs in CI against a started server and passes, and a failure blocks the merge.
**Must never:** Skip the conformance run for a release.

### S3 — A failed write leaves the instance clean
**Who:** An agent whose write fails halfway (disk full, git refuses, stale etag).
**Wants:** The wiki to stay as it was.
**So that:** Nobody finds a half-made handoff.
**We will know when:** Tests that inject each failure show no partial files, no stray sidebar entry and no log line for the failed operation.
**Must never:** Leave an instance that fails its own health check after a refused write.

### S4 — The import rule holds
**Who:** A reviewer.
**Wants:** The framework confined to the entry module.
**So that:** The core can be tested and reused without it.
**We will know when:** A test fails if another module imports the web framework.
**Must never:** Allow the rule to be satisfied by a list of exceptions that grows unnoticed.

## Out of scope
- New product features.
- Test data sets beyond what the contract tests need (INT-3 covers those).
- Load and performance testing.
- Tests for a UI that does not exist yet.

## Open questions
- Which recording format should the contract tests use, and where should the recordings live? (the product owner)
- Is the official conformance suite stable enough to be a required check, or should it start as advisory? (the product owner)
- What coverage level, if any, should be a gate? (the product owner)
