---
id: no-secrets
title: Secrets
severity: high
applies_to: coder, bug-coder, reviewer, test-coder, scenario-writer
status: active
source: convention
---
## Rule
Never commit credentials, tokens, private keys or `.env*` files, and never paste them into chat output, logs or documentation.

## Why
Secrets in history persist even after the file is deleted, and anyone with read access can recover them.

## Instead
Refer to secrets by variable name, keep secret files in `.gitignore`, and if one was exposed, tell the user to rotate it.

## Enforce
- hook: a secret scanner in pre-commit or CI (optional, per project)
