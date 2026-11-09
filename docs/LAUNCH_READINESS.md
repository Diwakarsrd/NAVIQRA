# NAVIQRA v0.5.0 — production foundation readiness

## Decision

**Suitable for a controlled developer preview and deployment testing. Not certified
for enterprise production, sensitive traveler data, or live travel transactions.**

## Verified locally

- `pytest -q`: 36 passed, 1 PostgreSQL integration test skipped locally (no PostgreSQL DSN).
- `python -m compileall -q naviqra`: passes.
- `python examples/platform_quickstart.py`: passes.
- `python benchmarks/v05_benchmark.py`: 1,000 local SQLite/in-process iterations.
- Python wheel builds successfully.
- Production configuration requires PostgreSQL, explicit host/CORS configuration,
  a 32+ character global secret and SHA-256 tenant-key hashes, and migration-managed schema creation.
- Legacy non-tenant-scoped v1 API is disabled by default in production.
- Tenant/path mismatch, oversized Content-Length, tenant-scoped deletion, and
  non-finite group scores have regression tests.

## Not verified

- Live PostgreSQL server/driver integration was not run locally; a dedicated CI
  service-container job now applies the migration and exercises both stores.
- Docker image build/runtime and cloud deployment.
- OIDC/SSO, distributed rate limiting, security audit, penetration test, external
  dependency scan, TLS termination, WAF, monitoring, backups and restore drills.
- Supplier APIs, live inventory, payment, ticketing, cancellation, and rebooking.
- Mobile app store build/submission.

## Before customer production use

1. Provision managed PostgreSQL and apply `migrations/0001_postgres_foundation.sql`
   using a migration identity.
2. Use a least-privilege runtime DB role and a managed secrets manager.
3. Deploy behind TLS, WAF and shared rate limiting; configure trusted hosts/origins.
4. Run tenant-isolation, load, failure, backup/restore and disaster-recovery tests.
5. Add OIDC/SSO and key rotation controls appropriate to customer contracts.
6. Complete privacy/legal review and independent security assessment.
7. Add supplier-specific sandbox/contract tests before any live travel actions.

## Product boundary

Agent execution is deterministic. Provider inventory is synthetic and non-bookable.
Recovery only creates alternatives and requires human confirmation. No live supplier
integration or payment/ticketing is present. Do not market the current build as a
live booking agent or security-audited enterprise platform.
