from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


class ProviderAdapter(Protocol):
    """Provider boundary. Adapters must never claim inventory is bookable unless verified."""
    name: str
    capabilities: tuple[str, ...]
    def search(self, query: dict[str, Any]) -> list[dict[str, Any]]: ...
    def health(self) -> dict[str, Any]: ...


@dataclass(frozen=True)
class ProviderDescriptor:
    name: str
    capabilities: tuple[str, ...]
    mode: str
    live_inventory: bool
    booking_enabled: bool


class ProviderRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, ProviderAdapter] = {}

    def register(self, adapter: ProviderAdapter) -> None:
        key = adapter.name.strip().lower()
        if not key or key in self._adapters:
            raise ValueError("provider name must be non-empty and unique")
        self._adapters[key] = adapter

    def get(self, name: str) -> ProviderAdapter:
        try:
            return self._adapters[name.strip().lower()]
        except KeyError as exc:
            raise KeyError(f"unknown provider: {name}") from exc

    def descriptors(self) -> list[dict[str, Any]]:
        result = []
        for adapter in sorted(self._adapters.values(), key=lambda a: a.name):
            health = adapter.health()
            result.append({"name": adapter.name, "capabilities": list(adapter.capabilities),
                           "mode": health.get("mode", "sandbox"),
                           "live_inventory": bool(health.get("live_inventory", False)),
                           "booking_enabled": bool(health.get("booking_enabled", False)),
                           "status": health.get("status", "unknown")})
        return result


class SandboxProvider:
    """Deterministic synthetic inventory for integration tests and demos only."""
    name = "sandbox"
    capabilities = ("accommodation_search", "activity_search", "disruption_alternatives")

    def search(self, query: dict[str, Any]) -> list[dict[str, Any]]:
        destination = str(query.get("destination", "unknown destination")).strip()
        if not destination or len(destination) > 160:
            raise ValueError("destination must be 1-160 characters")
        category = str(query.get("category", "accommodation"))
        if category not in {"accommodation", "activity", "transport"}:
            raise ValueError("category must be accommodation, activity or transport")
        return [
            {"id": f"sandbox-{category}-001", "category": category,
             "name": f"Sample {category} near {destination}", "destination": destination,
             "price": 119.0, "currency": "USD", "provider": self.name,
             "inventory_status": "synthetic", "bookable": False},
            {"id": f"sandbox-{category}-002", "category": category,
             "name": f"Alternative {category} in {destination}", "destination": destination,
             "price": 149.0, "currency": "USD", "provider": self.name,
             "inventory_status": "synthetic", "bookable": False},
        ]

    def health(self) -> dict[str, Any]:
        return {"status": "ok", "mode": "sandbox", "live_inventory": False, "booking_enabled": False}
