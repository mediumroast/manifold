# Installing the Manifold base bundle

## Requirements

Python 3.8 or newer (tested on 3.10 and 3.11; 3.8 compatibility is checked statically). The installer uses only the standard library. No network access is needed.

## Install

Unzip, then run the installer from inside the unzipped folder, pointing `--target` at your repository:

```bash
unzip manifold-base-0.1.0.zip
cd manifold-base-0.1.0
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
git add .claude docs/templates AGENTS.md CLAUDE.md .manifold
git commit -m "chore: add Manifold base bundle"
```

(Stage only the paths the installer reported; omit any that were not created.)

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
| `--uninstall` | Remove the files that are unmodified since install, and the managed block. `AGENTS.md` and `CLAUDE.md` are removed too, but only if the installer created them and nothing of yours is in them; if either holds your content, both are kept. Add `--apply` to do it. |

Exit status: `0` success, `1` error, `2` finished but some files were skipped because you had modified them.

## What the installer will and will not do

- It **creates** files that do not exist.
- It **updates** a file only if it is byte-for-byte what a previous install wrote (you have not touched it).
- It **skips and reports** a file you have edited, or that already existed and was not installed by this bundle. Use `--force` to replace it; your version is archived first.
- It edits `AGENTS.md` (or `CLAUDE.md`, if that is the file you have) **only between its own markers**, `<!-- manifold:begin v=1 -->` and `<!-- manifold:end -->`. Everything outside the markers is yours. If neither file exists it creates `AGENTS.md` and a `CLAUDE.md` that imports it.
- It adds an empty **Project commands** section outside the markers, which is where an agent will offer to record your build and test commands.

## Without Python

Copy the folders under `payload/` into your repository by hand:

- `payload/claude/.claude/` to `<repo>/.claude/`
- `payload/copilot/.github/` to `<repo>/.github/` (Copilot users)
- `payload/skills/.claude/skills/` to `<repo>/.claude/skills/` (experimental skills)
- `payload/common/docs/` to `<repo>/docs/`

You will not get the manifest, conflict detection or the `AGENTS.md` block.

## Upgrading

Unzip the newer bundle and run the installer again. Files you have not modified are updated; files you have modified are left alone and listed.
