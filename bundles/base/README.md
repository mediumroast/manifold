# Manifold: base bundle

Three focused coding agents, the document templates they use, and a small library of **rules** ("don't do this, and here is what to do instead") that every agent carries. Drop it into any repository to get a planner, a coder and a bug-fixer that work from the same plan, record evidence, and stay inside their scope.

| Agent | Use it to | It does not |
|---|---|---|
| **planner** | Turn a request, spec or bug report into a sequenced plan in `docs/plans/` | write production code |
| **coder** | Execute a plan task by task, verifying each step and keeping the plan truthful | refactor outside the task |
| **bug-coder** | Reproduce, diagnose, fix and regression-test a defect, root cause first | build new features |

It works in any language and any repository. Nothing is hard-coded about your stack: the agents discover how your project builds and tests, confirm it with you, and offer to record it.

## Install

You need Python 3.8 or newer (standard library only). It is tested on 3.10 and 3.11; 3.8 compatibility is checked statically.

```bash
unzip manifold-base-0.1.0.zip
cd manifold-base-0.1.0
./install.sh --target /path/to/your/repo            # shows the plan; writes nothing
./install.sh --target /path/to/your/repo --apply    # installs
```

The installer is a **dry run by default** and never overwrites a file you have edited. See [INSTALL.md](INSTALL.md) for options (Copilot format, status, uninstall, conflicts).

## What gets installed

| Path in your repo | What |
|---|---|
| `.claude/agents/{planner,coder,bug-coder}.md` | The agents, in Claude Code format (default) |
| `.github/agents/{planner,coder,bug-coder}.agent.md` | The same agents in GitHub Copilot format (`--format copilot` or `both`) |
| `.claude/skills/{plan-change,execute-plan,fix-bug}/SKILL.md` | The same roles as Agent Skills (`--format skills`, experimental; see below) |
| `docs/templates/{PHASE_PLAN_TEMPLATE,PHASE_TEST_PLAN_TEMPLATE,WT_TEMPLATE}.md` | Document templates the agents follow |
| `AGENTS.md` (managed block) | Which agents exist, where plans live, and the working rules. Created if you have neither `AGENTS.md` nor `CLAUDE.md` |
| `.manifold/` | A manifest of what was installed (with hashes), the license, and archived copies of anything replaced |

## Using the agents

In Claude Code, agents in `.claude/agents/` are discovered automatically. Invoke one by asking for it by name in plain language, by typing `@agent-planner` and picking it from the list, or run a whole session as one with `claude --agent planner`. In GitHub Copilot Chat, choose the agent from the agent list.

A typical flow:

1. **planner**: "Plan pagination for the search endpoint." It reads the code, asks about anything ambiguous, and writes `docs/plans/search-pagination.md`. You review it and set its status to `Approved`.
2. **coder**: "Execute docs/plans/search-pagination.md." It works task by task, runs each acceptance check, and ticks the task off with the command and result.
3. **bug-coder**: "Users see a blank page when the profile has no avatar." It reproduces the failure, states a diagnosis with evidence, fixes it, adds a regression test, and asks you to confirm before closing.

## Agent Skills (experimental)

The same three roles can be installed as [Agent Skills](https://agentskills.io), an open format for portable instructions that many tools support, instead of (or alongside) agent files:

```bash
./install.sh --target /path/to/your/repo --format skills --apply
```

| Skill | Same role as |
|---|---|
| `plan-change` | planner |
| `execute-plan` | coder |
| `fix-bug` | bug-coder |

- **Where they go.** `.claude/skills/<name>/SKILL.md`, the directory Claude Code reads. Other tools that support the standard may look elsewhere: check their documentation and pass `--skills-dir`. GitHub Copilot supports skills, but its repository path is not confirmed here.
- **How to run one.** In Claude Code, type `/plan-change` or ask for it by name.
- **How they differ from agents.** A skill runs inside your main conversation; an agent has its own context. A long planning session as a skill therefore uses your main context.
- **Pick one style per repository.** The installer refuses to add skills next to agents (or the reverse) unless you pass `--allow-overlap`, because two entry points for one role can confuse routing.
- **Status.** The rendered skills pass the official `skills-ref` validator and contain only fields defined by the specification, so they are portable. They have **not yet been tried in a live client**, which is why this format is experimental and the default stays `claude`.

## Rules

Each agent carries the rules that apply to its role, and the same rules are summarised in your `AGENTS.md`. Every rule states what not to do, **why**, and what to do **instead**: for example "stage only the files you changed", "never report tests as passing unless you ran them", "frontmatter must be the first line of the file". They live in [`rules/core/`](rules/core/), one small file each, so they are easy to review, change or extend.

## Customizing

The installed files are yours. Edit them freely: the installer will see the change and will not overwrite your version on an upgrade. To change the shared rules, edit or add files in `rules/core/` and rebuild.

## Building from source

```bash
python3 tools/build.py          # lint, render both formats, write dist/manifold-base-<version>.zip
python3 tools/build.py --check  # lint only
python3 -m pytest tests -q
```

The build is deterministic: building twice yields identical bytes.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Contributions are accepted under the Apache License 2.0 with a Developer Certificate of Origin sign-off.

## License

Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
