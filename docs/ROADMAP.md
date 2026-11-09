# Roadmap

## v0.1.0 — working foundation
- FastAPI API and browser demo
- deterministic itinerary agent and orchestration stages
- persistent traveler preference records
- provider protocol and clearly labeled demo inventory
- approval-gated, idempotent booking intent workflow
- tests, Docker, CI, and latency benchmark

## v0.2 — secure multi-tenant runtime
- OAuth/OIDC or signed API keys, tenant-scoped authorization
- PostgreSQL repository and migration tooling
- audit log, rate limiting, secret management, PII lifecycle controls
- structured event bus and background task execution

## v0.3 — model and tool integrations
- model-provider interface with JSON-schema output validation
- retrieval/ranking with provenance and freshness metadata
- maps, weather, flight, lodging, and activity provider adapters
- policy engine for budget, accessibility, visa and traveler constraints

## v0.4 — execution-grade workflows
- live availability and price revalidation
- provider-specific booking and cancellation APIs
- idempotent outbox, retries, compensation and reconciliation
- human approval UX and immutable action audit trail

## v1.0 — evidence-led release
- external security review and threat model
- load, reliability, quality, and cost benchmarks
- integration certification and provider contract tests
- documented SLOs and operational runbooks
- independent reproducibility of all published claims
