"""Spike: how deterministic is the endpoint at seed 0?

Sends the same request N times, counts distinct reply hashes, and charges the
budget ledger. Writes a run record. Reads NVIDIA_API_KEY from the environment.
"""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import budget as B, records, upstream  # noqa: E402

N = 10
MESSAGES = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "What is 17 * 23? Answer with the number only."},
]

budget = B.Budget(ROOT / "runs" / "budget.json")
hashes, replies, usages = [], [], []
for i in range(N):
    out = upstream.call(MESSAGES, budget, temperature=0.5, seed=0, max_tokens=64)
    hashes.append(out["reply_sha256"])
    replies.append(out["reply"])
    usages.append(out["usage"])

distinct = len(set(hashes))
print(f"runs={N} distinct_reply_hashes={distinct}")
print("replies:", sorted(set(replies)))
print("usage sample:", usages[0])
print("cached_tokens reported:", [u.get("prompt_tokens_details", {}).get("cached_tokens") for u in usages])

records.append(ROOT / "runs" / "records.jsonl", {
    "run_id": "determinism-probe-001", "spec_version": "0.2", "parent_id": None,
    "mutation": "none (determinism probe)", "condition": "baseline",
    "model": upstream.DEFAULT_MODEL, "temperature": 0.5, "top_p": 1, "max_tokens": 64, "seed": 0,
    "input_tokens": usages[0].get("prompt_tokens"), "output_tokens": usages[0].get("completion_tokens"),
    "deterministic_pass": distinct == 1, "judge_score": None, "judge_prompt_version": None,
    "timestamp": records.now(), "distinct_reply_hashes": distinct, "n": N,
})
