---
title: "Acme Cli"
component: "acme-cli"
status: active
last_updated: 2026-01-14
owner: "Support tools"
summary: "Command-line client for support staff."
---

# Acme Cli

## Overview

_Sourced from `raw/acme-cli/2026-01-12-acme-cli-readme.md`. Synthesise and rewrite this section as needed._

# Acme CLI

Acme CLI is a command-line client for support staff.

    acme orders show <id>
    acme orders cancel <id>
    acme products list

It reads its API address and token from `~/.acme/config` and prints tables or JSON (`--json`).


**Repository:** https://example.test/acme/acme-cli

## Architecture

_To be completed. Describe the internal design: key modules, patterns, and tech stack. Update this section from `raw/acme-cli/` source documents._

## API contract

_To be completed. List endpoints, schemas, and data models. Mark breaking changes clearly. Update from `raw/acme-cli/` source documents._

## Integration points

_To be completed. Describe how this component communicates with other components. Link each component name to its wiki page once known._

## Implementation status

| Area | Status | Notes |
|---|---|---|
| Initial registration | ✅ Done | 2026-01-14 |
| Raw source docs | ✅ Embedded | See Sources section |
| Architecture documented | ⬜ Review embedded content | |
| API contract documented | ⬜ Review embedded content | |

## Changelog

- **2026-01-14** — Component registered.

## Known issues

_None recorded at registration._

## Deployment

_To be completed. Document how the component runs, required environment
variables, dependencies, and health checks._

## Sources

- [`raw/acme-cli/2026-01-12-acme-cli-readme.md`](../../raw/acme-cli/2026-01-12-acme-cli-readme.md) — readme document
