"""Run an end-to-end local demonstration of the five NAVIQRA assets."""
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from naviqra.platform.core import AgentRuntime, PlatformStore


def main():
    with TemporaryDirectory() as tmp:
        store = PlatformStore(Path(tmp) / "naviqra-demo.sqlite")
        tenant = "demo"
        # 1. Five-tier traveler memory
        for tier, value in [
            ("profile", {"pace": "slow", "budget": "mid-range"}),
            ("episodic", {"last_trip": "Lisbon"}),
            ("semantic", {"prefers_walkable": True}),
            ("procedural", {"avoid_red_eye_flights": True}),
            ("active", {"current_trip": "Japan"}),
        ]:
            store.put_memory(tenant, "traveler-1", tier, "travel_context", value)

        # 2. Travel intelligence graph
        traveler = store.add_node(tenant, "traveler", "Traveler 1", {"traveler_id": "traveler-1"})
        destination = store.add_node(tenant, "destination", "Kyoto", {"country": "Japan"})
        store.add_edge(tenant, traveler["id"], "interested_in", destination["id"])

        # 3. Group consensus
        store.vote(tenant, "friends-trip", "member-a", "stay-1", 0.9)
        store.vote(tenant, "friends-trip", "member-b", "stay-1", 0.8)
        store.vote(tenant, "friends-trip", "member-a", "stay-2", 0.5)
        store.vote(tenant, "friends-trip", "member-b", "stay-2", 0.7)

        # 4. Agent runtime + recovery proposal (never books automatically)
        runtime = AgentRuntime(store)
        intelligence = runtime.execute(tenant, "travel_intelligence", {"traveler_id": "traveler-1"})
        consensus = runtime.execute(tenant, "group_consensus", {"group_id": "friends-trip"})
        recovery = runtime.execute(tenant, "recovery", {
            "trip_id": "trip-123",
            "disruption": "outbound_flight_cancelled",
            "options": [
                {"id": "alt-1", "type": "rebook", "price_delta": 85},
                {"id": "alt-2", "type": "refund_and_replan", "price_delta": 0},
            ],
        })

        print(json.dumps({
            "memory_tiers": [m["tier"] for m in store.get_memories(tenant, "traveler-1")],
            "graph": store.graph(tenant),
            "group_consensus": consensus["result"],
            "intelligence_agent": intelligence["status"],
            "recovery_agent": recovery["result"],
            "safety": "Recovery options require human selection; no booking was executed.",
        }, indent=2))


if __name__ == "__main__":
    main()
