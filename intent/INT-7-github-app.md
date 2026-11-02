---
id: INT-7
title: A GitHub App named manifold
author: Michael Hay
created: 2026-10-31
status: accepted
affects: [server, docs]
drafted_with: [claude-sonnet-5-5]
accepted_by: Michael Hay 2026-11-01
---

# Intent: A GitHub App named manifold

## Problem
Several planned features need to act on GitHub: writing to the instance repository without a local copy, creating a repository, opening pull requests, and turning a handoff into an issue. Today that would mean a personal access token tied to one person, with far more access than the job needs, no clear identity in the history, and a life that ends when the person leaves.

The server also needs to know which GitHub account a person is, so that people can obtain their credential by signing in and so that GitHub's own access rules can decide who may act for a component.

## Proposed outcome
A GitHub App called `manifold`, private at first, with only the permissions it needs. It can be created and installed by following a guided flow. It acts with short-lived tokens, and every action on GitHub is attributable to the App. An administrator can see what it may do, and can remove it.

The same App lets people sign in from the command line (device flow) and, later, from the browser. Signing in proves a GitHub identity once; the server then issues its own short-lived credential. Without the App, nothing in Manifold's protection changes (INT-1).

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
- **One App per company, created by the company.** Not a shared Manifold-owned App. Identity settings (client ID, secret, callback URLs) and automation settings (App ID, private key, installation ID) are separate configuration so the App can be split in two later. To be confirmed by a spike.
- **The App's private key stays with the server.** Agents never hold it. When an agent must act on GitHub directly, the server mints a narrowed token (one repository, minimum permissions).
- **Sign-in rule.** A person may sign in if they have read, triage, write, maintain or admin permission on the instance repository, as GitHub calculates it from all sources. Signing in grants the reader role only. The server refuses to turn on GitHub sign-in if the instance repository is public.
- **Either-rule for components.** A person may act for a component if they have a grant for it or write (including maintain) or admin permission on its repository, where the App can see that repository. Repository permission gives contributor on that component only, never registrar or admin. An explicit deny overrides both. If the repository cannot be checked, or GitHub cannot be reached, repository permission counts as not granted.
- **Protected mapping.** Only a human registrar can change a component's repository, owner or authority setting; the repository must belong to an allowed owner.
- **Revocation promise.** A change made inside Manifold takes effect on the very next request (INT-1). A change made on GitHub is looked up live before each write that relies on repository permission, and for reading it is picked up at a regular re-check, every five minutes by default and tunable by the administrator. If GitHub cannot be reached, repository permission is treated as not granted.
- **Sign-in lifetime.** A person's credential lasts 12 hours by default and at most 24, tunable within that range. On a failed re-check of their GitHub access, their credentials are revoked.
- **Every permission has a feature.** Repository Metadata (read) for permission checks; Contents and Pull requests (write) for INT-14, INT-15 and INT-16; Secrets (write) only if a later decision provisions credentials into repositories.
- **No GitHub token kept.** The person's GitHub token is used once to prove identity and then discarded.
- **GitHub.com only.** GitHub Enterprise Server is not supported; the project accepts that as known debt, since it is open source and cannot be tested here.

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

### S4 — Sign in from the command line
**Who:** A team member with access to the instance repository.
**Wants:** To run `manifold login`, approve in the browser, and get a credential for their AI client.
**So that:** They have their own identity without an administrator creating it.
**We will know when:** The person holds a reader credential that expires within a day, the history shows their GitHub account as the author, and a person without access to the instance repository is refused.
**Must never:** Store the person's GitHub token, or grant more than reader at sign-in.

### S5 — Either a grant or repository write is enough
**Who:** A person who pushes to a component's repository.
**Wants:** To act for that component without an administrator doing anything.
**So that:** Existing GitHub access is respected.
**We will know when:** The person can create a handoff from that component; after losing write on GitHub their next write for it is refused; a person with a grant but no repository write can still act; a person with an explicit deny cannot act even with write.
**Must never:** Let repository access give registrar or admin, or let anyone change a component's repository by editing a page.

### S6 — A component whose repository the App cannot see
**Who:** An administrator.
**Wants:** Components whose repository the App cannot see to still work.
**So that:** The App need not be installed everywhere.
**We will know when:** Such a component accepts grant-based access, and repository-based access is reported as unavailable, not silently allowed.
**Must never:** Treat "cannot check" as "allowed".

### S7 — Access lost on GitHub is lost here, within a stated time
**Who:** An administrator.
**Wants:** Someone removed from the repository on GitHub to lose access here.
**So that:** GitHub stays the place where access is decided.
**We will know when:** The removed person's next write that relies on repository permission is refused, and they can no longer read within the re-check interval.
**Must never:** Promise instant removal for reading, or treat an unreachable GitHub as permission.

### S8 — Claude Desktop is a known gap
**Who:** A user of Claude Desktop or claude.ai.
**Wants:** To know whether it works.
**So that:** They are not surprised.
**We will know when:** The guide says these clients connect from Anthropic's cloud and cannot reach a server on a private network, and points to INT-18.
**Must never:** Imply support that has not been tested.

## Out of scope
- Publishing the App to the marketplace.
- Company identity providers other than GitHub, and GitHub Enterprise Server.
- Claude Desktop and claude.ai access (INT-18).
- The browser sign-in screen (arrives with the new UI, INT-9).
- Acting as an MCP authorization server (INT-19).
- Webhook receivers.
- The features that use it (INT-6, INT-14, INT-15, INT-16).

## Open questions
- Which organization owns the App first, and can ownership be transferred later? (the product owner) Answer: We need to resolve this in planning with some pro/con thinking there isn't enough detail in the question to answer.
- Is the manifest flow enough to create it, or must the first one be made by hand? (the product owner) Answer: We need to resolve this in planning with some pro/con thinking there isn't enough detail in the question to answer. 
- Do any needed permissions require organization-owner approval that blocks the new company? (the product owner) Answer: I am unsure. I do know that we will need to create 1-2 repositories on behalf of the user.  The manifold repo and the aftertaste repo.  Org admins may need to assign users into either or both repos or at least assign a repo owner and delegate permissions to them.  This may not answer the question and likely requires planning and a spike.
- One App or two, after the spike? (the product owner) Answer: I presume we are talking one app create by mediumroast and then one app by the company using manifold or both. I'd opt for both because if the user allows the mediumroast app then they will make their lives easier. However for clear control then they can create and install their own following a guide and our example app.
- Does the repository-permission check work on repositories where the App is not installed, and what does it return? (answered by the spike)
- Should the installer provision a service credential into component repositories' Actions secrets (Secrets write)? The default is no. (the product owner) Answer: likely, no but put details in the planning doc and then we can decide then.
