# Manifold: base bundle

Eight focused agents, the document templates they use, a small library of **rules** ("don't do this, and here is what to do instead") that every agent carries, and a **guard hook** that refuses the most common rule breaches where the client lets it. They give a product repository a consistent loop (intent, plan, build, local checks, review, repair, re-review) and give a separate **quality repository** the means to judge product behavior independently. Drop it into any repository, in any language.

How the agents and the cycle work together is in [HOWTO.md](HOWTO.md), which is installed as `docs/process/HOWTO.md`. The roadmap (`ROADMAP.md`) is kept at the root of the Manifold source repository and is not part of this bundle.

## The roles

| Agent | Use it to | It does not |
|---|---|---|
| **planner** | Turn an intent (or a request, issue or bug report) into a sequenced `PHASE_<N>_PLAN.md` in `docs/plans/`, and amend a plan from a review. Given an intent it asks the analyst questions and **flags concerns it cannot resolve** | write production code, accept its own plan, fill in an approval line |
| **coder** | Execute an approved plan one checkpoint at a time, task by task, verifying each step and keeping the plan truthful | refactor outside the task, write behavior scenarios |
| **bug-coder** | Triage walkthrough notes (`WT_<NNN>_<slug>.md`), write a **failing test first**, then fix, root cause first | build new features, edit the failing test to make it pass |
| **reviewer** | Review a change against the plan, the intent and the review policy; write the findings by pass and severity to `docs/plans/REVIEW_PLAN_<N>.md` (the one file it writes) | edit code or the plan, fix findings, approve or block anything |
| **test-planner** | Plan tests. In a product repository: the repository's own unit and integration checks, from a phase plan and its intent, looking for gaps before it reads the existing tests and asking the human what it cannot decide. In a quality repository: automation of behavior scenarios | write test code |
| **test-coder** | Implement the automated cases of a human-approved test plan; it stops on a blocking question and leaves a failing check red | change production code, edit scenarios, run the full suite |
| **scenario-writer** | Expand an accepted intent's **scenario seeds** into behavior scenarios for the quality repository, from the intent and public behavior only | read the product's source code, approve its own scenarios |
| **coordinator** | Run the review-to-repair cycle by starting the other agents with named inputs, write the pull request's ready check, record breaches and list process gaps | do any agent's work, approve, move a pull request out of draft, merge |

## How the roles fit the loop

Every step ends by writing an artifact, and a human accepts it before the next step starts.

| Step | Who acts | Artifact | Who accepts |
|---|---|---|---|
| 1. Intent | A person with the AI as a drafting partner | `intent/INT-<n>-<slug>.md` from `INTENT_TEMPLATE.md`, with public **scenario seeds** | A person sets `status: accepted` |
| 2. Plan | planner | `docs/plans/PHASE_<N>_PLAN.md` (source intent, concerns flagged) | A person fills in **Approved by** |
| 3. Build | coder, one checkpoint at a time (with test-planner and test-coder for local checks) | The change, local unit and integration tests, a completion summary in the plan | A person reads each checkpoint report, approves the test plan and answers its questions |
| 4. Review | reviewer, in its own session | The review document `docs/plans/REVIEW_PLAN_<N>.md`: findings by pass and severity | A person decides what to repair, defer or reject |
| 5. Amendment | planner | A `## Review amendment (round <n>)` section in the plan: a repair checkpoint, what is not repaired and why | A person fills in **Amendment approved by** |
| 6. Repair | coder, not the agent that reviewed | The repair checkpoint's tasks, with failing tests first | A person reads the report |
| 7. Re-review | reviewer, in a new session | A new revision of the same review document | A person says the cycle is done |
| 8. Ready check | coordinator | The "Ready check" in the pull request, from `PULL_REQUEST_TEMPLATE.md` | A person confirms CI, moves the pull request out of draft and merges |
| 9. Scenarios | scenario-writer, in the quality repository | `scenarios/*.md`, citing the intent and its seeds | A person marks them `approved` |
| 10. Behavior run | test-planner and test-coder (scenario mode), then people | A satisfaction report per seed, against thresholds | A person reads it |
| 11. Fix | bug-coder | Failing test, fix, triage row | The person who reported it confirms |

The procedure for steps 4 to 8 is `docs/process/REVIEW_CYCLE.md`; [HOWTO.md](HOWTO.md) walks through it.

### Two layers of testing

- **Local checks** (unit, integration) live **in the product repository**, are written alongside the code, and are maintained there.
- **Behavior scenarios** (end-to-end user stories) live in a **separate quality repository**, are written from the intent rather than the implementation, and are never shown to the builder in full. The idea is the same as a holdout set in machine learning: the AI that builds the code must not be the AI that writes the tests that judge it, or the two can quietly agree with each other instead of with what the user wanted. Where no quality repository exists, the test planner's reading of the originating intent and its questions to the human act as a pseudo hold-out; that does not replace a quality repository.

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

### Choosing a model

Use Claude Sonnet for every role. Smaller models (Claude Haiku 4.5 and MAI-Code-1.1-Flash were tested) skipped the hold-out rule and other guardrails that Sonnet followed. [MODELS.md](MODELS.md) lists what was tested, what each model did, and the controls to add if you must use a smaller one.

### Rules are advice, not enforcement

Agent definitions and rules are **instructions that a model is likely, not certain, to follow**. The bundle adds one deterministic check, the **guard hook** (`.manifold/hooks/guard.py`), which a client runs before a tool call. It refuses a shell command that writes a file (heredocs, `sed -i`, `tee`, `>`, writes to `/tmp`), a write by the `reviewer` or the `coordinator` outside what each may write (the review document; the breach record and new draft intents), and a write to the guard, its log, the exception file or an agent definition. A blocked agent is pointed to the sanctioned route: the client's Write or Edit tool, or a snippet written to `.manifold/scratch/` and run.

What it does not cover:

- **It reads commands, not scripts.** A script that writes when it is run from a file is not read, so a snippet in `.manifold/scratch/` can write what the guard refuses to write directly. The limits are listed in the header of `.manifold/hooks/guard.py`; the coordinator compares each agent's "Rule exceptions" line with the diff and the guard log to find what got through.
- **Claude Code** runs the hook from each agent's definition: in subagents, and in a session started with `claude --agent <name>`. The ordinary main session and agents from plugins are not covered.
- **GitHub Copilot.** The installer adds `.github/hooks/manifold-guard.json` with `--format copilot`. Whether VS Code Copilot Chat runs it, and how it names the agent that is running, is unverified, so treat Copilot as instruction only until you have seen a refusal. The same rules, the same route and the same report line are in the agent text either way. [INSTALL.md](INSTALL.md) states this per client.
- **Agent Skills** carry no hook.

For rules that must always hold, back them with something outside the agent too: branch protection, required reviews, separate credentials. Each rule's *Enforce* line names the mechanism where one exists.

## Install profiles

| Profile | Install it in | Roles |
|---|---|---|
| `build` (default) | A product repository | planner, coder, bug-coder, reviewer, test-planner, test-coder, coordinator |
| `quality` | A **separate** repository for behavior scenarios | scenario-writer, test-planner, test-coder, coordinator |
| `single` | One repository that holds both (a way to start) | all eight, with a warning that verification is **not independent** |

```bash
./install.sh --target /path/to/product-repo --apply                    # build
./install.sh --target /path/to/quality-repo --profile quality --apply  # quality
```

The test agents work in two modes, decided by their input: from a phase plan (local checks, product repository) or from scenarios (quality repository).

## Install

You need Python 3.10 or newer (standard library only). The CI matrix tests it on 3.10 and 3.12; 3.11 was run by hand.

```bash
unzip manifold-base-<version>.zip
cd manifold-base-<version>
./install.sh --target /path/to/your/repo            # shows the plan; writes nothing
./install.sh --target /path/to/your/repo --apply    # installs
```

The installer is a **dry run by default** and never overwrites a file you have edited. See [INSTALL.md](INSTALL.md) for options (Copilot format, status, uninstall, conflicts).

## What gets installed

| Path in your repo | Profiles | What |
|---|---|---|
| `.claude/agents/<role>.md` | by role | The agents, in Claude Code format (default). Each carries the guard hook in its definition |
| `.github/agents/<role>.agent.md` | by role | The same agents in GitHub Copilot format (`--format copilot` or `both`) |
| `.github/hooks/manifold-guard.json` | all, Copilot format only | The guard hook for Copilot; whether VS Code Copilot Chat runs it is unverified (see INSTALL.md) |
| `.claude/skills/<skill>/SKILL.md` | by role | The same roles as Agent Skills (`--format skills`, experimental; see below). No hook |
| `.manifold/hooks/guard.py` | all | The guard hook script (standard library only). Every format installs it |
| `.manifold/scratch/` | all | The sanctioned place for a throwaway snippet an agent runs; git-ignored by a `.gitignore` inside it |
| `.manifold/.gitignore` | all | Keeps the guard's local refusal log `.manifold/guard-log.jsonl` out of git |
| `docs/process/REVIEW_CYCLE.md`, `BREACH_PROCEDURE.md`, `HOWTO.md` | all | The review-to-repair loop; how breaches are found and recorded; the guide to the whole cycle |
| `docs/templates/INTENT_TEMPLATE.md`, `WT_TEMPLATE.md`, `PHASE_TEST_PLAN_TEMPLATE.md`, `AGENT_FAILURES_TEMPLATE.md` | all | Intent (with scenario seeds), walkthrough notes, test plan, breach record |
| `docs/templates/PHASE_PLAN_TEMPLATE.md`, `REVIEW_TEMPLATE.md`, `REVIEW_PLAN_TEMPLATE.md`, `PULL_REQUEST_TEMPLATE.md` | build, single | Phase plan (with checkpoints); the review policy to copy to `REVIEW.md` if you want one; the review document the reviewer writes; the pull request description the coordinator fills in |
| `docs/templates/SCENARIO_TEMPLATE.md`, `SATISFACTION_REPORT_TEMPLATE.md` | quality, single | Behavior scenario; run report |
| `.manifold/quality-settings.json` | quality, single | Thresholds, visibility and gate mode (yours to edit) |
| `AGENTS.md` (managed block) | all | Which agents exist, where documents live, and the working rules. Created if you have neither `AGENTS.md` nor `CLAUDE.md`. Outside the block the installer adds two empty sections for you: `Project commands` and `Review process` (repository type and second approver); agents read `Review process` and never fill it in |
| `.manifold/` | all | A manifest of what was installed (with hashes), the license, and archived copies of anything replaced. **Always inside the repository you install into, never in your home folder** |

## Using the agents

In Claude Code, agents in `.claude/agents/` are discovered automatically. Invoke one by asking for it by name in plain language, by typing `@agent-planner` and picking it from the list, or run a whole session as one with `claude --agent planner`. In GitHub Copilot Chat, choose the agent from the agent list.

A typical flow in a product repository:

1. **You**: write an intent from `docs/templates/INTENT_TEMPLATE.md` (or ask the planner to interview you), including scenario seeds. Set `status: accepted` when you are satisfied.
2. **planner**: "Plan intent/INT-1-claim-status.md." It asks what the intent leaves open, flags any concerns, and writes `docs/plans/PHASE_1_PLAN.md`. You review it and fill in **Approved by**.
3. **coder**: "Execute docs/plans/PHASE_1_PLAN.md." It works one checkpoint at a time, task by task, runs each acceptance check, and ticks the task off (`[x]`, or `[~]` if blocked) with the command and result. It stops at the end of each checkpoint.
4. **test-planner** and **test-coder**: write the repository's own unit and integration checks from the plan.
5. **reviewer**: "Review this branch against docs/plans/PHASE_1_PLAN.md." It writes `docs/plans/REVIEW_PLAN_1.md`; you decide what to repair, defer or reject. Then the **planner** amends the plan from that file, you fill in **Amendment approved by**, the **coder** runs the repair checkpoint, and the **reviewer** re-reviews the same file.
6. **coordinator**: "Run the review cycle for docs/plans/PHASE_1_PLAN.md." It starts the agents above in turn, stops where you must decide, and writes the pull request's ready check. You move the pull request out of draft and merge.
7. **bug-coder**: after a walkthrough, or when a quality run reports a failure, it writes a failing test, fixes the code without touching that test, and asks you to confirm before closing.

And in the quality repository: **scenario-writer** expands the intent's seeds into scenarios; you approve them; **test-planner** and **test-coder** automate them against a deployed environment; a satisfaction report is written per seed.

## Agent Skills (experimental)

The same eight roles can be installed as [Agent Skills](https://agentskills.io), an open format for portable instructions that many tools support, instead of (or alongside) agent files:

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
| `coordinate-cycle` | coordinator |

- **Where they go.** `.claude/skills/<name>/SKILL.md`, the directory Claude Code reads. Other tools that support the standard may look elsewhere: check their documentation and pass `--skills-dir`. GitHub Copilot supports skills, but its repository path is not confirmed here.
- **How to run one.** In Claude Code, type `/plan-change` or ask for it by name.
- **How they differ from agents.** A skill runs inside your main conversation; an agent has its own context. A long planning session as a skill therefore uses your main context.
- **Pick one style per repository.** The installer refuses to add skills next to agents (or the reverse) unless you pass `--allow-overlap`, because two entry points for one role can confuse routing.
- **Status.** The rendered skills pass the official `skills-ref` validator and contain only fields defined by the specification, so they are portable. They have **not yet been tried in a live client**, which is why this format is experimental and the default stays `claude`.

## Rules

Each agent carries the rules that apply to its role, and the same rules are summarized in your `AGENTS.md`. Every rule states what not to do, **why**, and what to do **instead**: for example "stage only the files you changed", "never report tests as passing unless you ran them", "frontmatter must be the first line of the file". They live in [`rules/core/`](rules/core/), one small file each, so they are easy to review, change or extend.

## Customizing

**Tool restrictions are advice, not a sandbox.** In Claude Code the planning roles cannot use web tools, because the installed agent files list those tools as disallowed. That removes the tool from the agent itself. The reviewer and the coordinator do have an edit tool, because each must write one kind of file; what they may write is limited by the guard hook, where the client runs it, and by their instructions otherwise. An agent can still hand work to a subagent that has the tool, and a model can choose to ignore a rule, so keep your client's own permission prompts on.

**Hold-out data needs a real boundary.** The rule that keeps builders away from the quality side's scenarios is written text. In a live run, a smaller model read them anyway with shell `cat` and `find`, and the client's default sandbox did not block reads outside the repository. If the scenarios must stay hidden, deny reads to their path in your client's sandbox settings, or keep the quality repository on another account or machine.

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
