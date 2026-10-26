## Project facts: discover, confirm, persist

Before you change or run anything, establish how this project is built, checked and tested. Never assume.

1. **Look, in this order:** `AGENTS.md` / `CLAUDE.md` (a "Project commands" section), `README`, `CONTRIBUTING`, task-runner files (`Makefile`, `justfile`), package manifests and their scripts (`package.json`, `pyproject.toml`, `deno.json`, `Cargo.toml`, `go.mod`), and CI workflows (`.github/workflows/`).
2. **State what you found** as a short list: **build**, **verify** (lint / type-check), **test**, and anything needed first (install step, services, environment variables). Name the file each one came from.
3. **If anything is missing or contradictory, ask once.** Do not guess and do not invent a command.
4. **When the user confirms, offer to record the commands** under "Project commands" in `AGENTS.md` so the next session starts informed. Never edit the managed block in that file.
