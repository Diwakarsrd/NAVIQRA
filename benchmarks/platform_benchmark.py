"""Reproducible local microbenchmarks for core NAVIQRA primitives.

These measure local SQLite/domain operations only. They are not end-to-end
LLM, provider, booking, throughput, or production SLO measurements.
"""
from __future__ import annotations
import json
import statistics
import tempfile
import time
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from naviqra.platform.core import PlatformStore


def measure(fn, iterations=250):
    samples=[]
    for _ in range(iterations):
        start=time.perf_counter()
        fn()
        samples.append((time.perf_counter()-start)*1000)
    ordered=sorted(samples)
    return {
        "iterations":iterations,
        "mean_ms":round(statistics.mean(samples),4),
        "p50_ms":round(statistics.median(samples),4),
        "p95_ms":round(ordered[int((len(ordered)-1)*0.95)],4),
        "max_ms":round(max(samples),4),
    }


def main():
    with tempfile.TemporaryDirectory() as tmp:
        store=PlatformStore(Path(tmp)/"bench.sqlite")
        for tier in ("profile","episodic","semantic","procedural","active"):
            store.put_memory("bench","traveler-1",tier,"sample",{"value":tier})
        store.vote("bench","group-1","m-1","candidate-a",0.9)
        store.vote("bench","group-1","m-2","candidate-a",0.8)
        results={
            "benchmark":"naviqra-platform-primitives",
            "version":"0.3.0",
            "environment":"local SQLite; no LLM or supplier calls",
            "memory_read":measure(lambda:store.get_memories("bench","traveler-1")),
            "group_consensus":measure(lambda:store.consensus("bench","group-1")),
            "graph_read":measure(lambda:store.graph("bench")),
        }
        print(json.dumps(results,indent=2))


if __name__ == "__main__":
    main()
