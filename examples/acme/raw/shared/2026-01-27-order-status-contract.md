# Order status contract

Shared by Acme API, Acme Web and Acme CLI. Any change here needs a handoff to each of them.

| Status | Meaning | Next |
|---|---|---|
| `placed` | The order was created and payment is being taken | `confirmed`, `cancelled` |
| `confirmed` | Payment succeeded | `shipped`, `cancelled` |
| `shipped` | Handed to the carrier | `delivered` |
| `delivered` | Received by the customer | none |
| `cancelled` | Stopped before shipping | none |

Values are lowercase ASCII and are never reused for a different meaning.
