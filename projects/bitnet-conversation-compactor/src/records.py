"""Append-only run records (mutation-record-schema.md, extended per design v0.2 section 9)."""
import json
import pathlib
import time

REQUIRED = {"run_id", "spec_version", "parent_id", "mutation", "condition", "model",
            "temperature", "top_p", "max_tokens", "seed", "input_tokens", "output_tokens",
            "deterministic_pass", "judge_score", "judge_prompt_version", "timestamp"}


def append(path, record):
    missing = REQUIRED - record.keys()
    if missing:
        raise ValueError(f"record missing fields: {sorted(missing)}")
    path = pathlib.Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def now():
    return time.strftime("%Y-%m-%d", time.gmtime())
