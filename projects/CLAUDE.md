# projects/ — Working Notes for Claude Sessions

This is the parent folder for all research projects. It is an OKF bundle root (`index.md` declares `okf_version: "0.1"`). Each project under this folder owns its own knowledge base in `<project>/wiki/`.

## Layout

- `architecture/`, `process/`, `product/`, `pdlc/`, `templates/`, `samples/` — cross-project knowledge that applies to every project in this folder.
- `journal/`, `specs/`, `research/`, `src/`, `test/`, `spikes/` — cross-project working folders, same roles as in each project.
- `bitnet-conversation-compactor/` — the first project (BitNet as a conversation compactor).

## Conventions

- Every `.md` article (anything except `index.md`, `log.md`, `CLAUDE.md`) has OKF frontmatter: `type`, `title`, `description`, `resource`, `tags`, `timestamp` (ISO date).
- Only the root `index.md` declares `okf_version`.
- Every folder and subfolder has an `index.md` that lists each file with a one-line description.
- Optional domain fields (`status`, `enforcement`, `audience`, `disclosure_level`, `scope`) are used only on process/governance articles. Vocabulary:
  - `enforcement`: `prescriptive` (MUST/MUST NOT rules), `advisory` (SHOULD), `informational`.
  - `status`: `draft`, `review`, `finalized`, `deprecated`.
  - `scope`: `project`, `team`, `organization`, `universal`.
- Journal entries are append-only. New days get new files; never rewrite a past entry except to fix a factual error, and say so in the entry.

## Hard rules

- **Never push to the upstream repo this was forked from.** Work is committed and pushed only to `origin` (the fork) on the designated branch. Before any push, check `git remote -v`; if `upstream` exists, do not push to it. See [branching and remotes](process/branching-and-remotes.md).
- **Never write API keys into any file.** Keys are read from environment variables (`NVIDIA_API_KEY`). The NVIDIA key in use is temporary and will be rotated.

## How this tree was built

Scaffolded in one pass by a generator script, then linted with the OKF conformance checker (`~/.claude/skills/okf-wikify/scripts/lint_okf.py`). Articles were written by hand; the generator only handles frontmatter, index files, and file placement. Regenerate or extend by editing articles directly and re-running the linter.

## Lint

```bash
python3 ~/.claude/skills/okf-wikify/scripts/lint_okf.py /home/user/BitNet/projects
```
