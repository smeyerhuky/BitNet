---
type: "Spike"
title: "NVIDIA Probe Result"
description: "Endpoint probe verified: HTTP 200, correct answer, usage recorded."
resource: "projects/bitnet-conversation-compactor/spikes/nvidia-probe-result.md"
tags: ["spike", "nvidia", "endpoint", "verified"]
timestamp: "2026-11-21"
---

# NVIDIA Probe Result

Script: `nvidia_probe.py` in this folder. It reads `NVIDIA_API_KEY` from the environment and sends one chat completion.

Result on 2026-11-21: HTTP 200. Model `google/gemma-4-31b-it`. Reply `17 * 23 = 391`. Usage 46 prompt tokens, 12 completion tokens.

The key was supplied in-session, is temporary, and was not written to any file.
