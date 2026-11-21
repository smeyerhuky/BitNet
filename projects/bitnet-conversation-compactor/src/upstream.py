"""NVIDIA-hosted chat completions client (stdlib only).

The key is read from NVIDIA_API_KEY and is never stored or logged.
"""
import hashlib
import json
import os
import time
import urllib.error
import urllib.request

from src import telemetry

MIN_INTERVAL_S = 60.0 / 40  # community-reported 40 requests per minute
_last_call = [0.0]

URL = "https://integrate.api.nvidia.com/v1/chat/completions"
DEFAULT_MODEL = "google/gemma-4-31b-it"


def call(messages, budget, model=DEFAULT_MODEL, temperature=0.5, top_p=1,
         max_tokens=1024, seed=0, logprobs=False, timeout=120):
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError("NVIDIA_API_KEY is not set")
    payload = {
        "model": model, "messages": messages, "max_tokens": max_tokens,
        "temperature": temperature, "top_p": top_p, "seed": seed,
        "frequency_penalty": 0, "presence_penalty": 0, "stream": False,
    }
    if logprobs:
        payload.update({"logprobs": True, "top_logprobs": 1})
    budget.check(max_tokens + _estimate_prompt_tokens(messages))
    req = urllib.request.Request(
        URL, data=json.dumps(payload).encode("utf-8"),
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                 "Accept": "application/json"},
    )
    wait = MIN_INTERVAL_S - (time.time() - _last_call[0])
    if wait > 0:
        time.sleep(wait)
    started = time.time()
    _last_call[0] = started
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = json.load(resp)
            headers = dict(resp.headers.items())
            status = resp.status
    except urllib.error.HTTPError as e:
        latency = time.time() - started
        telemetry.record(URL, e.code, payload, None, dict(e.headers.items()), latency, error=str(e.reason))
        raise
    latency = time.time() - started
    telemetry.record(URL, status, payload, body, headers, latency)
    choice = body["choices"][0]
    usage = body.get("usage") or {}
    budget.charge(usage.get("total_tokens", 0))
    reply = choice["message"]["content"] or ""
    return {
        "reply": reply,
        "reply_sha256": hashlib.sha256(reply.encode("utf-8")).hexdigest(),
        "finish_reason": choice.get("finish_reason"),
        "usage": usage,
        "logprobs": choice.get("logprobs"),
        "latency_s": round(latency, 3),
        "model": body.get("model", model),
    }


def _estimate_prompt_tokens(messages):
    # Rough pre-call guard only (about 4 characters per token). Real counts come from usage.
    return sum(len(m.get("content", "")) for m in messages) // 4 + 1


EMBED_URL = "https://integrate.api.nvidia.com/v1/embeddings"
EMBED_MODEL = "nvidia/nemotron-3.5-embed-8b"  # the only embedding model this key can reach (probed 2026-11-21)


def embed(texts, budget, input_type="passage", model=EMBED_MODEL, batch=16, timeout=120):
    """Return one embedding vector per text, in order. Charges prompt tokens to the budget."""
    key = os.environ.get("NVIDIA_API_KEY")
    if not key:
        raise RuntimeError("NVIDIA_API_KEY is not set")
    vectors = []
    for i in range(0, len(texts), batch):
        chunk = texts[i:i + batch]
        payload = {"model": model, "input": chunk, "input_type": input_type, "encoding_format": "float"}
        budget.check(sum(len(t) for t in chunk) // 3 + 1)
        req = urllib.request.Request(
            EMBED_URL, data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json",
                     "Accept": "application/json"},
        )
        wait = MIN_INTERVAL_S - (time.time() - _last_call[0])
        if wait > 0:
            time.sleep(wait)
        started = time.time()
        _last_call[0] = started
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                body = json.load(resp)
                headers = dict(resp.headers.items())
                status = resp.status
        except urllib.error.HTTPError as e:
            telemetry.record(EMBED_URL, e.code, payload, None, dict(e.headers.items()), time.time() - started, error=str(e.reason))
            raise
        telemetry.record(EMBED_URL, status, payload, body, headers, time.time() - started)
        budget.charge((body.get("usage") or {}).get("total_tokens", 0))
        vectors += [d["embedding"] for d in sorted(body["data"], key=lambda d: d["index"])]
    return vectors
