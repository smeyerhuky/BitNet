---
type: "Architecture"
title: "Workspace Layout"
description: "Folder model for the parent projects tree and each project."
resource: "projects/"
tags: ["architecture", "okf", "workspace", "bitnet"]
timestamp: "2026-11-21"
---

# Workspace Layout

The `projects/` folder is the parent. Every project is a folder under it with the same working set:

```
projects/
  index.md  CLAUDE.md
  architecture/ process/ product/ pdlc/ templates/ samples/
  journal/ specs/ research/ src/ test/ spikes/
  <project>/
    CLAUDE.md  index.md
    wiki/          the project KB (OKF bundle, no okf_version)
    journal/ specs/ research/ src/ test/ spikes/ runs/
```

Rules:

- The wiki is the durable explanation of the project. Specs say what to build, journals say what happened, runs hold raw data.
- Every folder carries an `index.md`. Those indexes are the table of contents an agent reads first.
- Cross-project decisions go in the parent folders and are linked from each project's wiki.
