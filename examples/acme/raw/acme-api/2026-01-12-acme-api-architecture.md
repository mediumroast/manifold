# Acme API architecture

The service has three layers.

1. **Routers** validate requests and shape responses. One router per resource.
2. **Services** hold the business rules: pricing, stock checks, order state changes.
3. **Repositories** are the only code that talks to PostgreSQL.

Order state changes go through a single function so every change is checked against the
allowed transitions and written to an audit table.

Background work (confirmation emails, stock reconciliation) runs in a separate worker process
that reads a Postgres-backed job queue.
