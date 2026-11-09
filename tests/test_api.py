from datetime import date, timedelta
from uuid import uuid4


def trip_payload():
    start = date.today() + timedelta(days=30)
    return {"traveler_id": "traveler-test", "origin": "Bengaluru", "destination": "Tokyo",
            "start_date": start.isoformat(), "end_date": (start + timedelta(days=3)).isoformat(),
            "budget": 1500, "currency": "USD", "travelers": 2,
            "interests": ["food", "architecture"], "constraints": []}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_plan_trip_returns_days_and_trip_id(client):
    response = client.post("/v1/trips/plan", json=trip_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["trip_id"]
    assert len(body["itinerary"]["activities"]) == 3
    assert body["itinerary"]["estimated_total"] <= 1500


def test_invalid_date_range_rejected(client):
    payload = trip_payload()
    payload["end_date"] = payload["start_date"]
    assert client.post("/v1/trips/plan", json=payload).status_code == 422


def test_memory_persists(client):
    response = client.post("/v1/memories", json={"traveler_id": "memory-test", "key": "seat", "value": "aisle"})
    assert response.status_code == 200
    memories = client.get("/v1/travelers/memory-test/memories")
    assert memories.status_code == 200
    assert any(m["value"] == "aisle" for m in memories.json())


def test_booking_requires_approval_and_is_idempotent(client):
    intent = {"trip_id": "trip-123", "provider": "demo", "item_type": "stay",
              "item_id": "stay-1", "amount": 200, "currency": "USD",
              "idempotency_key": f"test-booking-{uuid4()}"}
    first = client.post("/v1/bookings/prepare", json=intent).json()
    second = client.post("/v1/bookings/prepare", json=intent).json()
    assert first["id"] == second["id"]
    assert first["status"] == "pending_approval"
    approved = client.post(f"/v1/bookings/{first['id']}/approval",
                           json={"approved": True, "approver": "traveler-test"})
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"


def test_demo_provider_is_explicitly_not_live(client):
    response = client.get("/v1/providers/demo/search", params={"destination": "Lisbon"})
    assert response.status_code == 200
    assert "not live" in response.json()["notice"]


def test_capabilities_disclose_demo_provider(client):
    response = client.get("/v1/platform/capabilities")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "NAVIQRA"
    assert body["providers"][0]["live_inventory"] is False
    assert body["execution_policy"]["purchase_requires_approval"] is True


def test_security_headers_are_present(client):
    response = client.get("/health")
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["x-request-id"]


def test_health_reports_database(client):
    body = client.get("/health").json()
    assert body["database"] == "ok"


def test_api_key_guard_can_be_enabled(client, monkeypatch):
    import naviqra.api as api
    monkeypatch.setattr(api, "API_KEY", "test-secret-key")
    assert client.get("/v1/platform/capabilities").status_code == 401
    authorized = client.get("/v1/platform/capabilities", headers={"X-API-Key": "test-secret-key"})
    assert authorized.status_code == 200



def test_oversized_content_length_rejected(client):
    import naviqra.api as api
    # Middleware uses a configurable cap; keep the test isolated from host env.
    import os
    previous = os.environ.get("NAVIQRA_MAX_REQUEST_BYTES")
    os.environ["NAVIQRA_MAX_REQUEST_BYTES"] = "32"
    try:
        response = client.post("/v1/memories", content=b"{}" * 40,
                               headers={"Content-Type": "application/json"})
        assert response.status_code == 413
    finally:
        if previous is None:
            os.environ.pop("NAVIQRA_MAX_REQUEST_BYTES", None)
        else:
            os.environ["NAVIQRA_MAX_REQUEST_BYTES"] = previous


def test_v2_tenant_path_must_match_authenticated_tenant(client, monkeypatch):
    import naviqra.api as api
    monkeypatch.setattr(api, "TENANT_KEYS", {"tenant-a": "a" * 32})
    response = client.get("/v2/tenants/tenant-b/capabilities", headers={
        "X-Tenant-ID": "tenant-a", "X-Tenant-Key": "a" * 32
    })
    assert response.status_code == 401


def test_legacy_v1_disabled_in_production(client, monkeypatch):
    import naviqra.api as api
    monkeypatch.setattr(api, "IS_PRODUCTION", True)
    monkeypatch.setattr(api, "ENABLE_LEGACY_V1", False)
    response = client.get("/v1/platform/capabilities")
    assert response.status_code == 404


def test_wildcard_production_host_policy_is_rejected_at_import(tmp_path):
    import os
    import subprocess
    import sys
    env = os.environ.copy()
    env.update({
        "NAVIQRA_ENV": "production",
        "NAVIQRA_API_KEY": "a" * 40,
        "NAVIQRA_TENANT_KEY_HASHES": '{"tenant-a":"' + "b" * 64 + '"}',
        "NAVIQRA_DATABASE_URL": "postgresql://db.example/naviqra",
        "NAVIQRA_CORS_ORIGINS": "https://app.example.com",
        "NAVIQRA_ALLOWED_HOSTS": "*",
        "NAVIQRA_DB_AUTO_CREATE": "false",
    })
    result = subprocess.run([sys.executable, "-c", "import naviqra.api"], env=env,
                            capture_output=True, text=True)
    assert result.returncode != 0
    assert "Wildcard CORS origins" in result.stderr


def test_production_tenant_key_hash_authentication(client, monkeypatch):
    import hashlib
    import naviqra.api as api
    raw_key = "production-tenant-secret-that-is-not-stored"
    monkeypatch.setattr(api, "IS_PRODUCTION", True)
    monkeypatch.setattr(api, "TENANT_KEY_HASHES", {
        "tenant-a": [hashlib.sha256(raw_key.encode()).hexdigest()]
    })
    monkeypatch.setattr(api, "ENABLE_LEGACY_V1", False)
    response = client.get("/v2/tenants/tenant-a/capabilities", headers={
        "X-Tenant-ID": "tenant-a", "X-Tenant-Key": raw_key
    })
    assert response.status_code == 200
    rejected = client.get("/v2/tenants/tenant-a/capabilities", headers={
        "X-Tenant-ID": "tenant-a", "X-Tenant-Key": "wrong-key"
    })
    assert rejected.status_code == 401
