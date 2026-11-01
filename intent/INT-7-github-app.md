---
id: INT-7
title: A GitHub App named manifold
author: Michael Hay
created: 2026-10-31
status: draft
affects: [server, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by:
---

# Intent: A GitHub App named manifold

## Problem
Several planned features need to act on GitHub: writing to the instance repository without a local copy, creating a repository, opening pull requests, and turning a handoff into an issue. Today that would mean a personal access token tied to one person, with far more access than the job needs, no clear identity in the history, and a life that ends when the person leaves.

## Proposed outcome
A GitHub App called `manifold`, private at first, with only the permissions it needs. It can be created and installed by following a guided flow. It acts with short-lived tokens, and every action on GitHub is attributable to the App. An administrator can see what it may do, and can remove it.

## Affected users and systems
- **Administrators** who create, install and revoke the App.
- **The server and installer,** which use the App's identity.
- **GitHub organizations and repositories** where the App is installed.
- **The first test organization,** where it is created and exercised before any company uses it.

## Constraints
- **Least privilege.** Each permission is listed with the feature that needs it; permissions with no feature are not requested.
- **Private first.** It is not published to the marketplace and not installable by others until a deliberate decision.
- **No long-lived secrets in the instance repository.** The App's private key is kept outside it and read from the environment or a secret file.
- **Short-lived tokens only.** Installation tokens expire; nothing caches them past that.
- **The name.** `manifold` must be available to the owner; if not, a fallback name is chosen before anything is built.
- **What an App cannot do** (such as approving its own pull requests, or some repository-creation cases) is verified before any plan relies on it.

## Scenario seeds

### S1 — Create and install the App
**Who:** An administrator of a test organization.
**Wants:** To create the App and install it on one repository by following a guide.
**So that:** The App exists with exactly the permissions listed.
**We will know when:** After the flow, the App's settings page shows only the documented permissions, and it is installed only on the chosen repository.
**Must never:** Request a permission that no feature uses.

### S2 — Act as the App
**Who:** The server.
**Wants:** To act on GitHub as the App.
**So that:** Actions are attributable and tokens do not live long.
**We will know when:** A test action appears on GitHub as done by the App, and the token used has expired by the next day.
**Must never:** Write the private key or a token to a log or to the instance repository.

### S3 — Remove it
**Who:** An administrator.
**Wants:** To remove the App's access completely.
**So that:** Revoking is a clear, quick step.
**We will know when:** After uninstalling, the server reports that GitHub access is gone and stops trying, while local features keep working.
**Must never:** Keep acting with a cached token after the installation is removed.

## Out of scope
- Publishing the App to the marketplace.
- Sign-in of people through the App (single sign-on).
- The features that use it (INT-6, INT-14, INT-15, INT-16).

## Open questions
- Which organization owns the App first, and can ownership be transferred later? (the product owner)
- Is the manifest flow enough to create it, or must the first one be made by hand? (the product owner)
- Do any needed permissions require organization-owner approval that blocks the new company? (the product owner)
