"""NVIDIA-hosted chat completions client (stdlib only).

The key is read from NVIDIA_API_KEY and is never stored or logged.
"""
import hashlib
import json
import os
import time
import urllib.request

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
    started = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        body = json.load(resp)
    latency = time.time() - started
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
