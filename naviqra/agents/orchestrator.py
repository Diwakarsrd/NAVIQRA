from __future__ import annotations
from uuid import uuid4
from naviqra.agents.planner import ItineraryAgent
from naviqra.models import AgentPlan, MemoryRecord, TripRequest
from naviqra.store import SQLiteStore


class TravelOrchestrator:
    def __init__(self, store: SQLiteStore) -> None:
        self.store = store
        self.planner = ItineraryAgent()

    def plan_trip(self, request: TripRequest) -> AgentPlan:
        trip_id = str(uuid4())
        memories = self.store.get_memories(request.traveler_id)
        itinerary = self.planner.plan(trip_id, request)
        warnings = []
        if not memories:
            warnings.append("No saved traveler preferences found; recommendations use this request only.")
        return AgentPlan(trip_id=trip_id,
                         stages=["load_traveler_memory", "discover_destination", "build_itinerary", "validate_budget"],
                         itinerary=itinerary, memory_used=memories, warnings=warnings)

    def remember(self, traveler_id: str, key: str, value: object) -> MemoryRecord:
        return self.store.add_memory(MemoryRecord(traveler_id=traveler_id, key=key, value=value))
