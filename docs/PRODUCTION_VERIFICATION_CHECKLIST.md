# NAVIQRA production deployment verification checklist

Mark each item only after observing the result in the actual Render/Supabase environment.

## Before first deployment
- [ ] Supabase project created in approved region; data residency reviewed.
- [ ] PostgreSQL foundation migration applied successfully by owner/migration role.
- [ ] Runtime DB role created with DML only; DDL denied.
- [ ] Runtime connection uses Supabase Session Pooler with TLS.
- [ ] Tenant key generated locally; raw key stored only in trusted secret manager.
- [ ] Render environment contains no migration/owner database credentials.
- [ ] Allowed hosts and CORS origins are exact, not wildcard.
- [ ] Render `NAVIQRA_API_KEY` generated and kept secret.
- [ ] No secrets committed to repository, build args, logs, or mobile bundle.

## Render deployment
- [ ] Docker image builds from clean checkout.
- [ ] Render service is in intended region and paid plan.
- [ ] TLS certificate active on Render hostname/custom domain.
- [ ] `/health` returns HTTP 200 and database status `ok`.
- [ ] Render deploy logs contain no secrets or DSNs.
- [ ] Restart/redeploy preserves data in Supabase.

## API security smoke tests
- [ ] `/v1/*` returns 404 in production.
- [ ] `/docs` and `/redoc` are disabled.
- [ ] Missing tenant headers return 401 on `/v2/*`.
- [ ] Wrong tenant key returns 401.
- [ ] Tenant A cannot request Tenant B path using Tenant A credentials.
- [ ] Tenant A cannot read Tenant B memory, graph, votes, audit, or recovery data.
- [ ] Oversized request is rejected at edge and application layer.
- [ ] Untrusted Host header is rejected.
- [ ] CORS rejects unlisted origins and permits only exact configured origins.
- [ ] Authenticated API responses include `Cache-Control: no-store`.
- [ ] Runtime database role cannot create/alter/drop tables.

## Reliability and operations
- [ ] Supabase backup/PITR policy enabled for selected plan.
- [ ] Restore tested into a separate Supabase project; application smoke test passes.
- [ ] Render service alerts and owner notifications configured.
- [ ] Load test completed at expected concurrency; DB connection limits respected.
- [ ] Error rate, latency, memory, CPU, DB connections and saturation monitored.
- [ ] Incident response and rollback owner identified.
- [ ] Key rotation tested with overlapping old/new hashes.
- [ ] Data deletion and retention workflow reviewed.
- [ ] Privacy/legal and security review completed before real customer data.

## Launch gate
- [ ] All mandatory checks above pass and evidence is retained.
- [ ] No real booking/payment claims are made; provider demo clearly marked synthetic.
- [ ] Product is labeled controlled pilot until OIDC/RLS/security audit/SLO gaps close.
