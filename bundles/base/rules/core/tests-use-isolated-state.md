---
id: tests-use-isolated-state
title: Test isolation
severity: high
applies_to: test-coder
status: active
source: convention
---
## Rule
Tests must not touch production data, and test files must not contain real credentials. Use isolated state (transaction rollback, a separate test store, in-memory mocks) and environment variables or fixture-generated tokens.

## Why
A test that writes to a real store corrupts it the first time it runs, and credentials in a test file end up in version control.

## Instead
Reuse an existing isolated fixture, or add one with a docstring in the central fixture file. Use a dedicated low-privilege fixture for permission cases, never an admin one.

## Enforce
- review: no connection strings, tokens or production paths in test files
