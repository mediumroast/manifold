- [Home](/)

- **Components**
  - [acme-api](/components/acme-api.md)
  - [acme-web](/components/acme-web.md)
  - [acme-cli](/components/acme-cli.md)

- **Architecture**
  - [Overview](/architecture/overview.md)

- **Decisions**
  - [Use REST for the order service](/decisions/2026-01-14-use-rest-for-orders.md)

- **Handoffs**
  - acme-web → acme-api
    - [○ Order history endpoint](/handoffs/acme-web-to-acme-api/feature-order-history-endpoint.md)
  - acme-cli → acme-api
    - [◉ Cancel returns 500 for an order that already shipped](/handoffs/acme-cli-to-acme-api/bug-cancel-returns-500-for-an-order-that-alr.md)
  - acme-api → acme-web
    - [✓ Order status values renamed](/handoffs/acme-api-to-acme-web/breaking-change-order-status-values-renamed.md)
