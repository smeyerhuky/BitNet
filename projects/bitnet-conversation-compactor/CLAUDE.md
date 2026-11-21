# bitnet-conversation-compactor — Working Notes for Claude Sessions

Question: can a BitNet model, run as an internal compression layer inside our API, shorten the conversation we send to an upstream API without hurting the answer?

## Where things are

- `wiki/` — the project KB (OKF bundle). Start at [wiki/index.md](wiki/index.md).
- `journal/` — daily, append-only.
- `specs/` — experiment protocol and record schema.
- `research/` — open questions.
- `src/` — compactor and harness code (empty for now).
- `test/` — tests (empty for now).
- `spikes/` — throwaway experiments. `nvidia_probe.py` checks the endpoint.
- `runs/` — raw run records (empty until baselines run).

## Rules

- Read the key from `NVIDIA_API_KEY`. Never write it into a file.
- Record every run with the schema in [specs/mutation-record-schema.md](specs/mutation-record-schema.md).
- Upstream is the NVIDIA-hosted `google/gemma-4-31b-it` for now. Keep the upstream behind one function so it can be swapped to OpenAI or Anthropic later.
- Push only to the fork's branch. See the parent [branching rules](../process/branching-and-remotes.md).
