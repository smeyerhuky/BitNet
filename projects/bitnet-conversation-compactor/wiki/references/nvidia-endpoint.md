---
type: "Reference"
title: "NVIDIA-Hosted Gemma Endpoint"
description: "Endpoint, model, parameters, and auth for the NVIDIA-hosted Gemma model."
resource: "https://integrate.api.nvidia.com/v1/chat/completions"
tags: ["reference", "nvidia", "gemma", "endpoint"]
timestamp: "2026-11-21"
---

# NVIDIA-Hosted Gemma Endpoint

Endpoint: `https://integrate.api.nvidia.com/v1/chat/completions` (OpenAI-compatible chat completions).

Model: `google/gemma-4-31b-it`.

Parameters used in the samples: `temperature` 0.5, `top_p` 1, `max_tokens` 1024, `seed` 0, `frequency_penalty` 0, `presence_penalty` 0, `stop` null.

Auth: `Authorization: Bearer $NVIDIA_API_KEY`. The key is read from the environment and is never written to a file. The key in use is temporary and will be rotated.

Verified 2026-11-21 with [the probe](../../spikes/index.md). See [spike result](../../spikes/nvidia-probe-result.md).
