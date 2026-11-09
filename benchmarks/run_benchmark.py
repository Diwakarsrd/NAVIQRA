"""Reproducible baseline benchmark for deterministic planning latency."""
from __future__ import annotations
import json
import statistics
import time
from datetime import date, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from naviqra.agents.planner import ItineraryAgent
from naviqra.models import TripRequest


def main(iterations: int = 250) -> None:
    agent = ItineraryAgent()
    start = date.today() + timedelta(days=60)
    request = TripRequest(traveler_id="bench", origin="Bengaluru", destination="Lisbon",
                          start_date=start, end_date=start + timedelta(days=5), budget=2500,
                          interests=["food", "museums"])
    samples = []
    for i in range(iterations):
        before = time.perf_counter()
        result = agent.plan(f"benchmark-{i}", request)
        samples.append((time.perf_counter() - before) * 1000)
        assert result.estimated_total <= request.budget
    samples.sort()
    report = {"benchmark": "planner_baseline", "iterations": iterations,
              "p50_ms": round(statistics.median(samples), 3),
              "p95_ms": round(samples[int(0.95 * (len(samples) - 1))], 3),
              "mean_ms": round(statistics.mean(samples), 3),
              "note": "Local deterministic planner only; not an LLM or live-provider benchmark."}
    out = Path("benchmark-results.json")
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
