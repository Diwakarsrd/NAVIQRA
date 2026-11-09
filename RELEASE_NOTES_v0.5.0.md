# NAVIQRA v0.5.0 — production deployment foundation

## Added
- Shared DB-API adapter for SQLite local development and PostgreSQL production via psycopg 3.
- Full PostgreSQL migration for legacy tables and all platform tables.
- Production startup requires PostgreSQL, migration-managed schema, independent global secret and SHA-256-hashed tenant keys, explicit HTTPS CORS origins, and explicit host allowlists.
- Runtime schema auto-creation is disabled in production; startup checks required tables.
- Legacy non-tenant-scoped `/v1` endpoints are disabled by default in production.
- Production tenant API keys are stored as SHA-256 hashes; multiple hashes per tenant support overlap during manual key rotation.
- Request Content-Length limit, sanitized request IDs, TrustedHost enforcement, no-store API responses, and safer container defaults.
- Nginx TLS/rate-limit example and production deployment runbook.
- PostgreSQL service-container integration job in GitHub Actions.
- Regression tests for oversized requests, tenant/path mismatch, tenant-scoped deletion, non-finite scores, wildcard production hosts, and database adapter behavior.

## Local verification
- `pytest -q`: 36 passed, 1 PostgreSQL integration test skipped (no local PostgreSQL DSN).
- `python -m compileall -q naviqra`: passed.
- `python examples/platform_quickstart.py`: passed.
- `python benchmarks/v05_benchmark.py`: 1,000 local SQLite/in-process iterations completed.
- `python -m pip wheel . --no-deps --no-build-isolation`: wheel built successfully.

## Not certified / not verified locally
- PostgreSQL integration job has been added but has not yet run on GitHub Actions.
- Docker image build/runtime and cloud deployment.
- OIDC/SSO, shared distributed rate limiting, formal tenant-key hashing/rotation, supplier production adapters, payment/ticketing, independent penetration testing, external vulnerability scan, backups/restore drills, and production SLO validation.
- No real inventory, booking, payment, ticketing, or rebooking is provided.

This is a **production deployment foundation**, not a security-audited enterprise travel transaction service. Do not store passport/payment-card data or expose it to real customers until the listed controls and independent review are complete.
