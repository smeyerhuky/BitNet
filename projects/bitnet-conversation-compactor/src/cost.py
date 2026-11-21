"""Cache-aware cost model (design v0.2, section 2 and 3.1).

Prices are per 1M tokens and must be supplied by the caller. No prices are
hard-coded here: none are verified for the NVIDIA endpoint yet.
"""


def cached_aware_cost(usage, prices):
    """usage: dict with prompt_tokens, completion_tokens, and optionally cached_tokens.
    prices: dict with input, cached_input, output (per 1M tokens). Missing keys raise."""
    prompt = usage.get("prompt_tokens", 0)
    cached = min(usage.get("cached_tokens", 0), prompt)
    uncached = prompt - cached
    completion = usage.get("completion_tokens", 0)
    return (uncached * prices["input"] + cached * prices["cached_input"]
            + completion * prices["output"]) / 1_000_000


def simulate_prefix_cache(prompts):
    """Approximate provider prefix caching. prompts: list of token-id lists in request order.
    Returns, per request, the number of tokens that would hit the cache: the longest
    common prefix with any earlier request. Block granularity is ignored."""
    seen = []
    out = []
    for toks in prompts:
        best = 0
        for prev in seen:
            n = 0
            for a, b in zip(prev, toks):
                if a != b:
                    break
                n += 1
            best = max(best, n)
        out.append(best)
        seen.append(toks)
    return out
