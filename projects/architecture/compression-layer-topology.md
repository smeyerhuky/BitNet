---
type: "Architecture"
title: "Compression Layer Topology"
description: "Where the compactor sits in the request path and what passes through it."
resource: "projects/architecture/compression-layer-topology.md"
tags: ["architecture", "compression-layer", "compactor", "bitnet"]
timestamp: "2026-11-21"
---

# Compression Layer Topology

The compression layer is an internal stage inside our own API, not a network proxy or a man-in-the-middle. It runs in the request path after the conversation is assembled and before the upstream call. Nothing outside our service sees it.

```
our API: assemble full request (system, tools, notes, config, files, history)
   -> compression layer: choose minimal context C' (span selection / rewrite)
   -> upstream call with C' (Gemma now; OpenAI or Anthropic later)
   -> reply returned to the caller unchanged
```

The upstream is a black box and is never trained. Only the compression layer changes, and it can be switched off to get the baseline path.

Baseline first: until the compression layer exists, we measure uncompacted append-style n+1 conversations and keep them as the reference. See [compactor concept](../bitnet-conversation-compactor/wiki/concepts/bitnet-compactor.md).
