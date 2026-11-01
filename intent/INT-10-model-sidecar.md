---
id: INT-10
title: A model sidecar that speaks MCP
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, sidecar, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A model sidecar that speaks MCP

## Problem
Planned features need a language model: writing an intent with help, and bringing pages in line with their sources. The server deliberately does not call models, and putting provider code, keys and prompts inside it would break that. People also differ on which model they may use: some use public foundation models, some need a private model on their own network. Without one shared piece, each feature would solve this separately.

## Proposed outcome
A separate sidecar process that exposes model-backed capabilities as MCP tools. The Python server calls it as an MCP client. It supports Anthropic models, Ollama, and any host that offers an OpenAI-compatible API. Keys live only in the sidecar's environment. New capabilities are added as new tools. The sidecar's tools form a published contract, so a different sidecar (for example a commercial one) can replace it.

## Affected users and systems
- **People who use model-assisted features,** and administrators who choose providers.
- **The Python server,** which learns only how to call an MCP tool on a configured sidecar.
- **Authors of other sidecars,** who implement the contract.
- **The intent editor and wiki reconciliation,** which depend on it.

## Constraints
- **The core stays model-free.** No provider code, keys or prompts in the server.
- **Keys from the environment only,** never stored in the instance repository and never logged.
- **Show before sending.** What will be sent to a model is shown and confirmed at least once per session, since page content leaves the machine for hosted providers.
- **A published, versioned contract** for tool names, arguments, results and errors, tested like the server's own tools.
- **Works offline in tests.** Tests use fake providers; no network.
- **Degrades cleanly.** If the sidecar is down, model features are unavailable and the wiki is not.
- **Least access.** The sidecar gets only what it needs from the wiki, under an identity of its own.

## Scenario seeds

### S1 — Choose a provider
**Who:** An administrator.
**Wants:** To pick a public or a private model.
**So that:** Their data policy decides where content goes.
**We will know when:** Pointing the sidecar at an Ollama host, an OpenAI-compatible host, or Anthropic by settings alone makes the same tool work with each.
**Must never:** Send content to a provider the administrator did not configure.

### S2 — See what leaves
**Who:** A person using a model feature.
**Wants:** To see what will be sent before it is.
**So that:** They do not leak content by accident.
**We will know when:** The first model request of a session shows the text and destination and waits for a yes.
**Must never:** Send page content to a hosted provider without that confirmation.

### S3 — The sidecar is replaced
**Who:** A vendor offering their own sidecar.
**Wants:** To implement the contract.
**So that:** The product works with it unchanged.
**We will know when:** A different implementation passes the same contract tests and the server uses it with only a settings change.
**Must never:** Require a change in the core for a conforming sidecar.

### S4 — A key does not leak
**Who:** An administrator.
**Wants:** The provider key to stay secret.
**So that:** It cannot be read from logs or the wiki.
**We will know when:** Searching logs, the instance repository and error messages after a failed request finds no key.
**Must never:** Echo a key in an error or trace.

## Out of scope
- Features built on it (INT-12, INT-13).
- Training or fine-tuning models.
- A hosted service run by the project.

## Open questions
- Does the sidecar call back into the wiki, or are contents passed to it in arguments? (the product owner)
- How is a reply streamed to the interface through MCP? (the product owner)
- How is a sidecar declared in the instance settings? (the product owner)
- Which provider is the first one to be fully supported? (the product owner)
