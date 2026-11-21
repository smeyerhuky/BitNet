"""Adversarial variants (GAN search v0.3, section 1): decision wording shares no content words with the request.

merge_intervals_adv: search set.  chunk_list_adv: test set.
Reference solutions and tests are the originals; only the planted decision text changes.
"""
import copy
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(HERE))

from tasks_v2 import TASKS_V2  # noqa: E402
from build_v2 import build  # noqa: E402
from src.score import run_tests  # noqa: E402

ADV_DECISIONS = {
    "merge_intervals": "Every returned span must be the immutable pair form, the one that cannot be changed after it is created, because the serializer rejects anything mutable.",
    "chunk_list": "Every group handed to the batcher must be the immutable sequence form, never the mutable one. The overall return value is an ordinary list of those groups.",
}

TASKS = {t["id"]: t for t in TASKS_V2}
for base, decision in ADV_DECISIONS.items():
    task = copy.deepcopy(TASKS[base])
    task["id"] = f"{base}_adv"
    task["decision"] = decision
    ok_beh, _ = run_tests(task["ref"], task["tests"])
    ok_dec, _ = run_tests(task["ref"], task["ctest"])
    print(f"{task['id']:<22} reference behavior={ok_beh} decision={ok_dec}")
    assert ok_beh and ok_dec, task["id"]
    (HERE / "conversations_v2" / f"{task['id']}.json").write_text(json.dumps(build(task), indent=2) + "\n")
print("adversarial variants written")
