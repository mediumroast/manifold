# Installing the Manifold base bundle

## Requirements

Python 3.8 or newer (tested on 3.10 and 3.11; 3.8 compatibility is checked statically). The installer and the guard hook use only the standard library. No network access is needed. The agents' guard hook runs with `python3`, so `python3` must be on the PATH of the client that runs the agents (see "What each client enforces").

## Install

Unzip, then run the installer from inside the unzipped folder, pointing `--target` at your repository. The zip and its folder are named for the bundle's version; `<version>` stands for it below:

```bash
unzip manifold-base-<version>.zip
cd manifold-base-<version>
./install.sh --target /path/to/your/repo
```

That prints a plan and writes nothing. Read it, then add `--apply`:

```bash
./install.sh --target /path/to/your/repo --apply
```

Then review and commit the result in your repository:

```bash
cd /path/to/your/repo
git status
git add .claude docs/templates docs/process AGENTS.md CLAUDE.md .manifold
git commit -m "chore: add Manifold base bundle"
```

(`git commit` needs a git identity (`user.name` and `user.email`) to be configured already; if it is not, git says so.) (Stage only the paths the installer reported. `git add` stops with an error if a path does not exist, so drop any that were not created, and add `.github` if you installed a Copilot format. The guard's refusal log and the contents of the scratch folder are git-ignored by files the installer adds inside `.manifold/`.)

Next, open `AGENTS.md`. Outside the managed block the installer adds two empty sections for you: `Project commands` (an agent proposes your build and test commands and asks you to confirm them) and `Review process` (the repository type, solo or team, and the second approver for a team; agents read it and never fill it in). Then read `docs/process/HOWTO.md`, the guide to the whole cycle.

### Is it really installed? Finder hides dot-folders

The agents go in `.claude/` (and `.github/`), folders whose names start with a dot. **Finder on macOS hides them**, so an installed or unzipped bundle can look as if nothing arrived. Check in a terminal:

```bash
ls -la /path/to/your/repo/.claude/agents
```

or press Cmd+Shift+. in Finder to show hidden files.

## Options

| Option | Effect |
|---|---|
| `--apply` | Write the changes. Without it the installer only shows its plan. |
| `--profile <name>` | Which roles to install: `build` (default; a product repository), `quality` (a separate repository for behavior scenarios) or `single` (everything in one repository; prints a warning that verification is not independent). Profiles accumulate: installing `quality` after `build` makes the repository `single`. |
| `--format <list>` | What to install: `claude`, `copilot`, `skills` (experimental), `both` (claude and copilot), `all`, or a comma list such as `claude,skills`. Default `claude`. |
| `--skills-dir <path>` | Where skills are installed, relative to the repository. Default `.claude/skills`. Remembered for later runs. |
| `--allow-overlap` | Install even if the repository already has agents or skills for the same roles (for example `acme-planner`), or if the install would leave both agents and skills for the same roles. Without it, `--apply` refuses, because two entry points for one role can confuse routing. |
| `--no-instructions` | Do not add the managed block to `AGENTS.md` / `CLAUDE.md`. |
| `--force` | Replace files you modified. The old versions are copied to `.manifold/archive/<timestamp>/` first. |
| `--status` | Compare installed files with the manifest (ok, MODIFIED, MISSING). |
| `--uninstall` | Remove the files that are unmodified since install, and the managed block. `AGENTS.md` and `CLAUDE.md` are removed too, but only if the installer created them and nothing of yours is in them; if either holds your content, both are kept. `.manifold/guard-log.jsonl` (evidence) and your `.manifold/guard-allow.json` are kept. Add `--apply` to do it. |

Exit status: `0` success, `1` error, `2` finished but some files were skipped because you had modified them.

## What the installer will and will not do

- It **creates** files that do not exist.
- It **updates** a file only if it is byte-for-byte what a previous install wrote (you have not touched it).
- It **skips and reports** a file you have edited, or that already existed and was not installed by this bundle. Use `--force` to replace it; your version is archived first.
- It edits `AGENTS.md` (or `CLAUDE.md`, if that is the file you have) **only between its own markers**, `<!-- manifold:begin v=1 -->` and `<!-- manifold:end -->`. Everything outside the markers is yours. If neither file exists it creates `AGENTS.md` and a `CLAUDE.md` that imports it.
- It adds empty **Project commands** and **Review process** sections outside the markers, once.

Besides the agents and templates, it installs these files in every profile: the guard hook `.manifold/hooks/guard.py`, the scratch folder `.manifold/scratch/` (with its own `.gitignore`), `.manifold/.gitignore` (which keeps the local refusal log `.manifold/guard-log.jsonl` out of git), the procedures and guide in `docs/process/` (`REVIEW_CYCLE.md`, `BREACH_PROCEDURE.md`, `HOWTO.md`), and, with a Copilot format, `.github/hooks/manifold-guard.json`. The README has the full table.

## What each client enforces

The agents' rules say that files are created with the client's Write or Edit tool (or from a snippet written to `.manifold/scratch/` and run), not from the shell, and that each agent ends its report with a "Rule exceptions" line. The guard hook turns the shell rule, the write limits of the `reviewer` and the `coordinator`, and the protection of the guard and the agent definitions into refusals at the tool call. Whether a refusal happens depends on the client:

| Client and format | Does the hook run? |
|---|---|
| Claude Code, `claude` format | Yes, as a `PreToolUse` hook in each agent's definition. The vendor documentation says per-agent hooks run when the agent is started as a subagent and when it runs as the main session through `claude --agent <name>`. A plain main session with no agent selected is not covered, and neither are agents that come from a plugin: there the rules are instruction only. If `python3` or `.manifold/hooks/guard.py` is missing, the agent's Bash, Edit and Write calls are blocked rather than allowed. |
| GitHub Copilot, `copilot` format | The installer adds `.github/hooks/manifold-guard.json`. The vendor documentation describes hooks that can deny a tool call, but whether VS Code Copilot Chat runs this file, how it passes the tool and the agent's name, and what exit code it honors are unverified: confirm by trying a refused command and looking for the refusal. Until then treat Copilot as **instruction only**. Because the agent's identity is unverified, the write limits for the `reviewer` and the `coordinator` may not apply there. |
| Agent Skills, `skills` format | No hook ships with a skill. Instruction only. |

**Instruction only** means: nothing refuses the breach, but the same rule, the same sanctioned route and the same "Rule exceptions" report line are in the agent's instructions in every format, and the `coordinator` (or you) compares that line with the diff afterwards (see `docs/process/BREACH_PROCEDURE.md`). The hook also has stated limits, even where it runs: it matches commands and does not read a script that writes when it is run from a file. They are listed at the top of `.manifold/hooks/guard.py`. None of this has been recorded in a live client yet; the capability record behind it is `docs/agents/harness-capabilities.md` in the Manifold source (not installed).

To check that the hook runs, from your repository's root with the Claude format installed, send it a command it must refuse (this adds one line to `.manifold/guard-log.jsonl`):

```bash
echo '{"tool_name":"Bash","tool_input":{"command":"echo x > f"}}' | python3 .manifold/hooks/guard.py --client claude; echo "exit $?"
```

Expected: a line starting `Refused by the Manifold guard (rule no-heredocs)` and `exit 2`. This checks the script, not that your client calls it.

### Granting an exception

Only a person grants one. A blocked agent stops, says what it tried and what it needs, and asks. To allow a command, add an entry to `.manifold/guard-allow.json` by hand (the file is a JSON list; the guard refuses an agent's direct write to it):

```json
[
  {"pattern": "echo done > build/status\\.txt", "reason": "the build script needs this file", "granted_by": "Your Name", "date": "2026-11-07"}
]
```

`pattern` is a regular expression that must match the whole command. To lift a protected path, such as an agent definition, for a task, the entry also needs `"scope": "path"` and an `"expires": "YYYY-MM-DD"` date; the entry then holds through that date and grants nothing after it. Remove an entry when the work is done. Each use is logged as rule `exception-used` in `.manifold/guard-log.jsonl`, and the coordinator lists every entry and every use. `docs/process/BREACH_PROCEDURE.md` says how an exception is recorded.

## Without Python

Copy the folders under `payload/` into your repository by hand:

- `payload/claude/.claude/` to `<repo>/.claude/`
- `payload/copilot/.github/` to `<repo>/.github/` (Copilot users)
- `payload/skills/.claude/skills/` to `<repo>/.claude/skills/` (experimental skills)
- `payload/common/docs/` to `<repo>/docs/`
- `payload/common/.manifold/hooks/` to `<repo>/.manifold/hooks/`, and `payload/common/.manifold/scratch/` and `payload/common/.manifold/.gitignore` to the same places under `<repo>/.manifold/`. Without the guard script the Claude agents' Bash, Edit and Write calls are blocked.

You will not get the manifest, conflict detection, the `AGENTS.md` block or the two empty sections.

## Upgrading

Unzip the newer bundle and run the installer again. Files you have not modified are updated; files you have modified are left alone and listed.
