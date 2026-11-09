"""Real PostgreSQL contract tests; enabled in CI by NAVIQRA_TEST_POSTGRES_DSN."""
import os
from pathlib import Path
from uuid import uuid4

import pytest

from naviqra.database import Database
from naviqra.platform.core import PlatformStore
from naviqra.store import SQLiteStore

DSN = os.getenv("NAVIQRA_TEST_POSTGRES_DSN")
pytestmark = pytest.mark.skipif(not DSN, reason="PostgreSQL integration DSN not configured")


def test_postgres_migration_and_tenant_store_roundtrip():
    assert DSN
    migration = Path(__file__).parents[1] / "migrations" / "0001_postgres_foundation.sql"
    database = Database(DSN)
    with database.connect() as conn:
        conn.executescript(migration.read_text(encoding="utf-8"))

    legacy_store = SQLiteStore(DSN, initialize=False)
    platform_store = PlatformStore(DSN, initialize=False)
    legacy_store.check()
    platform_store.check()

    tenant = f"ci-{uuid4()}"
    traveler = f"traveler-{uuid4()}"
    platform_store.put_memory(tenant, traveler, "profile", "seat", "aisle")
    assert platform_store.get_memories(tenant, traveler)[0]["value"] == "aisle"

    node_a = platform_store.add_node(tenant, "traveler", "Traveler", {})
    node_b = platform_store.add_node(tenant, "destination", "Kyoto", {})
    platform_store.add_edge(tenant, node_a["id"], "interested_in", node_b["id"])
    assert len(platform_store.graph(tenant)["edges"]) == 1

    platform_store.vote(tenant, "group-1", "member-1", "candidate-a", 0.9)
    assert platform_store.consensus(tenant, "group-1")["ranked_candidates"][0]["candidate_id"] == "candidate-a"

    platform_store.audit(tenant, "ci", "test.write", "memory", traveler, {})
    assert platform_store.audit_events(tenant)[0]["action"] == "test.write"
    assert platform_store.delete_traveler(tenant, traveler)["memory_records_deleted"] == 1
