---
type: "Template"
title: "Experiment Spec Template"
description: "Fields a spec must pin before a run."
resource: "projects/templates/experiment-spec.md"
tags: ["template", "spec", "experiment", "judging"]
timestamp: "2026-11-21"
---

# Experiment Spec Template

```yaml
# frontmatter as usual, plus:
spec_version: "0.1"
status: "draft"
```

Sections:

- **Hypothesis**: one sentence.
- **Conditions**: upstream model, compactor setting, temperature, top_p, max tokens, seed, and any invoke options. Pin every value.
- **Corpus**: which baseline conversations are used.
- **Scoring**: deterministic checks, blind judge prompt (version it), n@k setting.
- **Decision rule**: what result keeps or drops a mutation.
- **Records**: where the run files go and which schema they follow.
