---
type: "Spec"
title: "Mutation Record Schema"
description: "Fields every run and mutation record must carry."
resource: "projects/bitnet-conversation-compactor/specs/mutation-record-schema.md"
tags: ["spec", "schema", "records", "mutation"]
timestamp: "2026-11-21"
status: "draft"
enforcement: "prescriptive"
audience: "agent"
scope: "project"
---

# Mutation Record Schema

One JSON object per run, appended to `runs/records.jsonl`:

```json
{"run_id": "string", "spec_version": "0.1", "parent_id": "string or null",
  "mutation": "description of the token change", "condition": "baseline or compacted",
  "model": "google/gemma-4-31b-it", "temperature": 0.5, "top_p": 1, "max_tokens": 1024, "seed": 0,
  "input_tokens": 0, "output_tokens": 0, "deterministic_pass": true,
  "judge_score": null, "judge_prompt_version": "string", "timestamp": "YYYY-MM-DD"}
```

Never store API keys or raw secrets in a record.
