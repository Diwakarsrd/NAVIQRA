# NAVIQRA v0.4.1

## Added
- Provider registry contract with deterministic synthetic sandbox provider.
- Tenant-scoped provider discovery and search endpoints.
- Tenant-scoped audit event persistence and retrieval.
- Traveler memory deletion endpoint with an audit record.
- 1,000-iteration local microbenchmark for memory reads, synthetic provider search, and audit writes.
- Global 15-day acquisition-interest campaign and buyer-facing materials.
- PostgreSQL reference schema for future migration planning.

## Compatibility
- Existing v1 and v2 APIs remain available.
- SQLite remains the active persistence backend.
- Existing development tenant credentials remain development-only.

## Explicit limitations
- No real supplier API credentials, live inventory, booking, ticketing, or payments.
- No production OIDC/JWKS identity integration.
- PostgreSQL SQL is a reference migration, not wired to runtime startup or data access.
- No independent security audit or production certification.
- Benchmark results are local microbenchmarks, not production service-level objectives.


## v0.4.1 release hardening
- Package the demo frontend within the Python distribution so installed wheels can import the API.
- Add `Cache-Control: no-store, private, max-age=0` and `Pragma: no-cache` to authenticated v1/v2 API responses.
- Disable interactive API documentation by default in production.
- Validate minimum 32-character production API and tenant secrets at startup.
- Pass `NAVIQRA_TENANT_KEYS` through Docker Compose and document it in `.env.example`.
- Fix the benchmark script so it can be run from the repository root without setting `PYTHONPATH`.
- Add regression tests for cache headers and packaged frontend availability.
