"""Middleware telemetry for every endpoint call (stdlib only).

Logs one JSON line per call to runs/api_telemetry.jsonl:
- status, latency, error
- request shape (key paths and types) and a fingerprint
- response shape and fingerprint (first list element as representative)
- all response header names, plus values of rate-limit-like headers
Authorization and any key material are never logged.
"""
import hashlib
import json
import pathlib
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
LOG = ROOT / "runs" / "api_telemetry.jsonl"
RATE_HEADER_HINTS = ("ratelimit", "rate-limit", "retry", "quota", "limit", "remaining", "reset", "credit", "usage")
SECRET_HEADERS = {"authorization", "set-cookie"}


def shape(obj, prefix=""):
    out = set()
    if isinstance(obj, dict):
        for k, v in obj.items():
            p = f"{prefix}.{k}" if prefix else k
            out.add(f"{p}:{type(v).__name__}")
            out |= shape(v, p)
    elif isinstance(obj, list) and obj:
        out |= shape(obj[0], f"{prefix}[]")
    return out


def fingerprint(paths):
    return hashlib.sha256("\n".join(sorted(paths)).encode()).hexdigest()[:16]


def _headers(headers):
    names = sorted({k.lower() for k in headers.keys()} - SECRET_HEADERS)
    rate = {k.lower(): v for k, v in headers.items()
            if any(h in k.lower() for h in RATE_HEADER_HINTS)}
    return names, rate


def record(endpoint, status, request_body, response_body, headers, latency_s, error=None):
    req_paths = shape(request_body)
    resp_paths = shape(response_body) if response_body is not None else set()
    names, rate = _headers(headers or {})
    entry = {
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "endpoint": endpoint, "status": status, "latency_s": round(latency_s, 3), "error": error,
        "request_fingerprint": fingerprint(req_paths),
        "response_fingerprint": fingerprint(resp_paths),
        "response_paths": sorted(resp_paths),
        "header_names": names,
        "rate_headers": rate,
        "usage": (response_body or {}).get("usage") if isinstance(response_body, dict) else None,
    }
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, sort_keys=True) + "\n")
    return entry
