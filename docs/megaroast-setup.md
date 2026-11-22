<!-- SPDX-License-Identifier: Apache-2.0 -->
# Megaroast setup guide

This is the organization owner's ordered checklist for the Megaroast test repositories and the GitHub App. It is written with placeholders so a later organization can reuse it:

- `<ORG>`: the organization.
- `<source-owner>` and `<source-repo>`: the account and repository the history copy comes from.
- `<repo-role>`: one of copy with history, standalone UI, example instance, holdout QA.
- `<new url>`: the new repository's address (never written out here).
- `<App-name>`: the App's name.
- `<INSTALLATION_ID>`: the installation's number, as the plan writes it.
- `MANIFOLD_APP_KEY_FILE`: the variable that names the key file (the name only, never the path).

No real repository name, organization name, App ID, installation ID, key, token or path belongs in this file. All repositories are private this phase.

## Rules

- No agent reads the holdout QA repository, the private key or any token.
- A ticked box is the owner's own act. The coder ticks none.
- Where a tick is mirrored: each step below carries its plan task (a `Plan:` line). When you tick a box here, you (or the coordinator, at your word in chat) also tick the `**Todo:**` of that task in `docs/plans/PHASE_4_PLAN.md` and the matching line in the pull request description of the checkpoint's pull request. Part 0 steps have no plan task; their ticks are mirrored in the pull request description only, and the note of the plan task that confirms the repositories says "created in Part 0". This guide's boxes are your working copy; the plan Todo and the pull request description stay the record.
- Secrets never go in chat, a log, a pull request or any file in a repository.

Anything this guide does not already know from the plan is marked "unverified: confirm with <source>".

## Part 0: create from scratch

Nothing in Part 0 is a plan task; it is the precondition of the checks in Steps 1 to 8.

- [ ] **Step 0a: record the organization's starting state.** `<ORG>` is owned by you and holds one stale, unrelated repository (you state it was made private, not deleted, and holds nothing needed). Confirm in chat that it is private: `gh repo view <ORG>/<stale-repo> --json visibility` (form verified in the plan). It is outside the four roles; the App is never installed on it. Not verified by the coordinator.
- [ ] **Step 0b: create the copy with history** in `<ORG>` as `<repo-role>` "copy with history" (not a GitHub fork, not a transfer; the source keeps its place). First create the empty private repository: `gh repo create <ORG>/<copy-name> --private` (verified with `gh repo create --help`: a name plus `--private` creates it without prompts; do not pass `--add-readme`, `--license` or `--gitignore`, so it stays empty). Then, in a folder outside every checkout:
  - `gh repo clone <source-owner>/<source-repo> <copy-name>` (form verified in the plan).
  - `git remote rename origin source` (unverified: confirm with `git remote --help`).
  - `git remote add origin <new url>` (unverified: confirm with `git remote --help`).
  - push `main` and the tags to `origin` (unverified: confirm with `git push --help`).
  - `git remote remove source` (unverified: confirm with `git remote --help`).
  - Check that the commit count and the tag count are the same on both sides, and that `gh repo view <ORG>/<copy-name> --json visibility` says private (form verified in the plan).
  - If the push is rejected: GitHub created the repository with a README or licence, so the histories diverge. Preferred: create it empty (above). Otherwise inspect what is on the remote first, then replace `main` with a force-with-lease push (flags unverified: confirm with `git push --help`). You decide this; no agent does it.
  - The source's other branches are not pushed (owner's answer: `main` and the tags only).
  - Risk: the history may hold secrets. Private is fine; a history scrub is required before any public release (V1), and is not part of this phase.
- [ ] **Step 0c: create the fresh standalone UI repository**, empty and private, no history from elsewhere: `gh repo create <ORG>/<name> --private` (verified with `gh repo create --help`).
- [ ] **Step 0d: create the fresh holdout QA repository**, empty and private: `gh repo create <ORG>/<name> --private` (verified with `gh repo create --help`). No builder creates, fills, clones or reads it; you (or the quality side) do all of it.
- [ ] **Step 0e: create the fresh example instance repository**, private. Run the default `./manifold init` for the instance, then push it to a new private repository. How the instance directory becomes a repository is unverified: confirm with `./manifold --help` and `docs/quickstart.md`.

## Steps 1 to 8

### Checkpoint 4: the test repositories

- [ ] **Step 1.** Plan: Task 28. Write the permission, visibility and date rows in `server/tests/datasets/SIGNOFFS.md` yourself: one row per repository that derives from the company repository (the copy with history, the standalone UI, and the example instance if its content derives from it), with source by role, owner, permission date, visibility and "nothing committed here". Private for every repository this phase; stop and tell the owner if any row says otherwise. Confirm in chat that each row is filled by you and the diff shows only table rows.
- [ ] **Step 2.** Plan: Task 29. Run `gh repo view <ORG>/<repo-name> --json visibility` once per working repository (the copy with history, the standalone UI, the example instance). Confirm in chat: "3 of 3 exist", each private, matching the Step 1 rows.
- [ ] **Step 3.** Plan: Task 30. Confirm in chat that the holdout QA repository exists, is private, and that no builder session has been given access to it. Nothing is read or cloned.
- [ ] **Step 4.** Plan: Task 31. Needs your private terms file at `~/.manifold/excluded_terms.json` (never committed, never printed; if it does not exist, stop). Clone the example instance to a scratch folder outside every checkout: `gh repo clone <ORG>/<repo-name> <scratch folder>` (form verified in the plan). Start the server against it as described in `docs/quickstart.md` (see that file; the start command is not copied here), then call `wiki_health` and `wiki_inventory_tool`, and run the scan over the clone with your private terms file. Confirm in chat: health is healthy, the number of components listed (you expect two), and the count of scan findings per kind (counts only, never quoted). No file is copied into this repository.

### Checkpoint 5: the GitHub App

- [ ] **Step 5.** Plan: Task 32. Read GitHub's documentation and record each fact with its source. The facts still "unverified: confirm with GitHub's documentation" are: the JWT's claims and signing algorithm (unverified: confirm with GitHub's guide on generating a JWT for a GitHub App); that Metadata read is always granted to an App and what it allows; whether the installation endpoint `GET /installation/repositories` needs only Metadata; how a lost private key is revoked and replaced; whether a private App can be transferred to another organization later. Confirm in chat that each fact has its source or "unverified".
- [ ] **Step 6.** Plan: Task 33. Create the private App. Settings path as the plan records it: `<ORG>` organization settings, Developer settings, GitHub Apps, New GitHub App. Name `<App-name>` (GitHub refuses a name that is taken; if refused, choose a fallback and say so in chat before anything else). Installability: "Only on this account". Webhook: Active unchecked; no callback URL, no user authorization, no device flow. Permissions: Metadata read-only and nothing else (no Contents, Pull requests, Issues, Administration or Secrets). Create the App, generate one private key, and save the file outside every repository at the path held in `MANIFOLD_APP_KEY_FILE`. Confirm in chat: the App exists and is private, the permission list shows Metadata read-only only, the name, and that the key file is outside every repository. No key, App secret or token appears in chat.
- [ ] **Step 7.** Plan: Task 34. Install the App on `<ORG>` with "Only select repositories": the copy with history, the standalone UI and the example instance, not the holdout QA repository. If an organization-owner approval step appears, record it. Confirm in chat: the installation's repository count is 3 and the holdout QA repository is not among them. Never write an App ID or installation ID in a committed file.
- [ ] **Step 8.** Plan: Task 35. On your own machine, using the key file named by `MANIFOLD_APP_KEY_FILE`, sign a JWT and exchange it at `POST /app/installations/<INSTALLATION_ID>/access_tokens`, with `permissions` limited to Metadata read. Make one request with the token that lists the repositories the installation can see, then discard the token (never write it to a file, chat or log). After one hour repeat the one request and expect a refusal. How to sign the JWT with the tools on your machine is unverified: confirm with GitHub's guide on generating a JWT for a GitHub App. Confirm in chat: the exchange succeeded, the listing shows 3 repositories, and the same token is refused after one hour (HTTP status only, no token).

When a step changes, change this guide and the plan task together.
