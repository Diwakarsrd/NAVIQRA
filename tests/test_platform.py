import os
from pathlib import Path
import pytest
from fastapi.testclient import TestClient

os.environ["NAVIQRA_DB"] = str(Path(__file__).parent / "platform-test.sqlite")
from naviqra.api import app  # noqa: E402
from naviqra import api as api_module  # noqa: E402
from naviqra.platform.core import PlatformStore, AgentRuntime  # noqa: E402

client = TestClient(app)


@pytest.fixture(autouse=True)
def isolated_platform(tmp_path, monkeypatch):
    store = PlatformStore(tmp_path / "platform.sqlite")
    monkeypatch.setattr(api_module, "platform_store", store)
    monkeypatch.setattr(api_module, "agent_runtime", AgentRuntime(store))
TENANT = "acme-demo"
HEADERS = {"X-Tenant-ID": TENANT, "X-Tenant-Key": "local-dev-key"}


def url(path):
    return f"/v2/tenants/{TENANT}{path}"


def test_tenant_authentication_required():
    response = client.get(url("/capabilities"))
    assert response.status_code == 401


def test_five_assets_are_exposed():
    response = client.get(url("/capabilities"), headers=HEADERS)
    assert response.status_code == 200
    assert set(response.json()["assets"]) == {
        "agent_runtime", "five_tier_memory", "travel_intelligence_graph",
        "group_consensus", "travel_recovery", "provider_sdk",
        "provider_registry", "tenant_audit", "traveler_data_deletion"
    }


def test_five_tier_memory_is_persistent_and_tenant_scoped():
    for tier in ["profile", "episodic", "semantic", "procedural", "active"]:
        r = client.post(url("/memory"), headers=HEADERS, json={
            "traveler_id":"traveler-1","tier":tier,"key":f"k-{tier}","value":{"v":tier}
        })
        assert r.status_code == 200
    assert len(client.get(url("/memory/traveler-1"), headers=HEADERS).json()) == 5
    other = {"X-Tenant-ID":"other-tenant","X-Tenant-Key":"local-dev-key"}
    assert client.get("/v2/tenants/other-tenant/memory/traveler-1", headers=other).json() == []


def test_travel_graph_nodes_and_edges():
    a = client.post(url("/graph/nodes"), headers=HEADERS,
                    json={"kind":"traveler","label":"Traveler A","properties":{"locale":"en"}})
    b = client.post(url("/graph/nodes"), headers=HEADERS,
                    json={"kind":"destination","label":"Kyoto","properties":{}})
    assert a.status_code == b.status_code == 200
    edge = client.post(url("/graph/edges"), headers=HEADERS,
                       json={"source":a.json()["id"],"relation":"interested_in","target":b.json()["id"]})
    assert edge.status_code == 200
    assert len(client.get(url("/graph"), headers=HEADERS).json()["edges"]) == 1


def test_group_consensus_weighted_ranking():
    for member,candidate,score in [
        ("m1","hotel-a",0.9),("m2","hotel-a",0.8),("m1","hotel-b",0.4),("m2","hotel-b",0.5)
    ]:
        r=client.post(url("/groups/votes"),headers=HEADERS,json={
            "group_id":"g1","member_id":member,"candidate_id":candidate,"score":score
        })
        assert r.status_code == 200
    result=client.get(url("/groups/g1/consensus"),headers=HEADERS).json()
    assert result["ranked_candidates"][0]["candidate_id"] == "hotel-a"


def test_recovery_agent_creates_approval_gated_options():
    r=client.post(url("/agents/run"),headers=HEADERS,json={"task_type":"recovery","payload":{
        "trip_id":"trip-1","disruption":"flight_cancelled",
        "options":[{"id":"alt-1","price":450},{"id":"alt-2","price":520}]
    }})
    assert r.status_code == 200
    assert r.json()["result"]["requires_human_confirmation"] is True


def test_agent_runtime_rejects_unknown_agent():
    r=client.post(url("/agents/run"),headers=HEADERS,json={"task_type":"unbounded_tool","payload":{}})
    assert r.status_code == 422


def test_graph_cannot_cross_tenant_boundary():
    a=client.post(url("/graph/nodes"),headers=HEADERS,json={"kind":"x","label":"x"})
    other={"X-Tenant-ID":"another","X-Tenant-Key":"local-dev-key"}
    edge=client.post("/v2/tenants/another/graph/edges",headers=other,json={
        "source":a.json()["id"],"relation":"leaks","target":a.json()["id"]
    })
    assert edge.status_code == 422


def test_tenant_header_must_match_path():
    wrong = {"X-Tenant-ID":"other-tenant","X-Tenant-Key":"local-dev-key"}
    response = client.get(url("/capabilities"), headers=wrong)
    assert response.status_code == 401


def test_configured_enterprise_tenant_key(monkeypatch):
    monkeypatch.setattr(api_module, "TENANT_KEYS", {"partner-acme":"a-long-random-secret"})
    headers = {"X-Tenant-ID":"partner-acme","X-Tenant-Key":"a-long-random-secret"}
    ok = client.get("/v2/tenants/partner-acme/capabilities", headers=headers)
    assert ok.status_code == 200
    bad = client.get("/v2/tenants/partner-acme/capabilities",
                     headers={"X-Tenant-ID":"partner-acme","X-Tenant-Key":"wrong"})
    assert bad.status_code == 401


def test_sandbox_provider_search_is_explicitly_non_bookable():
    response = client.post(url("/providers/sandbox/search"), headers=HEADERS,
                          json={"destination": "Lisbon", "category": "accommodation"})
    assert response.status_code == 200
    body = response.json()
    assert len(body["results"]) == 2
    assert all(item["bookable"] is False for item in body["results"])
    assert body["inventory_mode"] == "synthetic_non_bookable"


def test_unknown_provider_returns_404():
    response = client.post(url("/providers/does-not-exist/search"), headers=HEADERS,
                           json={"destination": "Tokyo"})
    assert response.status_code == 404


def test_provider_validation_rejects_invalid_category():
    response = client.post(url("/providers/sandbox/search"), headers=HEADERS,
                           json={"destination": "Tokyo", "category": "flight"})
    assert response.status_code == 422


def test_provider_search_is_audited_and_tenant_scoped():
    client.post(url("/providers/sandbox/search"), headers=HEADERS,
                json={"destination": "Rome"})
    events = client.get(url("/audit"), headers=HEADERS).json()["events"]
    assert events[0]["action"] == "provider.search"
    other = {"X-Tenant-ID": "other-tenant", "X-Tenant-Key": "local-dev-key"}
    assert client.get("/v2/tenants/other-tenant/audit", headers=other).json()["events"] == []


def test_traveler_memory_deletion_creates_audit_record():
    client.post(url("/memory"), headers=HEADERS, json={
        "traveler_id": "privacy-user", "tier": "profile", "key": "home", "value": "Paris"
    })
    deleted = client.delete(url("/travelers/privacy-user/memory"), headers=HEADERS)
    assert deleted.status_code == 200
    assert deleted.json()["memory_records_deleted"] == 1
    assert client.get(url("/memory/privacy-user"), headers=HEADERS).json() == []
    events = client.get(url("/audit"), headers=HEADERS).json()["events"]
    assert events[0]["action"] == "privacy.delete_traveler_memory"


def test_authenticated_v2_responses_are_never_cacheable():
    response = client.get(url("/memory/traveler-1"), headers=HEADERS)
    assert response.status_code == 200
    assert response.headers["cache-control"] == "no-store, private, max-age=0"
    assert response.headers["pragma"] == "no-cache"


def test_demo_frontend_is_present_in_source_distribution():
    from pathlib import Path
    web_dir = Path(api_module.__file__).resolve().parent / "web"
    assert (web_dir / "index.html").is_file()


def test_memory_delete_is_tenant_scoped_and_idempotent(tmp_path):
    platform_store = PlatformStore(tmp_path / "delete-test.sqlite")
    platform_store.put_memory("tenant-a", "traveler-1", "profile", "seat", "aisle")
    platform_store.put_memory("tenant-b", "traveler-1", "profile", "seat", "window")
    result = platform_store.delete_traveler("tenant-a", "traveler-1")
    assert result["memory_records_deleted"] == 1
    assert platform_store.get_memories("tenant-a", "traveler-1") == []
    assert platform_store.get_memories("tenant-b", "traveler-1")[0]["value"] == "window"


def test_group_vote_rejects_nan_and_infinite(tmp_path):
    import math
    platform_store = PlatformStore(tmp_path / "nan-test.sqlite")
    for value in (math.nan, math.inf, -math.inf):
        try:
            platform_store.vote("tenant-a", "g1", "m1", "c1", value)
        except ValueError:
            pass
        else:
            raise AssertionError("non-finite score must be rejected")
