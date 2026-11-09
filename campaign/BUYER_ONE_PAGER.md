# NAVIQRA — Travel Intelligence Infrastructure

**Apache-2.0 | Global developer-first launch | Full-company acquisition is founder preference**

## The problem
Travel journeys span marketplaces, airlines, accommodation providers, activities, and support systems. Agent experiences need context and workflow orchestration across those boundaries, while each supplier must remain authoritative for identity, live availability, price, payment, and booking.

## The proposed layer
NAVIQRA is an open, provider-neutral infrastructure layer for travel agents: a deterministic runtime, portable five-tier traveler memory, a travel intelligence graph, group consensus, provider adapter contracts, auditability, and human-approved disruption recovery.

## Demonstrated in v0.5.0
- Tenant-scoped memory, graph, and APIs.
- Weighted group consensus.
- Synthetic provider adapter and registry.
- Auditable provider searches and memory deletion.
- Recovery options that require human confirmation.
- Automated tests, runnable demo, and local microbenchmark harness.

## Evaluation proposal
Choose one high-value workflow and one authoritative supplier sandbox. Agree on security, privacy, and identity boundaries. Implement one real adapter, measure success and failure cases, and decide whether to expand.

## Current boundaries
The public demo uses synthetic, non-bookable inventory. v0.5.0 includes a PostgreSQL deployment path and migration schema, but live PostgreSQL integration has not yet been verified. OIDC/SSO, supplier production integrations, and independent security review remain outstanding.

## Why discuss strategic fit
A travel marketplace or distribution platform may benefit from reusable orchestration and portable context that complements its existing supply and transaction systems. This is a strategic hypothesis for evaluation, not a claim of customer or buyer interest.

**Repository:** [URL] · **Demo:** [URL] · **Contact:** [Founder contact]
