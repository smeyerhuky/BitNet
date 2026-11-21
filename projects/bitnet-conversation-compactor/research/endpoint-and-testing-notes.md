---
type: "Research"
title: "Endpoint Surface, Quota Interpretation, and Mutation Testing"
description: "What the NVIDIA endpoint exposes (no OpenAPI spec found; model list and POST routes exist), how the 40 RPM figure applies, the telemetry middleware, and which mutation tester fits Python."
resource: "projects/bitnet-conversation-compactor/research/endpoint-and-testing-notes.md"
tags: ["research", "endpoint", "quota", "telemetry", "mutation-testing", "stryker", "mutmut"]
timestamp: "2026-11-21"
status: "draft"
---

# Endpoint Surface, Quota Interpretation, and Mutation Testing

## Endpoint surface (probed 2026-11-21)

- **No OpenAPI spec** at `/openapi.json`, `/v1/openapi.json`, `/openapi.yaml`, or `/docs` (all 404). The spec is not published at standard paths.
- **Model registry:** `GET /v1/models` returns an OpenAI-style list (200). It includes `google/gemma-4-31b-it` and about 30 other models.
- **Other POST routes:** `/v1/embeddings` and `/v1/completions` return 405 to GET, so they exist and expect POST. We haven't called them.
- **Health:** `GET /health` returns 200 with a gateway status object.
- **No usage or account route:** `/v1/usage`, `/v1/account`, and `/v1/me` return 404.
- **Response headers on success:** only `date`, `content-type`, `access-control-expose-headers`, `nvcf-reqid`, `nvcf-status`, `server`, `vary`, and `x-request-id`. No rate-limit headers were present.

## Quota interpretation

- The build site's **40 requests per minute** is a request-rate limit. It is not a token limit. The figure comes from community forum reports, not official documentation.
- NVIDIA publishes **no token limits** for the free endpoints that we could find.
- A third-party aggregator reports that, when free credits run out, requests fail with an authorization error rather than a throttle error. This is secondary and unconfirmed.
- Our client now throttles to one request every 1.5 seconds, which keeps us under 40 per minute.
- Our token cap (now 10,000,000) is a **local ledger** value that counts `total_tokens` from each response. It is not a provider quota. Real remaining quota has to come from the account page on build.nvidia.com.

## Telemetry middleware

- `src/telemetry.py` logs every call to `runs/api_telemetry.jsonl`: status, latency, error, request and response shape fingerprints, all header names, and rate-like header values. Authorization is never logged.
- `src/telemetry_report.py` summarizes fingerprint changes, header-name changes, status counts, and rate-like headers over time.
- Status: the middleware has logged its first call (200). Rate-limit or 429 behavior is still untested.

## Mutation testing

- **Stryker does not support Python.** The Stryker family covers JavaScript and TypeScript, plus C# and Scala. The search found no Python plugin.
- **Python options:** `mutmut` is a mutation tester for Python with an easy setup and can restrict mutations to covered lines. Cosmic Ray is a Python-specific alternative for Python 3.9+. MutPy is also named in a 2026 paper.
- **Plan:** use mutmut on `src/score.py`, `src/cost.py`, and `src/budget.py`, where bugs would silently corrupt results. One academic comparison found Cosmic Ray's competency score at 25.7%, and mutmut's result was inconclusive. That is a single data point, so we should test both on our own code before committing to one.

## Open items

- Test rate-limit behavior deliberately (a 429 path) and record the shape of the error response.
- Decide whether to log header values for every call or only rate-like headers.
- Fix the chunk_list decision wording before the next comparison (see the v2 baseline journal note).
