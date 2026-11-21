---
type: "Template"
title: "Project Scaffold"
description: "Commands and files for starting a new project folder."
resource: "projects/templates/project-scaffold.md"
tags: ["template", "scaffold", "project"]
timestamp: "2026-11-21"
---

# Project Scaffold

Create a new project with:

```bash
P=projects/<name>
mkdir -p $P/{wiki/concepts,wiki/results,wiki/references,journal,specs,research,src,test,spikes,runs}
```

Then add: `CLAUDE.md`, `index.md`, one `index.md` per folder, and a first journal entry. Add the project to the parent `index.md`. Run the linter. The [sample setup](../samples/sample-project-setup.md) shows a finished example.
