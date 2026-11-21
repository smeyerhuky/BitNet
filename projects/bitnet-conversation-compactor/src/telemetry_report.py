"""Summarize telemetry: response fingerprints over time, header-name changes, and status counts."""
import collections
import json
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from src.telemetry import LOG  # noqa: E402

rows = [json.loads(l) for l in LOG.read_text().splitlines()] if LOG.exists() else []
print(f"calls logged: {len(rows)}")
print("status counts:", dict(collections.Counter(r["status"] for r in rows)))
fps = collections.Counter(r["response_fingerprint"] for r in rows)
print("response fingerprints:", dict(fps))
names = [tuple(r["header_names"]) for r in rows]
for i in range(1, len(names)):
    if names[i] != names[i - 1]:
        added = set(names[i]) - set(names[i - 1]); removed = set(names[i - 1]) - set(names[i])
        print(f"header change at call {i}: +{sorted(added)} -{sorted(removed)}")
rate_seen = collections.Counter(k for r in rows for k in r["rate_headers"])
print("rate-like headers seen:", dict(rate_seen) or "none")
