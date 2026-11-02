<!-- SPDX-License-Identifier: Apache-2.0 -->
# TLS: HTTPS for the server

Without TLS, credentials and wiki content cross the network in clear text. The server has no TLS of its own; the **Caddy** container in front of it serves plain HTTP or HTTPS, chosen by one setting. Nothing here contacts a public certificate authority: the certificate comes from Caddy's own local authority, so the setup works offline.

## The setting

In `docker/.env.<environment>`:

| Setting | Meaning |
|---|---|
| `BIND_ADDRESS` | the address the host publishes on; `127.0.0.1` (loopback) by default |
| `MANIFOLD_TLS` | `off` (plain HTTP) or `on` (HTTPS) |
| `TLS_NAMES` | the names and addresses the certificate is made for, space separated, for example `localhost 127.0.0.1 192.168.1.5 wiki.example.test`; used when TLS is on |
| `ALLOWED_HOSTS` | extra `Host` values the server accepts, comma separated, for example `192.168.1.5:8686,wiki.example.test`; the same names your clients type |

`./svc_ctl.sh <env> init-env` sets `MANIFOLD_TLS=off` for a loopback `BIND_ADDRESS` and `on` for any other (give `BIND_ADDRESS=192.168.1.5 ./svc_ctl.sh production init-env`). To change it later, edit the file and `./svc_ctl.sh <env> restart`. `start` checks it:

- **plain HTTP on a non-loopback address is refused**, with the reason, unless you set `MANIFOLD_ALLOW_PLAIN_ON_NETWORK=yes` (in the file or the environment); then it starts with a warning you cannot miss. Do that only when the network is protected some other way.
- anything other than `off` or `on` is refused.

When TLS is on, Caddy serves `https://<name>:<PORT>` for every name in `TLS_NAMES`. A client that connects to an IP address sends no server name, so it gets the certificate of the first non-loopback IP address in `TLS_NAMES` (else the first IP address, else the first name); give people a name or that address.

## Trusting the certificate

Caddy creates a local certificate authority the first time it starts with TLS on. Its **root certificate** is in your data folder:

```
<DATA_DIR>/caddy/data/caddy/pki/authorities/local/root.crt
```

Copy that file (not the `.key` files next to it, which must stay private) to every machine whose clients should trust the server. **Never turn off certificate checking** (`-k`, `--insecure`, `NODE_TLS_REJECT_UNAUTHORIZED=0` or similar) to get around a trust error; fix the trust instead.

Checked here: `curl --cacert root.crt https://localhost:8686/health` answers `{"status":"healthy"}`, and the same request without `--cacert` fails. The steps for the clients below are the standard ways to add a trusted root and are **unverified**: they have not been run against this server. Confirm each one before relying on it, and tell us if it is wrong.

### Claude Code

Claude Code runs on Node.js, which reads extra trusted roots from `NODE_EXTRA_CA_CERTS` (**unverified** for Claude Code's MCP connections):

```bash
export NODE_EXTRA_CA_CERTS=/path/to/root.crt
MANIFOLD_TOKEN="$(cat /path/to/your/credential-file)" claude
```

Use an `https://` address in `.mcp.json` ([`examples/clients/claude-code-mcp.json`](../examples/clients/claude-code-mcp.json) shows the shape; change `http://localhost:8686/mcp` to your `https://` address).

### VS Code

VS Code uses the operating system's trusted roots. Add `root.crt` to the system store (**unverified** for the MCP connection): macOS, open it in Keychain Access and set *Always Trust* for SSL; Linux, copy it into the system certificate directory and run `update-ca-certificates` (Debian and Ubuntu); Windows is not supported by the host command. Then use an `https://` address in `.vscode/mcp.json` ([`examples/clients/vscode-mcp.json`](../examples/clients/vscode-mcp.json)).

### A browser

Import `root.crt` as a trusted authority (**unverified**): Firefox keeps its own list (Settings, Privacy and Security, Certificates, View Certificates, Authorities, Import); Chrome, Edge and Safari use the system store as above. Then open `https://<name>:8686/docs/`; the browser asks for a user name (any) and your credential as the password.

### Claude Desktop and claude.ai

Not supported yet ([INT-18](../intent/INT-18-claude-desktop-access.md)).

## Checking it

```bash
curl --cacert root.crt https://localhost:8686/health                          # {"status":"healthy"}
curl --cacert root.crt -o /dev/null -w '%{http_code}\n' https://localhost:8686/docs/        # 401: no credential
curl --cacert root.crt -H "Authorization: Bearer $(cat your-credential-file)" -o /dev/null -w '%{http_code}\n' https://localhost:8686/docs/   # 200
```

A plain-HTTP request to the HTTPS port is refused by Caddy. A request whose `Host` is not in `ALLOWED_HOSTS` (and not `127.0.0.1`, `localhost` or `[::1]` with the port) gets `421`.

## Your own certificate

To use a certificate you already have instead of Caddy's authority, mount the certificate and key files into the Caddy container and replace `tls internal` in [`docker/caddy/Caddyfile.on`](../docker/caddy/Caddyfile.on) with `tls /path/in/container/cert.pem /path/in/container/key.pem` (the Caddy `tls <cert> <key>` form; **unverified** here). Never point it at a public ACME issuer: that makes the server contact the outside world.
