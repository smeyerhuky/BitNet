"""Token budget ledger for NVIDIA endpoint calls (design v0.2, section 8.5).

Counts input plus output tokens. Halts at 80% of the phase cap and refuses any
single run above the per-run limit. State lives in runs/budget.json.
"""
import json
import pathlib

PHASE_CAP_TOKENS = 100_000_000  # local ledger only, not a provider quota; raised by owner, to be revisited on rate or quota limits
HALT_FRACTION = 0.8
PER_RUN_LIMIT = 50_000  # unchanged


class BudgetExceeded(RuntimeError):
    pass


class Budget:
    def __init__(self, path, cap=PHASE_CAP_TOKENS):
        self.path = pathlib.Path(path)
        self.cap = cap
        self.spent = 0
        if self.path.exists():
            self.spent = json.loads(self.path.read_text())["spent_tokens"]

    def check(self, estimated_tokens):
        if estimated_tokens > PER_RUN_LIMIT:
            raise BudgetExceeded(f"single run {estimated_tokens} exceeds per-run limit {PER_RUN_LIMIT}")
        if self.spent + estimated_tokens > HALT_FRACTION * self.cap:
            raise BudgetExceeded(f"would pass halt point: spent {self.spent} of cap {self.cap}")

    def charge(self, tokens):
        self.spent += tokens
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps({"spent_tokens": self.spent, "cap_tokens": self.cap}, indent=2) + "\n")

    @property
    def remaining(self):
        return self.cap - self.spent
