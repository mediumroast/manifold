---
id: INT-6
title: An installer that takes you from nothing to a working instance
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docker, docs, svc_ctl]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: An installer that takes you from nothing to a working instance

## Problem
Getting a first instance running takes about ten manual steps: copy an example, make it a git repository, create a settings file, edit a path, start the container, check health, connect a client. Each step is a place to go wrong, and the quickstart already found three bugs this way. A second company adopting Manifold would repeat all of it. Creating the repository for the instance on GitHub is a further manual chore.

## Proposed outcome
One guided command, `manifold init`, takes a person from an empty folder to a running server with one registered component and a working handoff. It can optionally create the instance's repository on GitHub, private by default, through the GitHub API with the user's explicit approval. The local path works without GitHub or Docker knowledge beyond what the guide states.

## Affected users and systems
- **Anyone installing Manifold for the first time,** including a technical advisor setting it up for a company.
- **The setup script, the container files, the quickstart and operations guide.**
- **GitHub,** for the optional repository creation (needs the GitHub App from INT-7 for that part).

## Constraints
- **Two parts.** The local part (instance, settings, token, start, check) has no GitHub dependency. The GitHub part comes after the App exists.
- **GitHub through its API,** not through the command-line tool, so it works wherever the server will run.
- **Show before creating.** Nothing is created on GitHub without first showing the owner, name and visibility and getting a yes. Private is the default.
- **Secrets.** The token is generated, written with owner-only permissions, and never printed into a log or committed.
- **Safe to run twice.** Re-running does not damage an existing instance.
- **Clear failure messages** that say what to fix.

## Scenario seeds

### S1 — From nothing to a handoff
**Who:** Someone who has just cloned the project.
**Wants:** A running server and a first handoff by following one command's prompts.
**So that:** They see it work in minutes.
**We will know when:** On a machine with the stated prerequisites, the command ends with a healthy server, two registered components, and a handoff the person created and read back.
**Must never:** Leave a half-created instance if a step fails.

### S2 — Run it again
**Who:** The same person, a week later.
**Wants:** To run the installer again without losing anything.
**So that:** Mistakes are cheap.
**We will know when:** A second run detects the existing instance, offers to repair or stop, and changes nothing without a yes.
**Must never:** Overwrite a token or an instance's contents silently.

### S3 — Create the repository on GitHub
**Who:** An administrator who wants the instance on GitHub.
**Wants:** The installer to create a private repository and connect to it.
**So that:** The instance is backed up and shared from the start.
**We will know when:** Before creating anything the installer shows the owner, repository name and visibility; after a yes the repository exists, is private, and holds the initial instance.
**Must never:** Create a public repository unless the person typed that choice, or create anything without showing it first.

## Out of scope
- Production hardening beyond the security baseline (INT-1).
- A graphical installer.
- Creating the repositories of the components themselves.
- Installing the agent bundle into component repositories.

## Open questions
- Which operating systems must the installer support in the first version? (the product owner)
- Does it also create the separate quality repository, or only the instance? (the product owner)
- Does the GitHub part ship before or after the local part? (the product owner)
