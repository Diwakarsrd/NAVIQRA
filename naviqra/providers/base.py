from __future__ import annotations
from typing import Protocol, Any


class TravelProvider(Protocol):
    name: str
    def search(self, query: dict[str, Any]) -> list[dict[str, Any]]: ...


class DemoProvider:
    """Deterministic local provider for demos and tests; it does not make real bookings."""
    name = "demo"

    def search(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        destination = str(query.get("destination", "your destination"))
        return [
            {"id": "demo-stay-001", "type": "stay", "name": f"Central stay in {destination}",
             "price": 120.0, "currency": "USD", "source": "demo", "bookable": False},
            {"id": "demo-activity-001", "type": "activity", "name": f"Local culture walk in {destination}",
             "price": 25.0, "currency": "USD", "source": "demo", "bookable": False},
        ]
