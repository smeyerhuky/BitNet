---
type: "PRD"
title: "PRD: Conversation Compactor Probe"
description: "Problem, question, and success criteria for the compactor probe."
resource: "projects/product/prds/compactor-probe.md"
tags: ["prd", "compactor", "bitnet", "product"]
timestamp: "2026-11-21"
status: "draft"
audience: "both"
scope: "project"
---

# PRD: Conversation Compactor Probe

Project: [bitnet-conversation-compactor](../../bitnet-conversation-compactor/index.md)

**Problem.** Long conversations resend the full system prompt, tools, notes, and history every turn. That costs tokens and dilutes attention.

**Question.** Can a small BitNet model, used as an in-line compactor, shorten the outgoing request while keeping the upstream answer as good as the uncompacted baseline?

**Success.** A compactor that cuts input tokens by a meaningful margin with no drop in blind-judge score, measured against the baseline with n@k runs.

**Out of scope for now.** Production serving, fine-tuning at scale, paid frontier APIs.

**Initial model and endpoint.** `google/gemma-4-31b-it` through the NVIDIA-hosted endpoint, to keep cost low. Upstream swap to OpenAI or Anthropic comes later.
