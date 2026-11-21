"""Winner view data: generations of candidates, their scores, status, and changes from the closest earlier candidate.

Built from runs/gan (reply files carry genome and generation) and runs/gan/state.json (evaluations and
the split each one belongs to). Lineage is not recorded by the search, so each candidate is compared with
its closest candidate from the previous generation.
"""
import hashlib
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src import gan  # noqa: E402

GAN_DIR = ROOT / "runs" / "gan"
STATE = GAN_DIR / "state.json"
GENES = ["keep_last_k", "keep_first_k", "retrieval_k", "cos_threshold", "keep_set", "tools_keep", "files_keep", "notes_keep"]


def _gid(g):
    return hashlib.sha256(json.dumps(g, sort_keys=True).encode()).hexdigest()[:10]


def _changes(a, b):
    out = []
    for k in GENES:
        if a.get(k) != b.get(k):
            va, vb = a.get(k), b.get(k)
            if k == "keep_set":
                added = sorted(set(vb) - set(va)); removed = sorted(set(va) - set(vb))
                if added: out.append(f"keep +{added}")
                if removed: out.append(f"keep -{removed}")
            else:
                out.append(f"{k} {va}→{vb}")
    return out


def build():
    if not STATE.exists():
        return {"generations": [], "best": None}
    st = json.loads(STATE.read_text())
    evals = st.get("evals", {})
    genomes, gen_of, rids = {}, {}, {}
    for f in GAN_DIR.glob("gan-g*.json"):
        m = re.match(r"gan-g(\d+)-([0-9a-f]{10})-(.+)-r(\d+)\.json", f.name)
        if not m:
            continue
        gen, gid = int(m.group(1)), m.group(2)
        data = json.loads(f.read_text())
        genomes[gid] = data["genome"]
        gen_of[gid] = min(gen, gen_of.get(gid, gen))
        rids.setdefault(gid, []).append(f"gan-g{gen}-{gid}-{m.group(3)}-r{m.group(4)}")
    runs_by = {}
    for key, ev in evals.items():
        gid, cid, rep = key.split("|")
        runs_by.setdefault(gid, {}).setdefault(ev["split"], []).append(ev)
    cands = []
    for gid, g in genomes.items():
        splits = runs_by.get(gid, {})
        search = gan.score_runs(splits["search"]) if splits.get("search") else None
        sel = gan.score_runs(splits["selection"]) if splits.get("selection") else None
        cands.append({"id": gid, "gen": gen_of[gid], "genome": g, "search": search, "selection": sel,
                      "runs": sorted(rids.get(gid, []))})
    generations = []
    for gen in sorted({c["gen"] for c in cands}):
        cs = [c for c in cands if c["gen"] == gen]
        ranked = sorted([c for c in cs if c["search"]], key=lambda c: c["search"]["fitness"], reverse=True)
        elite = {c["id"] for c in ranked[:gan.ELITES]}
        promoted = {c["id"] for c in ranked[:gan.PROMOTE]}
        prev = [c for c in cands if c["gen"] == gen - 1]
        for c in cs:
            c["status"] = "elite" if c["id"] in elite else "promoted" if c["id"] in promoted else "dropped" if c["search"] else "pending"
            c["closest_prev"], c["changes"] = None, []
            if prev:
                best_prev = min(prev, key=lambda p: len(_changes(p["genome"], c["genome"])))
                c["closest_prev"], c["changes"] = best_prev["id"], _changes(best_prev["genome"], c["genome"])
        generations.append({"gen": gen, "candidates": sorted(cs, key=lambda c: (c["search"] or {"fitness": -99})["fitness"], reverse=True)})
    best = None
    for gen in generations:
        for c in gen["candidates"]:
            if c["selection"] and (best is None or c["selection"]["fitness"] > best["selection"]["fitness"]):
                best = c
    return {"generations": generations, "best": best["id"] if best else None,
            "best_history": st.get("best_hist", []), "gen_done": st.get("gen", 0)}


if __name__ == "__main__":
    w = build()
    print("generations:", [(g["gen"], len(g["candidates"])) for g in w["generations"]], "best:", w["best"])
