"""Read-only smoke checks for a deployed NAVIQRA API."""
from __future__ import annotations
import os
import sys
import urllib.error
import urllib.request

base = os.getenv("NAVIQRA_BASE_URL", "").rstrip("/")
tenant = os.getenv("NAVIQRA_TEST_TENANT_ID", "")
key = os.getenv("NAVIQRA_TEST_TENANT_KEY", "")
if not base.startswith("https://"):
    raise SystemExit("Set NAVIQRA_BASE_URL to the HTTPS deployment URL")
if not tenant or not key:
    raise SystemExit("Set NAVIQRA_TEST_TENANT_ID and NAVIQRA_TEST_TENANT_KEY")

def request(path: str, headers: dict[str, str] | None = None) -> tuple[int, dict[str, str], str]:
    req = urllib.request.Request(base + path, headers=headers or {})
    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            return response.status, dict(response.headers.items()), response.read().decode("utf-8")
    except urllib.error.HTTPError as exc:
        return exc.code, dict(exc.headers.items()), exc.read().decode("utf-8")

checks = []
def check(label: str, condition: bool, detail: str) -> None:
    checks.append((label, condition, detail))

status, headers, body = request("/health")
check("health", status == 200 and '"status":"ok"' in body.replace(" ", ""), f"HTTP {status}: {body[:160]}")
status, _, _ = request("/v1/platform/capabilities")
check("legacy v1 disabled", status == 404, f"HTTP {status}")
status, _, _ = request("/docs")
check("API docs disabled", status == 404, f"HTTP {status}")
status, _, _ = request(f"/v2/tenants/{tenant}/capabilities")
check("unauthenticated tenant request denied", status == 401, f"HTTP {status}")
status, headers, body = request(f"/v2/tenants/{tenant}/capabilities", {
    "X-Tenant-ID": tenant, "X-Tenant-Key": key,
})
check("tenant authentication", status == 200, f"HTTP {status}: {body[:160]}")
cache = next((v for k, v in headers.items() if k.lower() == "cache-control"), "")
check("authenticated responses not cacheable", "no-store" in cache.lower(), f"Cache-Control: {cache}")

for label, passed, detail in checks:
    print(("PASS" if passed else "FAIL") + f"  {label}: {detail}")
failed = sum(not passed for _, passed, _ in checks)
print(f"\n{len(checks)-failed}/{len(checks)} checks passed")
sys.exit(1 if failed else 0)
