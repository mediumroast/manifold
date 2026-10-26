---
id: use-existing-environment
title: Environments
severity: medium
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
Use the project's existing virtual environment or toolchain. Do not create, reconfigure or reinstall one unless the user asks.

## Why
A second environment drifts from the first and makes results unreproducible; reinstalling can break a setup that works.

## Instead
Activate the environment the project documents. If it is missing or broken, report that and ask.

## Enforce
- review: no environment-creation commands appear without a request
