# How to work with the Manifold agents

This guide is for the people in a repository that has the base bundle installed. It says which agent to use, what happens at each step of the cycle, what you must decide, and what the agents will not do for you. It links to the procedures instead of repeating them: the loop is `docs/process/REVIEW_CYCLE.md`, breaches are `docs/process/BREACH_PROCEDURE.md`, and each agent's own rules are in its definition (`.claude/agents/<role>.md`, or `.github/agents/<role>.agent.md` in the Copilot format). Where this guide and one of those differ, they win; tell a maintainer.

## When to use each agent

| Agent | Use it when | Do not use it when |
|---|---|---|
| `planner` | You have an accepted intent, an issue or a bug report that needs a sequenced plan; or a review needs to become a repair checkpoint | You want code written, or you expect it to approve its own plan |
| `coder` | A plan has **Approved by** filled in by a person; it works one checkpoint at a time | The plan is unapproved, or the work is large or unclear (plan it first); it is the agent that wrote the change and you want a review |
| `bug-coder` | A defect, a regression, a failing test or walkthrough notes: it finds the root cause, writes the failing test first, then fixes | The report is really a new feature |
| `reviewer` | A change or checkpoint is finished and you want it judged against the plan, the intent and the review policy, in a session of its own | The same session wrote the change; you expect it to fix, approve or block anything: it writes one file, the review document |
| `test-planner` | You want the repository's own unit and integration checks planned from a phase plan (or, in a quality repository, the automation of scenarios) | You want test code |
| `test-coder` | A test plan exists and its automated cases need writing | You want production code or scenarios changed, or the full suite run for you |
| `scenario-writer` | In the quality repository, an accepted intent has scenario seeds to expand into behavior scenarios | You are in the product repository (the `build` profile does not install it), or you want it to read the product's code |
| `coordinator` | You want the review-to-repair cycle run for a change, a pull request's ready check written, or the last run's breaches recorded | You expect it to do an agent's work, approve, move a pull request out of draft or merge |

The `build` profile installs every role except `scenario-writer`; `quality` installs `scenario-writer`, `test-planner`, `test-coder` and `coordinator`; `single` installs all eight and warns that verification is then not independent.

## The cycle in order

The sequence is the one in `docs/process/REVIEW_CYCLE.md`: review, `docs/plans/REVIEW_PLAN_<N>.md`, planner amendment, human approval, coder repair checkpoint, re-review of the same file. Each step ends by writing an artifact, and a person accepts it before the next step starts. Without a `coordinator`, or in a client that cannot start subagents, you start each agent yourself with the inputs that procedure names.

### 1. Intent
**What usually happens.** You write an intent from `docs/templates/INTENT_TEMPLATE.md`, with public scenario seeds, or ask the `planner` to interview you.
**What you do.** Set `status: accepted` when you are satisfied.
**What the agents will not do.** Accept an intent. The `coordinator` can only draft one, with status `draft`.

### 2. Plan
**What usually happens.** The `planner` asks what the intent leaves open, flags concerns it cannot resolve, and writes `docs/plans/PHASE_<N>_PLAN.md` from `docs/templates/PHASE_PLAN_TEMPLATE.md`, with tasks grouped into checkpoints.
**What you do.** Read it, answer the open questions, and send it back for changes if it is wrong.
**What the agents will not do.** The `planner` never fills in **Approved by**, and it does not implement the plan.

### 3. Approve the plan
**What usually happens.** The plan waits. The `coder` reads **Approved by** first and, if it is blank, asks "Is this plan approved to execute?" and stops.
**What you do.** Write your name and the date on **Approved by**.
**What the agents will not do.** Execute a plan that is not approved, even when told to execute it.

### 4. Build, by checkpoint
**What usually happens.** The `coder` works through one checkpoint, runs each task's check, ticks the task off with a note (command and result) and reports the project's gates with real counts. It then stops. The `test-planner` and `test-coder` write the repository's own checks from the plan.
**What you do.** Read the checkpoint report, then tell the `coder` to continue. If a fix would change a test that pinned the old behavior, it stops and asks you; a yes, in your words, is recorded in the plan before the test is edited.
**What the agents will not do.** Start the next checkpoint unasked, edit a test to make a run pass, work outside the plan's file inventory, or commit unless you ask.

### 5. Review
**What usually happens.** The `reviewer` runs in its own session (the `coordinator` starts it, or you do), reads the change, the approved plan with its notes, the intent, the review policy and the writer's "Rule exceptions" line, and writes `docs/plans/REVIEW_PLAN_<N>.md` from `docs/templates/REVIEW_PLAN_TEMPLATE.md`: findings by pass and severity, with counts.
**What you do.** Read the review document and decide what to repair, defer or reject.
**What the agents will not do.** Review their own change, edit anything but that one file, or approve or block the change.

### 6. Amendment
**What usually happens.** The `planner` reads the review file and adds a `## Review amendment (round <n>)` section to the plan: a repair checkpoint (each task names its finding), the findings not repaired with a reason, and open questions.
**What you do.** Read it and answer the open questions.
**What the agents will not do.** Fill in **Amendment approved by**, or turn Nits into tasks unless you ask.

### 7. Approval of the amendment
**What usually happens.** Everything waits; the `coordinator` says that it is waiting for you.
**What you do.** Write your name and the date on **Amendment approved by**, and record your answers in the plan. The plan's **Approved by** does not cover the amendment.
**What the agents will not do.** Start the repair before that line is filled in by a person.

### 8. Repair
**What usually happens.** The `coder` runs the repair checkpoint only: failing tests first, the fixes, then the gates with counts, and a stop. It is not the agent that reviewed.
**What you do.** Read the report and tell it to continue or stop.
**What the agents will not do.** Edit the review document (only the `reviewer` writes it), or start the next checkpoint unasked.

### 9. Re-review
**What usually happens.** The `reviewer` runs again in a new session, never the agent that made the repair, on the same review file and the new commit. The file gets a new revision: each earlier finding is shown as repaired, deferred or rejected with evidence, and new findings are added.
**What you do.** Read the new revision. If something Important is still open, go back to step 6.
**What the agents will not do.** Delete or rewrite an earlier finding.

### 10. Close
**What usually happens.** The cycle ends at a re-review with nothing open or only Nits. The limit is three runs (the first review is run 1), or until you say enough.
**What you do.** Say the cycle is done, or accept the remainder in writing. After the third run with an Important finding open, you decide.
**What the agents will not do.** Call the cycle done or run a fourth round on their own.

### 11. The ready check
**What usually happens.** The `coordinator` writes into the pull request description, from `docs/templates/PULL_REQUEST_TEMPLATE.md`, what exists and what is missing: a review of the final commit, each finding repaired, deferred or rejected, CI of that exact commit read, and approval as the `Review process` section of `AGENTS.md` says.
**What you do.** Read the CI result for that commit yourself and confirm it.
**What the agents will not do.** Say "ready" while a line is missing, or count a CI run for an older commit. The `coordinator` never moves a pull request out of draft.

### 12. Merge
**What usually happens.** The pull request waits for you.
**What you do.** Move it out of draft and merge it, once the check is met and you agree.
**What the agents will not do.** Merge, move a pull request out of draft, or push, open or comment on one without your go-ahead.

## The human gates

Only a person does each of these:

- accept an intent (`status: accepted`);
- approve a plan (**Approved by**);
- answer a stop of the `coder` when a fix would change a test that pinned the old behavior;
- decide what to repair, defer or reject from a review;
- approve a review amendment (**Amendment approved by**) and answer its open questions;
- say the cycle is done, or accept the remainder in writing;
- confirm a bug is fixed (a bug nobody can check yet stays `Pending human confirmation`);
- mark behavior scenarios `approved` in the quality repository;
- give a go-ahead for anything that leaves the machine: a push, a pull request or a comment on one, a posted issue;
- grant an exception to the guard (an entry in `.manifold/guard-allow.json`, below);
- read CI of the exact commit and confirm it;
- approve any text that changes how an agent behaves;
- move a pull request out of draft and merge it.

## Breaches

A breach is a command or an edit that broke a rule in `AGENTS.md`. It shows in three places:

- **A refusal.** Where the guard hook runs, a forbidden shell write or file edit is refused and the agent sees a message naming the rule. Each refusal appends a line to `.manifold/guard-log.jsonl` (time, rule, tool, agent type and the first 80 characters of the command; the file stays on your machine). A blocked agent stops, says what it tried and what it needs, and asks; it does not look for another way round.
- **A rule broken that nothing refused.** Every agent ends its report with a "Rule exceptions" line: `none`, or each exception (command, file, reason). A difference between that line and the diff, the commit log, the guard log or the transcript is a breach the agent did not report.
- **A review finding.** The `reviewer` lists what it compared under "Rule exceptions compared" in the review document.

The `coordinator` (or you, when there is none) records breaches by `docs/process/BREACH_PROCEDURE.md`: append-only entries in `docs/agents/<harness>-failures.md`, made from `docs/templates/AGENT_FAILURES_TEMPLATE.md`, counted per agent and per rule, reported ones apart from concealed ones. A breach that repeats becomes a draft intent for you to decide on.

To allow something the guard refuses, you add an entry to `.manifold/guard-allow.json` yourself (`pattern`, `reason`, `granted_by`, `date`; a path exception also needs `"scope": "path"` and an `expires` date), and remove it when the work is done. The procedure says how it is recorded. Agents must not edit that file, and the guard refuses a direct write to it.

## Solo or team

`AGENTS.md` has a `Review process` section that the installer adds empty and that you fill in: the repository type (solo, one maintainer, or team), the companion quality repository if any, and the second approver for a team. Agents read it and never write it. In a solo repository the cycle completes with your own decisions and no second approver is expected or invented. A team writes the second approver there, and the ready check uses what is written and nothing else. A `REVIEW.md` you already have stays the review policy; without one the `reviewer` uses its built-in defaults.

## What differs by client

The guard is the same file in every client. What differs is whether the client runs it. This list is limited to what `docs/agents/harness-capabilities.md` in the Manifold source records, read from the vendors' documentation; none of it has been recorded in a live run yet, so treat it as "no evidence yet".

- **Claude Code.** The guard is a pre-tool hook written into each agent's definition. The vendor documentation says such hooks run when the agent is started as a subagent and when it runs as the main session (`claude --agent <name>`). A plain main session with no agent selected is not covered, and neither are agents supplied by plugins: there the rules are instruction only.
- **GitHub Copilot.** With `--format copilot` (or `both`, `all`) the installer adds `.github/hooks/manifold-guard.json`. The vendor documentation describes hooks that can deny, but whether VS Code Copilot Chat runs this file, and how it names the running agent, is unverified: confirm by running it. Until you have, treat Copilot as instruction only. In particular the write limit for the `reviewer` and the `coordinator` may not apply there.
- **Agent Skills format.** The skills carry no hook. They are instruction only.
- **Instruction only** means the rules, the sanctioned route (create files with the client's Write or Edit tool, or write a snippet to `.manifold/scratch/` and run it) and the "Rule exceptions" line are in the agent text, nothing refuses a breach, and the `coordinator` or the `reviewer` finds it afterwards.
- **Where the guard runs it has limits.** It matches commands; it does not read a script that writes when run from a file. The limits are listed in the header of `.manifold/hooks/guard.py`.
- **Subagents.** In Claude Code the `coordinator` starts the other agents itself. In Copilot, subagents cannot start further subagents by default, per the vendor documentation; where the `coordinator` cannot start an agent it asks you to, and lists the inputs.

## How to start

1. Install: unzip the bundle and run `./install.sh --target /path/to/your/repo` (a dry run), then again with `--apply`. `INSTALL.md` in the unzipped folder has the options and what each client enforces.
2. Open `AGENTS.md`: fill in `Review process`, and confirm the build and test commands the first agent proposes under `Project commands`.
3. Look at what arrived: the agents in `.claude/agents/` (and `.github/agents/`), templates in `docs/templates/`, procedures and this guide in `docs/process/`, the guard in `.manifold/hooks/guard.py` and the scratch folder `.manifold/scratch/`.
4. Write your first intent, then ask the `planner` to plan it. Ask for an agent by name; the README, under "Using the agents", shows the other ways to start one.
5. To run a whole review cycle, ask the `coordinator`, for example: "run the review cycle for docs/plans/PHASE_1_PLAN.md".
