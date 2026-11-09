import pytest
from fastapi.testclient import TestClient

from naviqra import api
from naviqra.agents.orchestrator import TravelOrchestrator
from naviqra.booking import BookingService
from naviqra.store import SQLiteStore


@pytest.fixture
def client(tmp_path, monkeypatch):
    isolated_store = SQLiteStore(tmp_path / "test-naviqra.db")
    monkeypatch.setattr(api, "store", isolated_store)
    monkeypatch.setattr(api, "orchestrator", TravelOrchestrator(isolated_store))
    monkeypatch.setattr(api, "booking_service", BookingService(isolated_store))
    monkeypatch.setattr(api, "API_KEY", None)
    with TestClient(api.app) as test_client:
        yield test_client
