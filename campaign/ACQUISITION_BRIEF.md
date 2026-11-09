# NAVIQRA — strategic acquisition discussion brief

## Thesis
NAVIQRA is an open, provider-neutral intelligence and orchestration layer for travel agents. It aims to make agent workflows portable across travel suppliers while leaving each marketplace or distribution provider authoritative for inventory, pricing, identity, payments, and booking.

## What exists in v0.5.0
- Deterministic agent runtime with recorded outcomes.
- Tenant-scoped five-tier memory and travel graph.
- Weighted group preference consensus.
- Recovery case generation with explicit human confirmation.
- Provider registry and synthetic sandbox adapter.
- Tenant audit events and traveler-memory deletion endpoint.
- Python SDK, API docs, tests, demo, and local microbenchmark harness.

## What is not claimed
- No live supplier inventory, booking, ticketing, or payment integration in this release.
- PostgreSQL deployment path and migration schema are included; live PostgreSQL integration is not yet verified. OIDC/SSO and independent security review remain outstanding.
- No independent security certification or external customer traction unless separately evidenced.
- Local microbenchmarks are not production SLOs.

## Why a strategic buyer might care
A buyer with marketplace, distribution, or travel-servicing assets may find value in reusable orchestration, portable context, and human-governed recovery workflows that can be integrated into existing products. This is a hypothesis to validate, not a claim of buyer interest.

## Proposed transaction posture
Founder preference: full-company acquisition. Any discussion would be subject to verified IP ownership, contributor/contractor assignments, license and dependency diligence, security review, liabilities, and mutually agreed terms. The project remains Apache-2.0; an acquisition does not imply the buyer can retroactively revoke rights already granted under the license.

## 30-day technical evaluation proposal
1. Select one workflow and one authoritative supplier sandbox.
2. Agree on identity, data minimization, retention, and security boundaries.
3. Build one real provider adapter with test fixtures and contract tests.
4. Measure task success, latency, failure recovery, and human-approval rates.
5. Review operational fit and decide whether to expand, partner, or stop.
