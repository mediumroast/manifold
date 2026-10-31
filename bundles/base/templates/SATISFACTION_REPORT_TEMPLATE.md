# Satisfaction report: <run id>
<!--
  Template for the result of a quality run. Copy it to reports/<run id>.md in the QUALITY
  repository. The test agents and the human fill it in. State the settings that were used:
  a number without its threshold means nothing. Delete these comments when done.
-->

**Run:** <run id>   **Date:** YYYY-MM-DD
**Product under test:** <repository> at <commit or version>
**Environment:** <staging | other>
**Visibility level:** sealed | described | open   (from the settings)
**Judge:** <model>   **Human spot-check:** <name, number of trajectories checked>

## Thresholds used
<!-- Copy the values in force from .manifold/quality-settings.json. -->

| Setting | Value |
|---|---|
| satisfaction.minimum_overall | |
| satisfaction.minimum_per_seed | |
| failures.critical_max_rate | |
| judge.minimum_confidence | |
| trajectories.per_scenario | |
| sampling.seed | |

## Results per seed

| Seed | Scenarios | Trajectories | Satisfied | Fraction | Threshold | Status |
|---|---|---|---|---|---|---|
| INT-<n> S1 | | | | | | meets / below |

**Overall satisfaction:** <fraction>   **Critical-failure rate:** <rate>   **Average judge confidence:** <value>

## Failures
<!-- Described level: scenario title, what was expected, what was observed. No steps, data or test code. -->

| Scenario | Expected | Observed | Critical? |
|---|---|---|---|
| | | | |

## Disclosed scenarios
<!-- Any scenario whose full steps were revealed to fix a bug. Each graduates to a regression test in the product repository and is replaced here. -->
-

## Verdict
**Gate mode:** report-only | required-check
**Meets all thresholds:** yes | no
**Notes:**
