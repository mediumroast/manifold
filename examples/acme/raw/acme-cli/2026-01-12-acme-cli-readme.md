# Acme CLI

Acme CLI is a command-line client for support staff.

    acme orders show <id>
    acme orders cancel <id>
    acme products list

It reads its API address and token from `~/.acme/config` and prints tables or JSON (`--json`).
