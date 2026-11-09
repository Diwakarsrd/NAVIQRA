# NAVIQRA v0.5.0 production deployment runbook

This runbook describes a single-region API deployment behind a TLS reverse proxy.
It is a baseline, not a substitute for a threat model, security audit, or operational
readiness review.

## Required infrastructure

- Managed PostgreSQL with TLS (`sslmode=verify-full`), encrypted storage and backups.
- Separate migration and runtime database roles. Runtime role must not have DDL.
- Secret manager for global API and tenant keys.
- TLS reverse proxy/WAF with request-size and distributed rate limits.
- Centralized logs, metrics, traces, alerting and on-call ownership.
- A tested backup restore and incident-response process.

## 1. Generate independent secrets

Generate one API key and one unique key per tenant. Do not reuse keys. Store them in
your secret manager; never commit `.env` files or place tenant keys in browser/mobile
build variables.

```bash
python -c 'import secrets; print(secrets.token_urlsafe(48))'
```

Set `NAVIQRA_API_KEY` using secret-manager injection. Configure
`NAVIQRA_TENANT_KEY_HASHES` as a JSON map from tenant IDs to one or more SHA-256
hex digests. The client retains the raw random key; the API stores only its hash.
To rotate without downtime, temporarily configure both old and new hashes, deploy
clients with the new key, then remove the old hash. Example generator:

```bash
python - <<'PYGEN'
import hashlib, secrets
key = secrets.token_urlsafe(48)
print("CLIENT_KEY=" + key)
print("SERVER_SHA256=" + hashlib.sha256(key.encode()).hexdigest())
PYGEN
```

The global API key must be independent from all tenant client keys.

## 2. Apply schema using a migration identity

```bash
psql "$NAVIQRA_MIGRATION_DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f migrations/0001_postgres_foundation.sql
```

Use a distinct runtime DB role with only `CONNECT`, schema `USAGE`, and the required
`SELECT, INSERT, UPDATE, DELETE` privileges on these tables. Do not grant `CREATE`,
`ALTER`, or superuser privileges to the API role.

## 3. Configure production environment

Required variables are documented in `.env.example`. In addition:

- `NAVIQRA_ENV=production`
- `NAVIQRA_DATABASE_URL=postgresql://...?...sslmode=verify-full`
- `NAVIQRA_DB_AUTO_CREATE=false`
- `NAVIQRA_TENANT_KEY_HASHES` with one or more 64-character SHA-256 hex hashes per tenant
- `NAVIQRA_ENABLE_LEGACY_V1=false`
- `NAVIQRA_DOCS=false`
- Explicit `NAVIQRA_ALLOWED_HOSTS` and `NAVIQRA_CORS_ORIGINS`

The service fails startup if production configuration is incomplete, SQLite is selected,
or required migrated tables are missing.

## 4. Deploy behind TLS and rate limiting

`docker compose up --build -d` binds the container to `127.0.0.1:8000`. Configure the
TLS reverse proxy to forward to that address. An example Nginx configuration is in
`deploy/nginx/naviqra.conf`; adapt certificates, hostname, rate limits, and network
policy to your environment. Do not expose port 8000 directly to the public internet.

## 5. Verify before enabling traffic

- `GET /health` returns 200 and database status `ok`.
- Invalid API key on `/v1` is rejected; `/v1` should return 404 in production.
- Invalid tenant credentials and tenant/path mismatches return 401.
- A tenant cannot read or delete another tenant's data.
- Request bodies over the proxy limit return 413.
- CORS only permits the configured frontend origins.
- Restore a backup into a clean environment and run smoke tests.
- Confirm logs do not contain credentials, authorization headers, or traveler secrets.

## Known blockers to broader enterprise approval

OIDC/SSO, a built-in distributed rate limiter, managed tenant-key hashing/rotation,
external supplier production adapters, payment/ticketing, a formal data-retention
workflow, independent penetration testing, and production SLO validation are not
included. The sample Nginx rate limiter is per edge instance; use a shared WAF or
central rate-limiting service for multi-edge/multi-region deployments.

Do not collect passport, payment-card, or other high-risk identity data in this
release. Synthetic provider results are non-bookable; no real booking or rebooking
is performed.
