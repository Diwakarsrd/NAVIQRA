-- Run in Supabase SQL Editor as the project database owner AFTER
-- migrations/0001_postgres_foundation.sql has been applied.
-- Replace the placeholder with a strong, unique password before execution.
-- Do not grant this role ownership, BYPASSRLS, or schema CREATE privileges.

DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'naviqra_runtime') THEN
    CREATE ROLE naviqra_runtime LOGIN PASSWORD 'REPLACE_WITH_A_LONG_RANDOM_PASSWORD';
  END IF;
END
$$;

GRANT CONNECT ON DATABASE postgres TO naviqra_runtime;
GRANT USAGE ON SCHEMA public TO naviqra_runtime;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO naviqra_runtime;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
  GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO naviqra_runtime;

-- Verify that runtime cannot create or alter schema objects.
REVOKE CREATE ON SCHEMA public FROM naviqra_runtime;
