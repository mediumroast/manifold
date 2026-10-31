# Acme API

Acme API is the order service behind the Acme storefront. It owns customers, products and
orders, and exposes them as a JSON REST API.

- Language: Python 3.12 with FastAPI
- Storage: PostgreSQL
- Runs as one container behind a load balancer

Start it locally with `make run`; the interactive API documentation is served at `/docs`.
