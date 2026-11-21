---
type: "Concept"
title: "Conversation Composition"
description: "The parts of a request and why appending every turn costs tokens."
resource: "projects/bitnet-conversation-compactor/wiki/concepts/conversation-composition.md"
tags: ["concept", "conversation", "baseline", "tokens"]
timestamp: "2026-11-21"
---

# Conversation Composition

An upstream LLM call is more than the messages. A request carries:

- system prompt
- tool definitions and their schemas
- notes and memory blocks
- config: temperature, top_p, max tokens, seed, stop, penalties
- special features (structured output, reasoning flags)
- file bytes, maps, skill text

Append-style n+1 conversations resend all of it every turn plus the full history. The first turn is:

```
User: Hello!
Assistant: how are you..
```

Turn n+1 is the same prefix plus the new user message. The cost grows with every turn, and so does the chance that old detail drowns out the trigger for the current turn.

The baseline measures this full composition unchanged, so every later result can be compared against it. See [compactor](bitnet-compactor.md).
