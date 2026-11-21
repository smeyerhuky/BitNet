---
type: "Architecture"
title: "Proxy Topology"
description: "Where the compactor sits in the request path and what passes through it."
resource: "projects/architecture/proxy-topology.md"
tags: ["architecture", "proxy", "compactor", "bitnet"]
timestamp: "2026-11-21"
---

# Proxy Topology

Target design for the first project. A compactor sits between the client and the upstream model API as an in-line proxy.

```
client (bot)  --turn n+1-->  [compactor proxy]  --compacted turn-->  upstream (OpenAI/Anthropic or NVIDIA-hosted Gemma)
                 <--reply--                       <--reply--
```

The compactor rewrites the outgoing conversation (system prompt, tools, notes, config, file bytes, and prior turns) into a shorter request. The upstream reply passes through unchanged, so the client sees a normal API.

Baseline first: until the proxy exists, we measure uncompacted append-style n+1 conversations and keep them as the reference. See [compactor concept](../bitnet-conversation-compactor/wiki/concepts/bitnet-compactor.md).
