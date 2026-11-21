---
type: "Spike"
title: "Determinism Probe"
description: "Same request ten times at seed 0 and temperature 0.5: one distinct reply; cached prompt tokens appear from the ninth call."
resource: "projects/bitnet-conversation-compactor/spikes/determinism_probe.py"
tags: ["spike", "determinism", "nvidia", "caching", "cost-model"]
timestamp: "2026-11-21"
---

# Determinism Probe

Script: `determinism_probe.py`. Ten identical requests to `google/gemma-4-31b-it` with the spec's pinned parameters (temperature 0.5, top_p 1, seed 0, max tokens 64).

**Result.** One distinct reply hash across all ten calls (reply `391`). Usage on the first call: 52 prompt tokens, 4 completion tokens.

**Caching.** `prompt_tokens_details.cached_tokens` was 0 for calls 1 to 8 and 32 for calls 9 and 10. So the endpoint does prefix caching, and it warms only after several repeats. Cost measurements must therefore count cached reads explicitly, and an uncached-only baseline will overstate cost.

**Limits of this result.** One prompt, one short answer. It does not show determinism on long answers or across days, so the daily sentinel re-run from the review still applies.

**Budget.** About 560 tokens charged to the phase ledger.
