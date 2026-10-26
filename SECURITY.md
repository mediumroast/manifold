# Security policy

## Reporting a vulnerability

Please report suspected vulnerabilities **privately**. Use **Report a vulnerability** under this repository's **Security** tab (GitHub private vulnerability reporting). Please do not open a public issue or pull request for a suspected vulnerability.

Include what you found, the version or commit, steps to reproduce or a proof of concept, and the impact you expect.

## What is in scope

The base bundle includes an installer that writes files into repositories you point it at, and agent instruction files that tools read. Examples of in-scope problems:

- the installer writing or deleting outside the target directory
- the installer overwriting or removing a file the user modified
- a release ZIP whose contents do not match the published checksums
- build or CI tampering that could change a release

## Supported versions

Only the latest release is supported.
