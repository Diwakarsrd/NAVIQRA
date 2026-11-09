from __future__ import annotations
import json
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class NaviqraClient:
    """Small stdlib-only SDK for the NAVIQRA v2 tenant API."""
    def __init__(self, base_url: str, tenant_id: str, tenant_key: str, timeout: float = 10):
        self.base_url = base_url.rstrip("/")
        self.tenant_id = tenant_id
        self.tenant_key = tenant_key
        self.timeout = timeout

    def _request(self, method: str, path: str, payload=None):
        body = None if payload is None else json.dumps(payload).encode()
        req = Request(self.base_url + path, data=body, method=method, headers={
            "Content-Type":"application/json", "X-Tenant-ID":self.tenant_id,
            "X-Tenant-Key":self.tenant_key
        })
        try:
            with urlopen(req, timeout=self.timeout) as response:
                return json.loads(response.read().decode())
        except HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            raise RuntimeError(f"NAVIQRA API {exc.code}: {detail}") from exc
        except URLError as exc:
            raise RuntimeError(f"Cannot connect to NAVIQRA API: {exc}") from exc

    def remember(self, traveler_id, tier, key, value):
        return self._request("POST", f"/v2/tenants/{self.tenant_id}/memory",
                             {"traveler_id":traveler_id,"tier":tier,"key":key,"value":value})

    def memories(self, traveler_id):
        return self._request("GET", f"/v2/tenants/{self.tenant_id}/memory/{traveler_id}")

    def add_graph_node(self, kind, label, properties=None):
        return self._request("POST", f"/v2/tenants/{self.tenant_id}/graph/nodes",
                             {"kind":kind,"label":label,"properties":properties or {}})

    def add_graph_edge(self, source, relation, target, properties=None):
        return self._request("POST", f"/v2/tenants/{self.tenant_id}/graph/edges",
                             {"source":source,"relation":relation,"target":target,
                              "properties":properties or {}})

    def run_agent(self, task_type, payload):
        return self._request("POST", f"/v2/tenants/{self.tenant_id}/agents/run",
                             {"task_type":task_type,"payload":payload})

    def vote(self, group_id, member_id, candidate_id, score, weight=1):
        return self._request("POST", f"/v2/tenants/{self.tenant_id}/groups/votes",
                             {"group_id":group_id,"member_id":member_id,
                              "candidate_id":candidate_id,"score":score,"weight":weight})

    def prepare_recovery(self, trip_id, disruption, options):
        return self.run_agent("recovery", {"trip_id":trip_id,"disruption":disruption,
                                           "options":options})
