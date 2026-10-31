# Satisfaction report: run1

**Run:** run1   **Date:** (example)
**Product under test:** protocol product (scratch copy of the product repository) at protocol-ready
**Environment:** staging
**Visibility level:** described   (from the settings)
**Judge:** none, hand-filled example   **Human spot-check:** protocol tester, 3 trajectories checked

## Thresholds used

| Setting | Value |
|---|---|
| satisfaction.minimum_overall | 0.85 |
| satisfaction.minimum_per_seed | 0.70 |
| failures.critical_max_rate | 0.05 |
| judge.minimum_confidence | 0.85 |
| trajectories.per_scenario | 3 |
| sampling.seed | 42 |

## Results per seed

| Seed | Scenarios | Trajectories | Satisfied | Fraction | Threshold | Status |
|---|---|---|---|---|---|---|
| INT-1 S1 | 4 (freshness-001, 002, 004, 005) | 12 | 11 | 0.92 | 0.70 | meets |
| INT-1 S2 | 3 (freshness-003, 004, 005) | 9 | 8 | 0.89 | 0.70 | meets |

**Overall satisfaction:** 0.93 (14 of 15 trajectories)   **Critical-failure rate:** 0.00 (0 of 15)   **Average judge confidence:** n/a (no judge ran)

## Failures

| Scenario | Expected | Observed | Critical? |
|---|---|---|---|
| Everything callers already get is unchanged, with days-behind added | Every field returned before the change is still returned with the same value | In one of three trajectories the existing last-updated field was missing from one entry | No |

## Disclosed scenarios

- None.

## Verdict

**Gate mode:** report-only
**Meets all thresholds:** yes
**Notes:** One non-critical failure in freshness-005. Scenarios freshness-004 and 005 belong to both seeds, so the overall figure counts them once (5 scenarios x 3 = 15 trajectories) while the seed rows count them in each. Because the gate is report-only, nothing is blocked. The run is made-up data for the protocol.
