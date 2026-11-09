# NAVIQRA — early development

**Open infrastructure for interoperable travel agents.** Apache-2.0.

NAVIQRA provides a tenant-scoped travel-agent runtime, five-tier traveler memory,
travel intelligence graph, group consensus, approval-gated disruption recovery,
provider adapter boundary, and Python SDK. It is an infrastructure foundation,
not a travel marketplace or booking provider.


## Deploy on Render + Supabase

A controlled-pilot deployment blueprint is included in `render.yaml`. Follow
[`docs/RENDER_SUPABASE_DEPLOYMENT.md`](docs/RENDER_SUPABASE_DEPLOYMENT.md) to provision
Supabase PostgreSQL, apply migrations, create a least-privilege runtime role, configure
Render secrets, and verify the deployment. Use the checklist in
[`docs/PRODUCTION_VERIFICATION_CHECKLIST.md`](docs/PRODUCTION_VERIFICATION_CHECKLIST.md).
Do not use the migration/owner database credentials as the application runtime user.


## Quick start — local development

```bash
python -m venv .venv
# Windows: .venv\\Scripts\\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
uvicorn naviqra.api:app --reload
```

Open `http://127.0.0.1:8000/docs`.

Development tenant credentials:
- `X-Tenant-ID: demo`
- `X-Tenant-Key: local-dev-key`

Never use the development key outside local development.

## Main capabilities

- Five-tier tenant-scoped memory: profile, episodic, semantic, procedural, active.
- Tenant-scoped graph nodes and edges.
- Weighted group preference consensus.
- Deterministic agent workflow runtime with execution records.
- Travel disruption alternatives that require human selection/approval.
- Provider registry with synthetic sandbox inventory (non-bookable).
- Tenant audit events and traveler memory deletion.
- Python SDK, FastAPI, mobile source, tests, benchmark harness, Docker and CI.

## v2 API example

```bash
curl http://127.0.0.1:8000/v2/tenants/demo/capabilities \
  -H "X-Tenant-ID: demo" -H "X-Tenant-Key: local-dev-key"
```

## Python SDK

```python
from naviqra.sdk import NaviqraClient

client = NaviqraClient("http://127.0.0.1:8000", "demo", "local-dev-key")
client.remember("traveler-1", "profile", "travel_style", "slow travel")
print(client.memories("traveler-1"))
```

## Verification

```bash
pytest -q
python -m compileall -q naviqra
python examples/platform_quickstart.py
python benchmarks/v05_benchmark.py
python -m pip wheel . --no-deps --no-build-isolation -w dist
```

The benchmark is a local SQLite/in-process microbenchmark, not a production SLO.

## Production deployment foundation

Production mode requires PostgreSQL, a global API secret and SHA-256 hashes of independent tenant secrets,
explicit trusted CORS origins and hostnames, and pre-applied schema migrations.
SQLite is restricted to development and tests. Install the driver:

```bash
pip install -e ".[postgres]"
```

Apply the schema with a migration role:

```bash
psql "$NAVIQRA_MIGRATION_DATABASE_URL" -v ON_ERROR_STOP=1 \
  -f migrations/0001_postgres_foundation.sql
```

Then configure production environment variables as shown in `.env.example` and
`docs/PRODUCTION_DEPLOYMENT.md`. The runtime role should have DML permissions only.
The Docker Compose service binds to localhost; expose it only behind a TLS reverse
proxy/WAF. The legacy non-tenant-scoped `/v1` API is disabled in production by default.

## Known production blockers

This is a **development foundation**, not an audited enterprise travel
transaction service. The following remain outside this release: OIDC/SSO,
built-in distributed rate limiting, automated key lifecycle management and rotation workflow,
production supplier integrations, payment/ticketing, formal privacy/retention
workflows, independent penetration testing, live PostgreSQL integration has not yet run locally (a CI service-container job is configured), cloud deployment, and restore-drill/SLO
evidence. The API must not be used for live booking or rebooking. Synthetic provider
results are non-bookable; no payment, ticketing, or external supplier operation is
performed. Do not collect passport or payment-card data.

## Campaign

`campaign/` contains buyer briefs, outreach drafts, launch messaging, demo script,
acquisition brief, 15-day execution plan, and current release status. Outreach is
not sent automatically and no acquisition interest is implied.

## Mobile app

The optional Expo app is an early client. Run `npm install`, `npm run typecheck`,
`npm test`, Expo Doctor, and native builds before distribution. Do not embed tenant
secrets in client-side environment variables.

## License

Apache License 2.0. See `LICENSE`.


## Project maturity

This renamed repository is an initial integration scaffold. Before public claims of production readiness, complete and pass the PostgreSQL CI job, OIDC/SSO, distributed rate limiting, key lifecycle automation, supplier contract tests, privacy review, restore drills, load tests and independent security review.
