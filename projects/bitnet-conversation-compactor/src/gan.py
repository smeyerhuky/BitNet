"""Generational compactor search (GAN search v0.3).

Genome: a policy over one conversation's history, system notes, tools and files.
Fitness and stop rule as committed in specs/gan-search-v0.3.md. Every evaluation is a
checkpointed record, so an interrupted run resumes without repeating a call.

Usage:
  python3 src/gan.py run        # run (or resume) the search; stops at the stop rule or on errors
  python3 src/gan.py status     # print generation, best fitness, and call counts
"""
import hashlib
import json
import os
import pathlib
import random
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src import budget as B, conditions, records, retrieval, score, upstream  # noqa: E402

CONV_DIR = ROOT / "corpus" / "conversations_v2"
GAN_DIR = ROOT / "runs" / "gan"
STATE = GAN_DIR / "state.json"
LOG = GAN_DIR / "gan.log"
RECORDS = ROOT / "runs" / "records.jsonl"

SPLIT = {
    "search": ["reverse_words", "merge_intervals_adv", "slugify", "flatten", "roman_to_int", "binary_search"],
    "selection": ["is_palindrome", "parse_duration", "running_mean"],
    "test": ["chunk_list_adv", "dedupe_keep_order", "count_vowels"],
}
POP, ELITES, GENERATIONS, REPEATS_SEARCH, REPEATS_SELECT, PROMOTE = 8, 2, 6, 2, 3, 2
BASELINE_PROMPT = 3250
MIN_TOKENS = 150
MAX_ERRORS = 3
KEEP_LAST = (0, 8); KEEP_FIRST = (0, 4); RETR_K = (0, 12)


def log(msg):
    GAN_DIR.mkdir(parents=True, exist_ok=True)
    line = f"{time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())} {msg}"
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line, flush=True)


def score_runs(runs):
    """Fitness and summary for one candidate over its runs (spec v0.3, section 7). Shared with the winner view."""
    n = len(runs)
    beh = sum(x["behavior"] for x in runs) / n
    both = sum(x["behavior"] and x["decision"] for x in runs) / n
    tok = sum(x["prompt"] for x in runs) / n
    tok_ratio = tok / BASELINE_PROMPT
    gate = any(not x["decision"] for x in runs) or (tok < MIN_TOKENS and both < 1)
    f = (-10 + both - tok_ratio) if gate else (10 * beh - 5 * tok_ratio)
    return {"fitness": round(f, 4), "behavior": round(beh, 3), "both": round(both, 3), "tokens": round(tok), "gate": gate}


# ---------- genome ----------
FLOORS = [
    {"keep_last_k": 2, "keep_first_k": 0, "retrieval_k": 0, "cos_threshold": 0.0, "keep_set": [],
     "tools_keep": False, "files_keep": True, "notes_keep": True},   # keep-last-2 floor
    {"keep_last_k": 0, "keep_first_k": 0, "retrieval_k": 6, "cos_threshold": 0.0, "keep_set": [],
     "tools_keep": False, "files_keep": True, "notes_keep": True},   # retrieval floor
    {"keep_last_k": 0, "keep_first_k": 0, "retrieval_k": 0, "cos_threshold": 0.0, "keep_set": [],
     "tools_keep": False, "files_keep": True, "notes_keep": False},  # structural floor (no history)
]


def genome_id(g):
    return hashlib.sha256(json.dumps(g, sort_keys=True).encode()).hexdigest()[:10]


def random_genome(rng):
    return {"keep_last_k": rng.randint(*KEEP_LAST), "keep_first_k": rng.randint(*KEEP_FIRST),
            "retrieval_k": rng.randint(*RETR_K), "cos_threshold": round(rng.random() * 0.6, 3),
            "keep_set": sorted(rng.sample(range(40), rng.randint(0, 3))),
            "tools_keep": rng.random() < 0.3, "files_keep": True, "notes_keep": rng.random() < 0.8}


def mutate(parent, rng, others_idx):
    g = json.loads(json.dumps(parent))
    fired = False
    if rng.random() < 0.35:
        g["keep_last_k"] = min(KEEP_LAST[1], max(KEEP_LAST[0], g["keep_last_k"] + rng.choice([-1, 1]))); fired = True
    if rng.random() < 0.35:
        g["retrieval_k"] = min(RETR_K[1], max(RETR_K[0], g["retrieval_k"] + rng.choice([-2, -1, 1, 2]))); fired = True
    if rng.random() < 0.25:
        g["cos_threshold"] = round(min(1.0, max(0.0, g["cos_threshold"] + rng.gauss(0, 0.05))), 3); fired = True
    if rng.random() < 0.20:
        key = rng.choice(["tools_keep", "notes_keep"]); g[key] = not g[key]; fired = True
    if rng.random() < 0.25:
        candidates = [i for i in others_idx if i not in g["keep_set"]]
        if candidates:
            g["keep_set"] = sorted(g["keep_set"] + [rng.choice(candidates)]); fired = True
    if rng.random() < 0.15 and g["keep_set"]:
        g["keep_set"].remove(rng.choice(g["keep_set"])); fired = True
    if not fired:
        return mutate(parent, rng, others_idx)
    return g


def crossover(a, b, rng):
    return {k: (a[k] if rng.random() < 0.5 else b[k]) for k in a}


# ---------- compile a genome into messages ----------
def build_messages(conv, g, budget):
    history = conv["history"]
    n = len(history)
    keep = set()
    if g["keep_last_k"]:
        keep |= set(range(max(0, n - g["keep_last_k"]), n))
    if g["keep_first_k"]:
        keep |= set(range(min(g["keep_first_k"], n)))
    if g["retrieval_k"] or g["cos_threshold"]:
        vecs = retrieval._embed_cached([m["content"] for m in history], "passage", budget)
        q = retrieval._embed_cached([conv["request"]], "query", budget)[0]
        scored = sorted(((retrieval._cos(q, v), i) for i, v in enumerate(vecs)), reverse=True)
        top = [i for s, i in scored[:g["retrieval_k"]] if s >= g["cos_threshold"]] if g["retrieval_k"] else []
        keep |= set(top)
    keep |= {i for i in g["keep_set"] if 0 <= i < n}
    notes = "\n".join(f"- {x}" for x in conv["notes"])
    system = conv["system"] + ("\n\nNotes:\n" + notes if g["notes_keep"] else "")
    if g["tools_keep"]:
        system += "\n\nTools:\n" + "\n".join(json.dumps(t) for t in conv["tools"])
    msgs = [{"role": "system", "content": system}]
    msgs += [history[i] for i in sorted(keep)]
    files = conditions._file_text(conv) if g["files_keep"] else ""
    msgs.append({"role": "user", "content": (conv["request"] + ("\n\n" + files if files else ""))})
    return msgs, sorted(keep)


# ---------- evaluation with checkpointing ----------
class Search:
    def __init__(self):
        GAN_DIR.mkdir(parents=True, exist_ok=True)
        self.budget = B.Budget(ROOT / "runs" / "budget.json")
        self.state = json.loads(STATE.read_text()) if STATE.exists() else {"gen": 0, "pop": None, "evals": {}, "best_hist": [], "errors": 0}
        self.rng = random.Random(20261121)
        self.convs = {p.stem: json.loads(p.read_text()) for p in CONV_DIR.glob("*.json")}

    def save(self):
        GAN_DIR.mkdir(parents=True, exist_ok=True)
        tmp = STATE.with_suffix(".tmp"); tmp.write_text(json.dumps(self.state)); os.replace(tmp, STATE)

    def run_one(self, g, cid, rep, split, gen):
        key = f"{genome_id(g)}|{cid}|{rep}"
        if key in self.state["evals"]:
            return self.state["evals"][key]
        conv = self.convs[cid]
        msgs, kept = build_messages(conv, g, self.budget)
        for attempt in range(MAX_ERRORS):
            try:
                res = upstream.call(msgs, self.budget, seed=0, temperature=0.5, max_tokens=1024)
                self.state["errors"] = 0
                break
            except B.BudgetExceeded as e:
                raise SystemExit(f"budget guard: {e}")
            except Exception as e:
                self.state["errors"] += 1
                log(f"error {key} attempt {attempt + 1}: {str(e)[:120]}")
                self.save()
                if self.state["errors"] >= MAX_ERRORS:
                    raise SystemExit("stopping: three consecutive endpoint errors; checkpoint saved")
                time.sleep(min(60, 5 * 2 ** attempt))
        else:
            raise SystemExit("stopping after retries")
        s = score.score_reply(res["reply"], {"tests": conv["check"]["behavior_tests"], "ctest": conv["check"]["constraint_tests"]})
        out = {"behavior": s["behavior_pass"], "decision": s["constraint_pass"],
               "prompt": res["usage"].get("prompt_tokens", 0), "cached": res["usage"].get("prompt_tokens_details", {}).get("cached_tokens", 0),
               "kept": kept, "reply_sha": hashlib.sha256(res["reply"].encode()).hexdigest()[:12], "split": split}
        rid = f"gan-g{gen}-{genome_id(g)}-{cid}-r{rep}"
        (GAN_DIR / f"{rid}.json").write_text(json.dumps({"reply": res["reply"], "genome": g, "kept": kept}, indent=1))
        records.append(RECORDS, {"run_id": rid, "spec_version": "0.3", "parent_id": None, "mutation": "gan search",
                                 "condition": "gan", "model": upstream.DEFAULT_MODEL, "temperature": 0.5, "top_p": 1,
                                 "max_tokens": 1024, "seed": 0, "input_tokens": out["prompt"],
                                 "output_tokens": res["usage"].get("completion_tokens"),
                                 "deterministic_pass": out["behavior"] and out["decision"], "judge_score": None,
                                 "judge_prompt_version": None, "timestamp": records.now(), "conversation": cid,
                                 "behavior_pass": out["behavior"], "constraint_pass": out["decision"],
                                 "cached_tokens": out["cached"]})
        self.state["evals"][key] = out
        self.save()
        return out

    def fitness(self, g, cids, repeats, split, gen):
        runs = [self.run_one(g, cid, r, split, gen) for cid in cids for r in range(repeats)]
        return score_runs(runs)

    def generation(self):
        gen = self.state["gen"]
        if self.state["pop"] is None:
            pop = [dict(g) for g in FLOORS] + [random_genome(self.rng) for _ in range(POP - len(FLOORS))]
            self.state["pop"] = pop
            self.state["scores"] = {}
        pop = self.state["pop"]
        scores = self.state["scores"]
        for g in pop:
            gid = genome_id(g)
            if gid not in scores:
                scores[gid] = self.fitness(g, SPLIT["search"], REPEATS_SEARCH, "search", gen)
                log(f"gen {gen} {gid} search fitness {scores[gid]['fitness']} tokens {scores[gid]['tokens']} gate {scores[gid]['gate']}")
        ranked = sorted(pop, key=lambda g: scores[genome_id(g)]["fitness"], reverse=True)
        elites = ranked[:ELITES]
        promoted = ranked[:PROMOTE]
        for g in promoted:
            gid = genome_id(g)
            sel = self.fitness(g, SPLIT["selection"], REPEATS_SELECT, "selection", gen)
            scores[gid]["selection"] = sel
        best = max(promoted, key=lambda g: scores[genome_id(g)]["selection"]["fitness"])
        best_f = scores[genome_id(best)]["selection"]["fitness"]
        self.state["best_hist"].append(best_f)
        children = []
        idx = list(range(40))
        cross_slots = {0, 1}
        for i in range(POP - ELITES):
            a, b = self.rng.sample(elites, 2) if len(elites) > 1 else (elites[0], elites[0])
            child = crossover(a, b, self.rng) if i in cross_slots else dict(a)
            children.append(mutate(child, self.rng, idx))
        self.state["pop"] = elites + children
        self.state["gen"] = gen + 1
        self.state["scores"] = {genome_id(g): scores[genome_id(g)] for g in self.state["pop"] if genome_id(g) in scores}
        self.save()
        log(f"gen {gen} done: best selection fitness {best_f}")
        return best_f

    def stop_rule(self):
        h = self.state["best_hist"]
        if self.state["gen"] >= GENERATIONS:
            return "generation budget reached"
        if len(h) >= 3 and max(h[-2:]) - h[-3] < 0.1:
            return "no improvement of 0.1 for two generations"
        return None


def run():
    s = Search()
    log(f"search starting at generation {s.state['gen']}")
    while True:
        s.generation()
        reason = s.stop_rule()
        if reason:
            log(f"stopped: {reason}")
            break
    s.save()


def status():
    st = json.loads(STATE.read_text()) if STATE.exists() else {}
    print("generation:", st.get("gen"), "| evaluations:", len(st.get("evals", {})), "| best history:", st.get("best_hist"))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "status"
    {"run": run, "status": status}[cmd]()
