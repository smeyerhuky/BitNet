"""Resumable sweep over the v2 corpus.

State lives in runs/sweep_state.json (written atomically). A run counts as done only when its
record is in runs/records.jsonl, so an interruption loses at most the call in flight. Restarting
skips done runs and retries failed ones. Progress lines go to runs/sweep.log.

Usage: python3 src/sweep.py [condition ...]   (default: retrieval keep_last_k structural, n=3)
"""
import json
import os
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import budget as B, conditions, records, retrieval, score, upstream  # noqa: E402

STATE = ROOT / "runs" / "sweep_state.json"
LOG = ROOT / "runs" / "sweep.log"
RECORDS = ROOT / "runs" / "records.jsonl"
CONV_DIR = ROOT / "corpus" / "conversations_v2"
LABEL_PREFIX = "v2-"
N_RUNS = 3
MAX_TRIES = 3
BUILDERS = {"keep_last_k": conditions.keep_last_k, "structural": conditions.structural}


def log(msg):
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def save_state(state):
    tmp = STATE.with_suffix(".tmp")
    tmp.write_text(json.dumps(state, indent=1))
    os.replace(tmp, STATE)  # atomic on POSIX: an interrupted write never leaves a half-written state


def done_ids():
    if not RECORDS.exists():
        return set()
    return {json.loads(l)["run_id"] for l in RECORDS.read_text().splitlines() if '"conversation"' in l}


def plan_for(conditions_wanted):
    convs = sorted(CONV_DIR.glob("*.json"))
    return [(c, conv_path, r) for c in conditions_wanted for conv_path in convs for r in range(N_RUNS)]


def main(conditions_wanted):
    budget = B.Budget(ROOT / "runs" / "budget.json")
    state = json.loads(STATE.read_text()) if STATE.exists() else {"runs": {}, "started": None}
    state.setdefault("started", time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    state["conditions"] = conditions_wanted
    jobs = plan_for(conditions_wanted)
    done = done_ids()
    todo = []
    for cond, conv_path, r in jobs:
        conv = json.loads(conv_path.read_text())
        rid = f"{LABEL_PREFIX}{cond}-{conv['id']}-r{r}"
        if rid in done:
            state["runs"][rid] = "done"
            continue
        if state["runs"].get(rid, {}).get("tries", 0) >= MAX_TRIES if isinstance(state["runs"].get(rid), dict) else False:
            continue  # gave up on this run in an earlier pass
        todo.append((cond, conv_path, r, rid))
    save_state(state)
    log(f"plan: {len(jobs)} runs, {len(jobs) - len(todo)} already done, {len(todo)} to do")

    retrieval_cache = {}
    for cond, conv_path, r, rid in todo:
        conv = json.loads(conv_path.read_text())
        key = (cond, conv["id"])
        if cond == "retrieval":
            if key not in retrieval_cache:
                retrieval_cache[key] = retrieval.build(conv, budget)[0]
            msgs = retrieval_cache[key]
        else:
            msgs = BUILDERS[cond](conv)

        entry = state["runs"].get(rid) if isinstance(state["runs"].get(rid), dict) else {"tries": 0}
        res = None
        for attempt in range(MAX_TRIES):
            try:
                res = upstream.call(msgs, budget, seed=0, temperature=0.5, max_tokens=1024)
                break
            except B.BudgetExceeded as e:
                log(f"stop: budget guard: {e}")
                state["stopped"] = str(e)
                save_state(state)
                return 2
            except Exception as e:  # network, rate limit or endpoint errors: back off and retry
                entry["tries"] = entry.get("tries", 0) + 1
                entry["last_error"] = str(e)[:200]
                state["runs"][rid] = entry
                save_state(state)
                wait = min(60, 5 * 2 ** attempt)
                log(f"retry {rid} attempt {attempt + 1}: {str(e)[:120]}; waiting {wait}s")
                time.sleep(wait)
        if res is None:
            state["runs"][rid] = dict(entry, status="failed")
            save_state(state)
            log(f"failed {rid} after {MAX_TRIES} attempts")
            continue

        s = score.score_reply(res["reply"], {"tests": conv["check"]["behavior_tests"], "ctest": conv["check"]["constraint_tests"]})
        out_dir = ROOT / "runs" / f"{LABEL_PREFIX}{cond}"
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{rid}.json").write_text(json.dumps({"reply": res["reply"], "usage": res["usage"], "score": s}, indent=2))
        records.append(RECORDS, {
            "run_id": rid, "spec_version": "0.2", "parent_id": None, "mutation": "none",
            "condition": f"{LABEL_PREFIX}{cond}", "model": upstream.DEFAULT_MODEL, "temperature": 0.5, "top_p": 1,
            "max_tokens": 1024, "seed": 0,
            "input_tokens": res["usage"].get("prompt_tokens"), "output_tokens": res["usage"].get("completion_tokens"),
            "deterministic_pass": s["behavior_pass"] and s["constraint_pass"], "judge_score": None,
            "judge_prompt_version": None, "timestamp": records.now(), "conversation": conv["id"],
            "behavior_pass": s["behavior_pass"], "constraint_pass": s["constraint_pass"],
            "cached_tokens": res["usage"].get("prompt_tokens_details", {}).get("cached_tokens", 0),
        })
        state["runs"][rid] = "done"
        save_state(state)
        n_done = sum(1 for v in state["runs"].values() if v == "done")
        log(f"done {rid} beh={s['behavior_pass']} dec={s['constraint_pass']} prompt={res['usage'].get('prompt_tokens')} "
            f"[{n_done}/{len(jobs)}] spent={budget.spent}")

    state["finished"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    save_state(state)
    log("sweep complete")
    return 0


if __name__ == "__main__":
    wanted = sys.argv[1:] or ["retrieval", "keep_last_k", "structural"]
    sys.exit(main(wanted))
