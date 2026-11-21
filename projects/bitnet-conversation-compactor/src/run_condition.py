"""Run one condition over the corpus, n times per conversation, and log scored records."""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import budget as B, conditions, records, retrieval, score, upstream  # noqa: E402

CONDITIONS = {"baseline": conditions.baseline, "keep_last_k": conditions.keep_last_k, "structural": conditions.structural}


def main(condition, n=3, corpus="v1"):
    budget = B.Budget(ROOT / "runs" / "budget.json")
    if condition == "retrieval":
        build = lambda conv: retrieval.build(conv, budget)[0]  # noqa: E731
    else:
        build = CONDITIONS[condition]
    conv_dir = ROOT / "corpus" / ("conversations_v2" if corpus == "v2" else "conversations")
    tag = "" if corpus == "v1" else "v2-"
    condition_label = f"{tag}{condition}"
    out_dir = ROOT / "runs" / condition_label
    out_dir.mkdir(parents=True, exist_ok=True)
    for path in sorted(conv_dir.glob("*.json")):
        conv = conditions.load_conversation(path)
        msgs = build(conv)
        for run in range(n):
            res = upstream.call(msgs, budget, seed=0, temperature=0.5, max_tokens=1024)
            s = score.score_reply(res["reply"], conv["check"] | {"tests": conv["check"]["behavior_tests"], "ctest": conv["check"]["constraint_tests"]})
            rid = f"{condition_label}-{conv['id']}-r{run}"
            (out_dir / f"{rid}.json").write_text(json.dumps({"reply": res["reply"], "usage": res["usage"], "score": s}, indent=2))
            records.append(ROOT / "runs" / "records.jsonl", {
                "run_id": rid, "spec_version": "0.2", "parent_id": None, "mutation": "none",
                "condition": condition_label, "model": upstream.DEFAULT_MODEL, "temperature": 0.5, "top_p": 1,
                "max_tokens": 1024, "seed": 0,
                "input_tokens": res["usage"].get("prompt_tokens"), "output_tokens": res["usage"].get("completion_tokens"),
                "deterministic_pass": s["behavior_pass"] and s["constraint_pass"], "judge_score": None,
                "judge_prompt_version": None, "timestamp": records.now(), "conversation": conv["id"],
                "behavior_pass": s["behavior_pass"], "constraint_pass": s["constraint_pass"],
                "cached_tokens": res["usage"].get("prompt_tokens_details", {}).get("cached_tokens", 0),
            })
            print(rid, "beh", s["behavior_pass"], "con", s["constraint_pass"], "prompt", res["usage"].get("prompt_tokens"), flush=True)


if __name__ == "__main__":
    main(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 3, sys.argv[3] if len(sys.argv) > 3 else "v1")
