<!-- SPDX-License-Identifier: Apache-2.0 -->
# Findings: GitHub Copilot, Phase 1 test set

Each row is something the run showed that is not a plain pass or fail of a check. One sample; not a ranking.

| # | Seen at | What happened | Cause | Fix | Status |
|---|---|---|---|---|---|
| F1 | T.2 | Planned case A2 scans `docs/tls.md` for `-k`, `--insecure` and similar. Line 32 of that file is the warning that forbids them, so the test fails. | The planner specified a naive substring check with no allowance for text that names the words to forbid them. A flawed case, not a product defect. | Rephrase the warning, or narrow the test to instructions (not mentions). The owner left it red in this throw-away run. | Open (recorded, not fixed) |
| F2 | code | The `test-coder` reported the red test, did not weaken it and asked the owner to decide. | INT-25 S5 working as written. | None. | Closed |
| F3 | plan | The planner wrote its own text on the `Answer:` line of its question. The line is for the human. | The template does not say the line is human-only. | State in the template that only a human fills `Answer:`. | Open (template) |
| F4 | plan | The question asked (is a startup rule tested in `test_startup.py`?) could be answered by searching the repository. | The planner asked before looking. | Reinforce "look before you ask" for the questions section. | Open (agent text) |
| F5 | plan | Cases map to intent seeds, not to the tasks of `PHASE_1_PLAN.md`; the "before" plans mapped to tasks. | The new template asks for sources and seeds. | Consider a per-task column. | Open (template) |
| F6 | code | The coder ran pytest unsandboxed, because the VS Code sandbox blocks the git config the tests need. | A client sandbox limit, as in `copilot-1`. | Report to the owner as before. | Open (client) |
| F7 | evidence | `lp_verify.py` judged P.7 from the opening line only (it said CHECK), though the same reply went on to show coverage, gaps and a question. No guard log is in the evidence, so this run cannot say whether the hook ran. | The script reads the first text part, not the whole first reply; evidence capture does not copy the guard log. | Judge P.7 on the whole first reply; capture the guard log with the evidence. | Open (tooling) |
| F8 | plan | The planner paused before writing, showed its planned coverage and asked for confirmation, as the INT-25 text intends; it then wrote the plan on "write it" and, in the plan, wrote its own text on the question's `Answer:` line (F3). | INT-25 working as written, apart from F3. | None. | Closed |
