# bitnet-conversation-compactor — Working Notes for Claude Sessions

Question: can a BitNet model, run as an internal compression layer inside our API, shorten the conversation we send to an upstream API without hurting the answer?

## Where things are

- `wiki/` — the project KB (OKF bundle). Start at [wiki/index.md](wiki/index.md).
- `corpus/` — coding conversations: v1 (planted constraint in file) and v2 (planted decision in early history). Built by `build.py` and `build_v2.py`.
- `src/` — harness: budget, upstream clients, conditions and floors, scoring, sweep, feed and publisher. See [src/index.md](src/index.md).
- `runs/` — raw records, sweep state, feed and context documents. See [runs/index.md](runs/index.md).
- `dashboard/` — the live run page.
- `specs/` — experiment protocol, design v0.2, GAN search v0.3, record schema.
- `journal/` — daily, append-only.
- `research/` — open questions and endpoint notes.
- `spikes/` — throwaway probes, including the browser check.
- `test/` — unit tests.

## Status (2026-11-21)

- Corpus v2 floor sweep complete: 108 runs. Retrieval passes all 36 at 373 prompt tokens; keep-last-2 and structural lose the planted decision.
- Run-watch page live. Store at feed version 8, synced by the session with ArtifactData after each checkpoint (no print-mode publishing).
- GAN search (spec v0.3) implemented in `src/gan.py`. Single-room end-to-end check passed: one candidate, one conversation, scored, recorded, shown in the feed.
- Adversarial variants built (`corpus/build_adv.py`): `merge_intervals_adv` (search), `chunk_list_adv` (test).

## Rules

- Read the key from `NVIDIA_API_KEY`. Never write it into a file.
- Record every run with the schema in [specs/mutation-record-schema.md](specs/mutation-record-schema.md).
- Upstream is the NVIDIA-hosted `google/gemma-4-31b-it` for now. Keep the upstream behind one function so it can be swapped to OpenAI or Anthropic later.
- Push only to the fork's branch. See the parent [branching rules](../process/branching-and-remotes.md).
