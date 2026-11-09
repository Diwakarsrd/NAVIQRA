# NAVIQRA v0.5.0 — release status for launch communications

NAVIQRA v0.5.0 adds a PostgreSQL-backed production deployment path, explicit
production configuration gates, migration-managed schema creation, tenant-scoped
API access, and hardened container/reverse-proxy guidance.

Verified locally: 36 automated tests, Python compilation, quickstart demo, local
SQLite microbenchmark, and wheel build.

Not verified: live PostgreSQL integration (PostgreSQL driver/server unavailable in
the build environment), Docker image execution, cloud deployment, OIDC/SSO,
independent penetration testing, supplier production APIs, payment/ticketing, or
real travel transactions.

Use the term **production deployment foundation** or **developer preview**, not
"security audited", "enterprise certified", or "live booking platform". Public
launch claims must be updated after the actual cloud deployment and independent
review are complete.
