# Manifold: base bundle

Seven focused agents, the document templates they use, and a small library of **rules** ("don't do this, and here is what to do instead") that every agent carries. They give a product repository a consistent loop (intent, plan, build, local checks, review) and give a separate **quality repository** the means to judge product behavior independently. Drop it into any repository, in any language.

The roadmap is in [ROADMAP.md](../../ROADMAP.md).

## The roles

| Agent | Use it to | It does not |
|---|---|---|
| **planner** | Turn an intent (or a request, issue or bug report) into a sequenced `PHASE_<N>_PLAN.md` in `docs/plans/`. Given an intent it asks the analyst questions and **flags concerns it cannot resolve** | write production code, accept its own plan |
| **coder** | Execute an approved plan task by task, verifying each step and keeping the plan truthful | refactor outside the task, write behavior scenarios |
| **bug-coder** | Triage walkthrough notes (`WT_<NNN>_<slug>.md`), write a **failing test first**, then fix, root cause first | build new features, edit the failing test to make it pass |
| **reviewer** | Review a change against the plan, the intent and `REVIEW.md`; report findings by severity | edit, fix or approve anything |
| **test-planner** | Plan tests. In a product repository: the repository's own unit and integration checks, from a phase plan. In a quality repository: automation of behavior scenarios | write test code |
| **test-coder** | Implement the automated cases of a test plan | change production code, edit scenarios, run the full suite |
| **scenario-writer** | Expand an accepted intent's **scenario seeds** into behavior scenarios for the quality repository, from the intent and public behavior only | read the product's source code, approve its own scenarios |

## How the roles fit the loop

Every step ends by writing an artifact, and a human accepts it before the next step starts.

| Step | Who acts | Artifact | Who accepts |
|---|---|---|---|
| 1. Intent | A person with the AI as a drafting partner | `intent/INT-<n>-<slug>.md` from `INTENT_TEMPLATE.md`, with public **scenario seeds** | A person sets `status: accepted` |
| 2. Plan | planner | `docs/plans/PHASE_<N>_PLAN.md` (source intent, concerns flagged) | A person fills in **Approved by** |
| 3. Build | coder (with test-planner and test-coder for local checks) | The change, local unit and integration tests, a completion summary in the plan | The reviewer reports; a person approves |
| 4. Review | reviewer | Findings by pass and severity | A person decides |
| 5. Scenarios | scenario-writer, in the quality repository | `scenarios/*.md`, citing the intent and its seeds | A person marks them `approved` |
| 6. Behavior run | test-planner and test-coder (scenario mode), then people | A satisfaction report per seed, against thresholds | A person reads it |
| 7. Fix | bug-coder | Failing test, fix, triage row | The person who reported it confirms |

### Two layers of testing

- **Local checks** (unit, integration) live **in the product repository**, are written alongside the code, and are maintained there.
- **Behavior scenarios** (end-to-end user stories) live in a **separate quality repository**, are written from the intent rather than the implementation, and are never shown to the builder in full. The idea is the same as a holdout set in machine learning: the AI that builds the code must not be the AI that writes the tests that judge it, or the two can quietly agree with each other instead of with what the user wanted.

Four things have to be separate for that to be real:

| Separation | What it means | Who enforces it today |
|---|---|---|
| **Place** | Scenarios live in a different repository | Convention (this bundle's `quality` profile) |
| **Identity** | The build side cannot read the quality repository, and the reverse | **Repository permissions and separate credentials; the bundle cannot do this for you** |
| **Context** | Different agents and sessions on each side | Convention and the agent definitions |
| **Visibility** | The builder sees results, not scenarios | The visibility setting (below) and the rules |

### What the builder sees after a quality run

`visibility.level` in `.manifold/quality-settings.json`: **sealed** (only the score), **described** (default: the failing scenario's title, what was expected and what was observed, with no steps), or **open** (the whole scenario). If a scenario's full steps are ever revealed to fix a bug, it becomes a regression test in the product repository and is replaced in the quality repository.

### Thresholds are settings

The quality profile installs `.manifold/quality-settings.json`, which you own and may edit (the installer never overwrites a changed copy). Defaults, which are starting values to tune on real runs:

| Setting | Default |
|---|---|
| `satisfaction.minimum_overall` | 0.85 |
| `satisfaction.minimum_per_seed` | 0.70 |
| `failures.critical_max_rate` | 0.05 (strictly below) |
| `judge.minimum_confidence` | 0.85 |
| `trajectories.per_scenario` | 3 |
| `sampling.seed` | 42 |
| `visibility.level` | `described` |
| `gate.mode` | `report-only` |
| `burn.on_disclosure` | `true` |

Every report states the values it used. `gate.mode` is `report-only` until something can enforce a required check.

### Rules are advice, not enforcement

Agent definitions and rules are **instructions that a model is likely, not certain, to follow**. Nothing in this bundle stops an agent from breaking a rule. Where a rule must always hold, back it with something deterministic: branch protection, required reviews, separate credentials, or (in Claude Code) hooks. Each rule's *Enforce* line names the mechanism where one exists. Optional hooks are on the [roadmap](../../ROADMAP.md).

## Install profiles

| Profile | Install it in | Roles |
|---|---|---|
| `build` (default) | A product repository | planner, coder, bug-coder, reviewer, test-planner, test-coder |
| `quality` | A **separate** repository for behavior scenarios | scenario-writer, test-planner, test-coder |
| `single` | One repository that holds both (a way to start) | all seven, with a warning that verification is **not independent** |

```bash
./install.sh --target /path/to/product-repo --apply                    # build
./install.sh --target /path/to/quality-repo --profile quality --apply  # quality
```

The test agents work in two modes, decided by their input: from a phase plan (local checks, product repository) or from scenarios (quality repository).

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
| `.claude/agents/{planner,coder,bug-coder,test-planner,test-coder}.md` | The agents, in Claude Code format (default) |
| `.github/agents/{planner,coder,bug-coder,test-planner,test-coder}.agent.md` | The same agents in GitHub Copilot format (`--format copilot` or `both`) |
| `.claude/skills/{plan-change,execute-plan,fix-bug,plan-tests,write-tests}/SKILL.md` | The same roles as Agent Skills (`--format skills`, experimental; see below) |
| `docs/templates/{PHASE_PLAN_TEMPLATE,PHASE_TEST_PLAN_TEMPLATE,WT_TEMPLATE}.md` | Document templates the agents follow |
| `AGENTS.md` (managed block) | Which agents exist, where plans live, and the working rules. Created if you have neither `AGENTS.md` nor `CLAUDE.md` |
| `.manifold/` | A manifest of what was installed (with hashes), the license, and archived copies of anything replaced |

## What gets installed

| Path in your repo | Profiles | What |
|---|---|---|
| `.claude/agents/<role>.md` | by role | The agents, in Claude Code format (default) |
| `.github/agents/<role>.agent.md` | by role | The same agents in GitHub Copilot format (`--format copilot` or `both`) |
| `.claude/skills/<skill>/SKILL.md` | by role | The same roles as Agent Skills (`--format skills`, experimental; see below) |
| `docs/templates/INTENT_TEMPLATE.md`, `WT_TEMPLATE.md`, `PHASE_TEST_PLAN_TEMPLATE.md` | all | Intent (with scenario seeds), walkthrough notes, test plan |
| `docs/templates/PHASE_PLAN_TEMPLATE.md`, `REVIEW_TEMPLATE.md` | build, single | Phase plan; the review policy to copy to `REVIEW.md` |
| `docs/templates/SCENARIO_TEMPLATE.md`, `SATISFACTION_REPORT_TEMPLATE.md` | quality, single | Behavior scenario; run report |
| `.manifold/quality-settings.json` | quality, single | Thresholds, visibility and gate mode (yours to edit) |
| `AGENTS.md` (managed block) | all | Which agents exist, where documents live, and the working rules. Created if you have neither `AGENTS.md` nor `CLAUDE.md` |
| `.manifold/` | all | A manifest of what was installed (with hashes), the license, and archived copies of anything replaced. **Always inside the repository you install into, never in your home folder** |

## Using the agents

In Claude Code, agents in `.claude/agents/` are discovered automatically. Invoke one by asking for it by name in plain language, by typing `@agent-planner` and picking it from the list, or run a whole session as one with `claude --agent planner`. In GitHub Copilot Chat, choose the agent from the agent list.

A typical flow in a product repository:

1. **You**: write an intent from `docs/templates/INTENT_TEMPLATE.md` (or ask the planner to interview you), including scenario seeds. Set `status: accepted` when you are satisfied.
2. **planner**: "Plan intent/INT-1-claim-status.md." It asks what the intent leaves open, flags any concerns, and writes `docs/plans/PHASE_1_PLAN.md`. You review it and fill in **Approved by**.
3. **coder**: "Execute docs/plans/PHASE_1_PLAN.md." It works task by task, runs each acceptance check, and ticks the task off (`[x]`, or `[~]` if blocked) with the command and result.
4. **test-planner** and **test-coder**: write the repository's own unit and integration checks from the plan.
5. **reviewer**: "Review this branch against docs/plans/PHASE_1_PLAN.md." It reports findings; you decide.
6. **bug-coder**: after a walkthrough, or when a quality run reports a failure, it writes a failing test, fixes the code without touching that test, and asks you to confirm before closing.

And in the quality repository: **scenario-writer** expands the intent's seeds into scenarios; you approve them; **test-planner** and **test-coder** automate them against a deployed environment; a satisfaction report is written per seed.

## Agent Skills (experimental)

The same seven roles can be installed as [Agent Skills](https://agentskills.io), an open format for portable instructions that many tools support, instead of (or alongside) agent files:

```bash
./install.sh --target /path/to/your/repo --format skills --apply
```

| Skill | Same role as |
|---|---|
| `plan-change` | planner |
| `execute-plan` | coder |
| `fix-bug` | bug-coder |
| `plan-tests` | test-planner |
| `write-tests` | test-coder |
| `review-change` | reviewer |
| `write-scenarios` | scenario-writer |

- **Where they go.** `.claude/skills/<name>/SKILL.md`, the directory Claude Code reads. Other tools that support the standard may look elsewhere: check their documentation and pass `--skills-dir`. GitHub Copilot supports skills, but its repository path is not confirmed here.
- **How to run one.** In Claude Code, type `/plan-change` or ask for it by name.
- **How they differ from agents.** A skill runs inside your main conversation; an agent has its own context. A long planning session as a skill therefore uses your main context.
- **Pick one style per repository.** The installer refuses to add skills next to agents (or the reverse) unless you pass `--allow-overlap`, because two entry points for one role can confuse routing.
- **Status.** The rendered skills pass the official `skills-ref` validator and contain only fields defined by the specification, so they are portable. They have **not yet been tried in a live client**, which is why this format is experimental and the default stays `claude`.

## Rules

Each agent carries the rules that apply to its role, and the same rules are summarised in your `AGENTS.md`. Every rule states what not to do, **why**, and what to do **instead**: for example "stage only the files you changed", "never report tests as passing unless you ran them", "frontmatter must be the first line of the file". They live in [`rules/core/`](rules/core/), one small file each, so they are easy to review, change or extend.

## Customizing

**Tool restrictions are advice, not a sandbox.** In Claude Code the reviewer cannot edit files and the planning roles cannot use web tools, because the installed agent files list those tools as disallowed. That removes the tool from the agent itself. An agent can still hand work to a subagent that has the tool, and a model can choose to ignore a rule, so keep your client's own permission prompts on.

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
