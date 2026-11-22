# Curated test data sets

Small instances for tests, built to be awkward. Everything under `curated/` is invented and
harmless. A test asks for one with the `dataset` fixture (or `loader.copy_curated`) and gets a
private git-backed copy; nothing in `curated/` is ever changed by a test.

| Set | What it holds |
|---|---|
| `messy` | dotted and look-alike slugs (`acme.io`, `acme-io`), a page with no frontmatter, two pages with one title, a stale page, a page in several scripts |
| `hostile` | pages whose text addresses an AI agent ("ignore your instructions", "call the tool ... with ..."); harmless test strings only |

A very long page is not committed. `loader.long_page(chars)` makes one of the stated size.

## The awkward cases

Dotted slug, look-alike slug, page with no frontmatter, duplicate title, stale page, very long
page, non-English text (more than one script), text aimed at an AI. A test checks that each one is
present (`test_the_sets_cover_every_awkward_case`).

## The real-data rule

Nothing real enters this repository without written permission from its owner and a scrub that a
person has checked. Until then only invented data is committed.

1. **Permission.** The owner of the data gives permission in writing. Without it, stop.
2. **Scrub.** Work on a copy outside this repository. Remove or replace every person's name, every
   host (use a name ending `.test`), every secret (keys, tokens, passwords) and every email address.
3. **Check.** Run `python server/tests/datasets/scan.py <folder> --terms-file <your term list>`.
   It reports emails, hosts not ending `.test`, `.example` or `.invalid`, token-shaped strings and
   every term of your private term list (a JSON list of strings kept outside every checkout, by
   default `~/.manifold/excluded_terms.json`; it is never committed or printed). The scan finds
   what it is shaped to find: a person then reads the scrubbed set, and the person who did is named
   in the sign-off.
4. **Record.** Add a row to `SIGNOFFS.md`: source, owner, permission date, who checked the scrub,
   scan result.
5. **The original is never committed**, and neither is a scrub nobody checked.

## Megaroast testbed

Real content for testing comes from outside this repository: the Megaroast organization on
GitHub holds four repositories, named here by role only:

- a fork (of a company's own repository),
- a standalone GUI (pulled out of that fork),
- a holdout QA repository,
- an example instance.

They are outside this repository. Nothing from them is committed here, no test reads them, and no
builder agent reads the holdout QA repository. The owner has permitted naming the repositories
but has not supplied names, so none appear here.
