from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable
from uuid import uuid4

from naviqra.database import Database


def utcnow() -> str:
    return datetime.now(timezone.utc).isoformat()


class PlatformStore:
    """Tenant-scoped persistence for graph, memory, groups, runs and recovery cases."""

    def __init__(self, path: str | Path, *, initialize: bool = True):
        self.path = str(path)
        self.database = Database(self.path)
        if initialize:
            self._initialize()

    def _initialize(self):
        with self.connect() as db:
            db.executescript("""
            CREATE TABLE IF NOT EXISTS t_memory(
              tenant TEXT NOT NULL, traveler TEXT NOT NULL, tier TEXT NOT NULL,
              key TEXT NOT NULL, value TEXT NOT NULL, updated_at TEXT NOT NULL,
              PRIMARY KEY(tenant, traveler, tier, key));
            CREATE TABLE IF NOT EXISTS graph_nodes(
              tenant TEXT NOT NULL, id TEXT NOT NULL, kind TEXT NOT NULL,
              label TEXT NOT NULL, properties TEXT NOT NULL, created_at TEXT NOT NULL,
              PRIMARY KEY(tenant,id));
            CREATE TABLE IF NOT EXISTS graph_edges(
              tenant TEXT NOT NULL, id TEXT NOT NULL, source TEXT NOT NULL,
              relation TEXT NOT NULL, target TEXT NOT NULL, properties TEXT NOT NULL,
              created_at TEXT NOT NULL, PRIMARY KEY(tenant,id));
            CREATE INDEX IF NOT EXISTS idx_edges_source ON graph_edges(tenant,source);
            CREATE TABLE IF NOT EXISTS group_votes(
              tenant TEXT NOT NULL, group_id TEXT NOT NULL, member_id TEXT NOT NULL,
              candidate_id TEXT NOT NULL, score REAL NOT NULL, weight REAL NOT NULL,
              created_at TEXT NOT NULL,
              PRIMARY KEY(tenant,group_id,member_id,candidate_id));
            CREATE TABLE IF NOT EXISTS agent_runs(
              tenant TEXT NOT NULL, run_id TEXT NOT NULL, task_type TEXT NOT NULL,
              status TEXT NOT NULL, result TEXT, created_at TEXT NOT NULL,
              PRIMARY KEY(tenant,run_id));
            CREATE TABLE IF NOT EXISTS audit_events(
              tenant TEXT NOT NULL, event_id TEXT NOT NULL, actor TEXT NOT NULL,
              action TEXT NOT NULL, resource_type TEXT NOT NULL, resource_id TEXT NOT NULL,
              metadata TEXT NOT NULL, created_at TEXT NOT NULL,
              PRIMARY KEY(tenant,event_id));
            CREATE INDEX IF NOT EXISTS idx_audit_tenant_time ON audit_events(tenant,created_at);
            CREATE TABLE IF NOT EXISTS recovery_cases(
              tenant TEXT NOT NULL, case_id TEXT NOT NULL, trip_id TEXT NOT NULL,
              disruption TEXT NOT NULL, options TEXT NOT NULL, selected_option TEXT,
              status TEXT NOT NULL, created_at TEXT NOT NULL,
              PRIMARY KEY(tenant,case_id));
            """)

    def connect(self):
        return self.database.connect()

    def check(self):
        self.database.check()
        with self.connect() as db:
            db.execute("SELECT 1 FROM t_memory LIMIT 1").fetchone()

    def put_memory(self, tenant: str, traveler: str, tier: str, key: str, value: Any):
        allowed = {"profile", "episodic", "semantic", "procedural", "active"}
        if tier not in allowed:
            raise ValueError("tier must be one of " + ", ".join(sorted(allowed)))
        with self.connect() as db:
            db.execute("""INSERT INTO t_memory VALUES(?,?,?,?,?,?)
              ON CONFLICT(tenant,traveler,tier,key) DO UPDATE SET
              value=excluded.value,updated_at=excluded.updated_at""",
              (tenant, traveler, tier, key, json.dumps(value), utcnow()))
        return {"tenant_id": tenant, "traveler_id": traveler, "tier": tier,
                "key": key, "value": value}

    def get_memories(self, tenant: str, traveler: str):
        with self.connect() as db:
            rows = db.execute("""SELECT tier,key,value,updated_at FROM t_memory
              WHERE tenant=? AND traveler=? ORDER BY updated_at DESC""",
              (tenant, traveler)).fetchall()
        return [{"tier": r["tier"], "key": r["key"], "value": json.loads(r["value"]),
                 "updated_at": r["updated_at"]} for r in rows]

    def add_node(self, tenant: str, kind: str, label: str, properties: dict[str, Any]):
        node_id = str(uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO graph_nodes VALUES(?,?,?,?,?,?)",
                       (tenant,node_id,kind,label,json.dumps(properties),utcnow()))
        return {"id": node_id, "kind": kind, "label": label, "properties": properties}

    def add_edge(self, tenant: str, source: str, relation: str, target: str,
                 properties: dict[str, Any] | None = None):
        edge_id = str(uuid4())
        with self.connect() as db:
            exists = db.execute("""SELECT COUNT(*) n FROM graph_nodes
                WHERE tenant=? AND id IN (?,?)""", (tenant,source,target)).fetchone()["n"]
            if exists != 2:
                raise ValueError("both graph endpoints must exist in this tenant")
            db.execute("INSERT INTO graph_edges VALUES(?,?,?,?,?,?,?)",
                       (tenant,edge_id,source,relation,target,json.dumps(properties or {}),utcnow()))
        return {"id": edge_id, "source": source, "relation": relation, "target": target,
                "properties": properties or {}}

    def graph(self, tenant: str, limit: int = 100):
        with self.connect() as db:
            nodes = db.execute("SELECT * FROM graph_nodes WHERE tenant=? ORDER BY created_at DESC LIMIT ?",
                               (tenant,limit)).fetchall()
            edges = db.execute("SELECT * FROM graph_edges WHERE tenant=? ORDER BY created_at DESC LIMIT ?",
                               (tenant,limit)).fetchall()
        return {
            "nodes": [{"id":r["id"],"kind":r["kind"],"label":r["label"],
                       "properties":json.loads(r["properties"])} for r in nodes],
            "edges": [{"id":r["id"],"source":r["source"],"relation":r["relation"],
                       "target":r["target"],"properties":json.loads(r["properties"])} for r in edges]
        }

    def vote(self, tenant: str, group_id: str, member_id: str, candidate_id: str,
             score: float, weight: float = 1.0):
        if not 0 <= score <= 1 or not 0 < weight <= 10:
            raise ValueError("score must be 0..1 and weight must be >0..10")
        with self.connect() as db:
            db.execute("""INSERT INTO group_votes VALUES(?,?,?,?,?,?,?)
              ON CONFLICT(tenant,group_id,member_id,candidate_id) DO UPDATE SET
              score=excluded.score,weight=excluded.weight,created_at=excluded.created_at""",
              (tenant,group_id,member_id,candidate_id,score,weight,utcnow()))
        return self.consensus(tenant, group_id)

    def consensus(self, tenant: str, group_id: str):
        with self.connect() as db:
            rows = db.execute("""SELECT candidate_id, SUM(score*weight)/SUM(weight) AS score,
              COUNT(DISTINCT member_id) AS voters FROM group_votes
              WHERE tenant=? AND group_id=? GROUP BY candidate_id ORDER BY score DESC,candidate_id""",
              (tenant,group_id)).fetchall()
        return {"group_id":group_id,"ranked_candidates":[
            {"candidate_id":r["candidate_id"],"score":round(r["score"],4),"voters":r["voters"]}
            for r in rows]}

    def save_run(self, tenant: str, run_id: str, task_type: str, status: str, result: Any):
        with self.connect() as db:
            db.execute("INSERT INTO agent_runs VALUES(?,?,?,?,?,?)",
                       (tenant,run_id,task_type,status,json.dumps(result),utcnow()))

    def create_recovery(self, tenant: str, trip_id: str, disruption: str,
                        options: list[dict[str, Any]]):
        case_id = str(uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO recovery_cases VALUES(?,?,?,?,?,?,?,?)",
                       (tenant,case_id,trip_id,disruption,json.dumps(options),None,"awaiting_selection",utcnow()))
        return {"case_id":case_id,"trip_id":trip_id,"disruption":disruption,
                "options":options,"status":"awaiting_selection","requires_human_confirmation":True}

    def audit(self, tenant: str, actor: str, action: str, resource_type: str,
              resource_id: str, metadata: dict[str, Any] | None = None):
        event_id = str(uuid4())
        with self.connect() as db:
            db.execute("INSERT INTO audit_events VALUES(?,?,?,?,?,?,?,?)",
                       (tenant,event_id,actor,action,resource_type,resource_id,
                        json.dumps(metadata or {}, sort_keys=True),utcnow()))
        return {"event_id":event_id,"actor":actor,"action":action,
                "resource_type":resource_type,"resource_id":resource_id}

    def audit_events(self, tenant: str, limit: int = 100):
        with self.connect() as db:
            rows = db.execute("SELECT * FROM audit_events WHERE tenant=? ORDER BY created_at DESC LIMIT ?",
                              (tenant,limit)).fetchall()
        return [{"event_id":r["event_id"],"actor":r["actor"],"action":r["action"],
                 "resource_type":r["resource_type"],"resource_id":r["resource_id"],
                 "metadata":json.loads(r["metadata"]),"created_at":r["created_at"]} for r in rows]

    def delete_traveler(self, tenant: str, traveler: str):
        with self.connect() as db:
            cursor = db.execute("DELETE FROM t_memory WHERE tenant=? AND traveler=?", (tenant,traveler))
            deleted = cursor.rowcount
        self.audit(tenant,"tenant_api","privacy.delete_traveler_memory","traveler",traveler,
                   {"memory_records_deleted":deleted})
        return {"tenant_id":tenant,"traveler_id":traveler,"memory_records_deleted":deleted}


@dataclass
class Agent:
    name: str
    handler: Callable[[dict[str, Any]], dict[str, Any]]


class AgentRuntime:
    """Deterministic, auditable workflow runtime; LLM/provider execution is an explicit adapter."""
    def __init__(self, store: PlatformStore):
        self.store = store
        self.agents: dict[str, Agent] = {
            "travel_intelligence": Agent("travel_intelligence", self._intelligence),
            "group_consensus": Agent("group_consensus", self._consensus),
            "recovery": Agent("recovery", self._recovery),
        }

    def execute(self, tenant: str, task_type: str, payload: dict[str, Any]):
        if task_type not in self.agents:
            raise ValueError("unsupported task_type")
        run_id = str(uuid4())
        try:
            result = self.agents[task_type].handler({"tenant_id":tenant, **payload})
            self.store.save_run(tenant,run_id,task_type,"succeeded",result)
            return {"run_id":run_id,"agent":task_type,"status":"succeeded","result":result}
        except (ValueError, KeyError, TypeError) as exc:
            self.store.save_run(tenant,run_id,task_type,"failed",{"error":str(exc)})
            raise

    def _intelligence(self, p):
        traveler = p.get("traveler_id")
        if not traveler:
            raise ValueError("traveler_id is required")
        return {"traveler_id":traveler,"memory":self.store.get_memories(p["tenant_id"],traveler),
                "graph":self.store.graph(p["tenant_id"],limit=50)}

    def _consensus(self, p):
        if not p.get("group_id"):
            raise ValueError("group_id is required")
        return self.store.consensus(p["tenant_id"],p["group_id"])

    def _recovery(self, p):
        trip_id, disruption = p.get("trip_id"), p.get("disruption")
        options = p.get("options")
        if not trip_id or not disruption or not isinstance(options,list) or not options:
            raise ValueError("trip_id, disruption and non-empty options are required")
        return self.store.create_recovery(p["tenant_id"],trip_id,disruption,options)
