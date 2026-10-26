---
id: no-heredocs
title: Heredocs
severity: medium
applies_to: coder, bug-coder, test-coder
status: active
source: convention
---
## Rule
Do not write multi-line text or code through shell heredocs, and do not use heredoc-style blocks as comments or docstrings.

## Why
Heredocs break on some shells and systems, are easy to get wrong with quoting, and cost many tokens to emit and review.

## Instead
Create or edit the file with the file tools. If you need multi-line input to try something, put it in a test file or in a scratch folder such as `experiments/`. Use plain `#` or `//` comments, and docstrings only where the language expects them.

## Enforce
- review: no heredoc commands in the session transcript
