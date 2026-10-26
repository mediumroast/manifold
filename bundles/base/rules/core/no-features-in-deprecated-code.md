---
id: no-features-in-deprecated-code
title: Deprecated code
severity: medium
applies_to: coder, bug-coder
status: active
source: convention
---
## Rule
Do not add features to, or restructure, code the project marks as deprecated or superseded.

## Why
Effort spent there is thrown away, and it prolongs the life of code the project is trying to retire.

## Instead
Make the change in the replacement. If the replacement lacks something, raise it as a gap, or fix a defect in the old code only when users still depend on it and the user agrees.

## Enforce
- review: no feature diffs under paths marked deprecated
