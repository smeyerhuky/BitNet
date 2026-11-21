"""End-to-end probe: corpus -> conditions -> embeddings -> chat -> scoring -> records -> telemetry -> budget.

Runs baseline and retrieval on two v2 conversations with n=1, then checks every stage automatically
and prints a PASS/FAIL checklist. Writes to a separate probe directory so the real runs are untouched.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import budget as B, conditions, retrieval, score, telemetry, upstream  # noqa: E402

PROBE_DIR = ROOT / "runs" / "probe"
CONVS = ["parse_duration", "roman_to_int"]
results = []


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"[{'PASS' if ok else 'FAIL'}] {name} {detail}")


def telemetry_rows():
    return sum(1 for _ in telemetry.LOG.open()) if telemetry.LOG.exists() else 0


def main():
    PROBE_DIR.mkdir(parents=True, exist_ok=True)
    budget = B.Budget(ROOT / "runs" / "budget.json")
    before_spent, before_rows = budget.spent, telemetry_rows()
    out = {}
    for cid in CONVS:
        conv = conditions.load_conversation(ROOT / "corpus" / "conversations_v2" / f"{cid}.json")
        base_msgs = conditions.baseline(conv)
        ret_msgs, kept = retrieval.build(conv, budget)
        for label, msgs in [("baseline", base_msgs), ("retrieval", ret_msgs)]:
            res = upstream.call(msgs, budget, seed=0, temperature=0.5, max_tokens=1024)
            s = score.score_reply(res["reply"], {"tests": conv["check"]["behavior_tests"],
                                                 "ctest": conv["check"]["constraint_tests"]})
            out[(cid, label)] = (res, s, kept if label == "retrieval" else None)
            (PROBE_DIR / f"{label}-{cid}.json").write_text(json.dumps({"reply": res["reply"], "score": s}, indent=2))

    check("chat calls return text", all(v[0]["reply"] for v in out.values()))
    check("scoring returns both flags", all(set(v[1]) >= {"behavior_pass", "constraint_pass"} for v in out.values()))
    check("retrieval keeps fewer history messages than baseline",
          all(len(out[(c, "retrieval")][2]) < len(conditions.load_conversation(
              ROOT / "corpus" / "conversations_v2" / f"{c}.json")["history"]) for c in CONVS))
    cache = json.loads(retrieval.CACHE.read_text()) if retrieval.CACHE.exists() else {}
    check("embedding cache populated", len(cache) > 0, f"({len(cache)} entries)")
    check("embedding vectors are 4096-d", all(len(v) == 4096 for v in list(cache.values())[:5]))
    check("telemetry rows added", telemetry_rows() > before_rows, f"(+{telemetry_rows() - before_rows})")
    check("budget charged for this probe", budget.spent > before_spent, f"(+{budget.spent - before_spent} tokens)")
    check("budget under cap", budget.spent < budget.cap)
    check("no key material in telemetry",
          "nvapi-" not in (telemetry.LOG.read_text() if telemetry.LOG.exists() else ""))

    print("\nper-call summary:")
    for (cid, label), (res, s, kept) in out.items():
        print(f"  {cid:<15} {label:<10} beh={s['behavior_pass']} con={s['constraint_pass']} "
              f"prompt={res['usage'].get('prompt_tokens')} cached={res['usage'].get('prompt_tokens_details', {}).get('cached_tokens')}")
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)}/{len(results)} checks passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
