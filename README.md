# Manifold

Consistent plans, test plans and walkthrough-driven bug triage from coding agents, in any repository.

Manifold is a toolkit for making AI coding tools such as Claude Code and GitHub Copilot behave consistently across repositories: they plan before they build, record evidence for what they did, stay inside the task's scope, and leave documents that people and other tools can read and reuse.

## What is in this release: v0.1.0, the base bundle

The first release is the foundation. It is self-contained, needs no server, and installs into any repository:

- **Seven agents:** `planner` (with an intent mode), `coder`, `bug-coder` (failing test first), `reviewer`, `test-planner`, `test-coder` and `scenario-writer`, in Claude Code and GitHub Copilot formats.
- **Two layers of testing.** Unit and integration checks live in your product repository. Behavior scenarios live in a **separate quality repository**, written from the intent rather than the implementation, so the AI that builds the code is not the AI that writes the tests that judge it. Install profiles (`build`, `quality`, `single`) set each repository up for its job.
- **Rules:** a small library of "don't do this, and do this instead" rules, each with the reason behind it. Every agent carries the rules that apply to its role. They are advice a model is likely, not certain, to follow; the bundle says plainly where deterministic enforcement is needed.
- **Templates:** intent (with scenario seeds), phase plan, test plan, walkthrough notes, review policy, behavior scenario and satisfaction report, installed to `docs/templates/`.
- **Quality settings:** numerical thresholds as defaults you can change.
- **An installer** that shows what it will do before it does anything, never overwrites a file you edited, and removes cleanly.
- **Agent Skills (experimental):** the same roles as portable [Agent Skills](https://agentskills.io).

See [`bundles/base`](bundles/base/README.md) for details and [ROADMAP.md](ROADMAP.md) for what comes next.

## Quick start

Download `manifold-base-<version>.zip` from the latest release, then:

```bash
unzip manifold-base-<version>.zip
cd manifold-base-<version>
./install.sh --target /path/to/your/repo            # shows the plan; writes nothing
./install.sh --target /path/to/your/repo --apply    # installs
```

It needs Python 3.8 or newer and uses only the standard library.

## What is coming

A wiki server and web interface for handing work from one repository's agents to another's, with an editor where a person and an AI write an intent together. They are not part of this release, and there are no dates. See [ROADMAP.md](ROADMAP.md).

## How this relates to the AI-native SDLC

Manifold follows the loop in Anthropic's [AI-native SDLC playbook](https://claude.com/resources/articles/the-ai-native-sdlc-playbook) (Louis Claxton): each stage commits an artifact, the next stage starts by reading it, and people hold the gates. The roles map onto it like this:

| Stage | Artifact | Manifold role |
|---|---|---|
| Plan | An intent (problem, outcome, constraints, scenario seeds) | `planner` in intent mode drafts; a person accepts |
| Design and build | A phase plan, then the diff | `planner` writes the plan; a person approves it; `coder` executes it |
| Test | Failing test first; evidence from literal command output | `bug-coder`, `test-planner`, `test-coder` |
| Review | Findings against the plan | `reviewer` (read-only, never approves) |
| Behavior check | Scenarios in a separate quality repository | `scenario-writer`, then the test roles in scenario mode |

Where Manifold departs (it is tool-neutral, spans many repositories, and cannot rely on Claude Code hooks, so its rules are advice) and what is missing is written down in [docs/plans/design/sdlc-playbook-alignment.md](docs/plans/design/sdlc-playbook-alignment.md). The playbook is a third-party document, linked and not copied.

## Status

v0.1.0 is a pre-release. The agents and skills pass the project's automated checks, including the official Agent Skills validator, and have been run end to end by hand in **Claude Code** and in **GitHub Copilot in VS Code**; see [tests/results](tests/results/README.md). The Agent Skills format is experimental.

The main finding: the guardrails hold on Claude Sonnet and are weaker on smaller models. Use Sonnet, and read [`bundles/base/MODELS.md`](bundles/base/MODELS.md) before choosing another model.

## Plans, tests and how we work

Manifold is developed in the open, with its own agents once they are ready for it. The design documents and the development plan are in [docs/plans](docs/plans/README.md). The live-client test protocol is in [tests/live](tests/live/README.md), and the results are in [tests/results](tests/results/README.md).

## Repository layout

| Path | What |
|---|---|
| `bundles/base/` | The base bundle: agents, rules, templates, installer, build tool and tests |
| `docs/plans/` | The development plan and design documents |
| `tests/live/` | The live-client protocol: step-by-step runs for Claude Code and GitHub Copilot, with the scripts that save and judge evidence |
| `tests/results/` | Summaries, results and findings of each live run |

## Contributing and security

See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Apache License 2.0. Copyright 2026 Mediumroast, Inc. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
