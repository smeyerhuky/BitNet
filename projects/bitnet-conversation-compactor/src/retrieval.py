"""Retrieval floor (P3): keep the system text, notes, file bytes and request, plus only the k history
messages most similar to the request by embedding cosine. No learning, no LLM summarizing."""
import hashlib
import json
import math
import pathlib

from src import conditions, upstream

ROOT = pathlib.Path(__file__).resolve().parents[1]
CACHE = ROOT / "runs" / "embed_cache.json"


def _load_cache():
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _key(text, input_type):
    return hashlib.sha256((input_type + "\x00" + text).encode()).hexdigest()


def _embed_cached(texts, input_type, budget):
    cache = _load_cache()
    missing = [t for t in texts if _key(t, input_type) not in cache]
    if missing:
        for t, v in zip(missing, upstream.embed(missing, budget, input_type=input_type)):
            cache[_key(t, input_type)] = v
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        CACHE.write_text(json.dumps(cache))
    return [cache[_key(t, input_type)] for t in texts]


def _cos(a, b):
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def build(conv, budget, k=6):
    history = conv["history"]
    contents = [m["content"] for m in history]
    hist_vecs = _embed_cached(contents, "passage", budget)
    query_vec = _embed_cached([conv["request"]], "query", budget)[0]
    scores = [_cos(query_vec, v) for v in hist_vecs]
    keep = sorted(sorted(range(len(history)), key=lambda i: scores[i], reverse=True)[:k])
    notes = "\n".join(f"- {n}" for n in conv["notes"])
    msgs = [{"role": "system", "content": f"{conv['system']}\n\nNotes:\n{notes}"}]
    msgs += [history[i] for i in keep]
    msgs.append({"role": "user", "content": f"{conv['request']}\n\n{conditions._file_text(conv)}"})
    return msgs, keep
