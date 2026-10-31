# Acme Engineering Wiki (example instance)

A small, fictional instance for trying Manifold and for testing it. It describes three
made-up components of an online store:

| Component | What it is |
|---|---|
| `acme-api` | the order service |
| `acme-web` | the storefront |
| `acme-cli` | a command-line client for support staff |

It holds the pieces a real instance has: `manifold.yaml` (the component registry), the schema
page (`wiki/CLAUDE.md`), component pages, an architecture overview, one decision record, a log,
raw source documents (including one shared across components), and three handoffs in
different states: one open, one in progress and one completed. One component page is
deliberately out of date, so the freshness check has something to report.

Everything here is invented. Nothing refers to a real company, product, person or host.

## Use a copy, not this folder

The server records every change as a git commit, and it only does so in a repository whose top
level is the wiki root. This folder sits inside the Manifold repository, so the server refuses
to commit here (it would otherwise write into Manifold's own history). Copy it out and make it
a repository of its own:

```bash
cp -R examples/acme ~/acme-wiki
cd ~/acme-wiki
git init -q && git add -A && git commit -q -m "Start from the Acme example"
```

Then point the server at the copy (`WIKI_ROOT` for the container, `CONTAINER_WIKI_ROOT` when
running the server directly) and see the server's README for the rest.
