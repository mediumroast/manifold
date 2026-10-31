---
id: disclose-failures-as-behavior
title: Reporting failures
severity: medium
applies_to: test-planner, test-coder, scenario-writer
status: active
source: convention
---
## Rule
Report a failed scenario to the product side as behavior: the scenario's title, what was expected and what was observed, at the visibility level in the quality settings. Do not send the scenario file, its steps, its data or the test code unless the settings say open.

## Why
Disclosing the scenario turns a held-out check into something the builder can tune against.

## Instead
Describe the symptom in the user's terms. If the steps must be revealed, record the disclosure in the satisfaction report, so the scenario is turned into a regression test on the product side and replaced here.

## Enforce
- review: failure reports to the product side contain no scenario steps unless visibility is open
