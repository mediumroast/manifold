-- SPDX-License-Identifier: Apache-2.0
-- Manifold security store, schema version 1.
-- Secrets are never stored: credentials keep only a SHA-256 hash of the secret.

CREATE TABLE settings (
    key        TEXT PRIMARY KEY,
    value      TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE principals (
    id                          TEXT PRIMARY KEY,
    name                        TEXT NOT NULL UNIQUE,
    kind                        TEXT NOT NULL CHECK (kind IN ('human', 'agent', 'service')),
    active                      INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1)),
    may_self_grant_on_register  INTEGER NOT NULL DEFAULT 0 CHECK (may_self_grant_on_register IN (0, 1)),
    created_at                  TEXT NOT NULL,
    disabled_at                 TEXT
);

CREATE TABLE credentials (
    credential_id TEXT PRIMARY KEY,
    principal_id  TEXT NOT NULL REFERENCES principals(id) ON DELETE CASCADE,
    secret_hash   TEXT NOT NULL,
    label         TEXT NOT NULL DEFAULT '',
    created_at    TEXT NOT NULL,
    expires_at    TEXT,
    revoked_at    TEXT
);
CREATE INDEX credentials_by_principal ON credentials(principal_id);

CREATE TABLE roles (
    principal_id TEXT NOT NULL REFERENCES principals(id) ON DELETE CASCADE,
    role         TEXT NOT NULL CHECK (role IN ('reader', 'contributor', 'registrar', 'admin')),
    PRIMARY KEY (principal_id, role)
);

CREATE TABLE grants (
    principal_id TEXT NOT NULL REFERENCES principals(id) ON DELETE CASCADE,
    scope        TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (principal_id, scope)
);

CREATE TABLE denies (
    principal_id TEXT NOT NULL REFERENCES principals(id) ON DELETE CASCADE,
    scope        TEXT NOT NULL,
    created_at   TEXT NOT NULL,
    PRIMARY KEY (principal_id, scope)
);

CREATE TABLE component_state (
    slug        TEXT PRIMARY KEY,
    authority   TEXT NOT NULL DEFAULT 'either' CHECK (authority IN ('grants', 'repo-write', 'either')),
    state       TEXT NOT NULL DEFAULT 'active' CHECK (state IN ('active', 'archived')),
    reason      TEXT NOT NULL DEFAULT '',
    archived_at TEXT,
    purge_after TEXT
);

CREATE TABLE usage (
    principal_id TEXT NOT NULL,
    day          TEXT NOT NULL,
    counter      TEXT NOT NULL,
    count        INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (principal_id, day, counter)
);

CREATE TABLE audit (
    id      INTEGER PRIMARY KEY AUTOINCREMENT,
    ts      TEXT NOT NULL,
    event   TEXT NOT NULL,
    actor   TEXT NOT NULL,
    subject TEXT NOT NULL DEFAULT '',
    detail  TEXT NOT NULL DEFAULT ''
);
CREATE INDEX audit_by_ts ON audit(ts);
