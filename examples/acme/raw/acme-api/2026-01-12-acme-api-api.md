# Acme API contract

Base path `/v1`. All bodies are JSON. Errors use `{"error": {"code": "...", "message": "..."}}`.

| Method | Path | Purpose |
|---|---|---|
| GET | /v1/products | List products |
| GET | /v1/products/{id} | One product |
| POST | /v1/orders | Create an order |
| GET | /v1/orders/{id} | One order |
| POST | /v1/orders/{id}/cancel | Cancel an order that has not shipped |

An order has `id`, `customer_id`, `lines`, `total_cents`, `currency` and `status`.
Status values are listed in the shared order-status contract.
