"""Generate a high-entropy tenant API key and its server-side SHA-256 digest."""
import hashlib
import json
import secrets
import sys

if len(sys.argv) != 2:
    raise SystemExit("Usage: python scripts/generate_tenant_key.py <tenant-id>")
tenant = sys.argv[1]
if not tenant or len(tenant) > 128:
    raise SystemExit("tenant-id must contain 1..128 characters")
key = secrets.token_urlsafe(48)
digest = hashlib.sha256(key.encode("utf-8")).hexdigest()
print("CLIENT_TENANT_KEY=" + key)
print("SERVER_TENANT_KEY_HASHES=" + json.dumps({tenant: [digest]}, separators=(",", ":")))
print("Store CLIENT_TENANT_KEY in the client secret manager; store only SERVER_TENANT_KEY_HASHES in Render.")
