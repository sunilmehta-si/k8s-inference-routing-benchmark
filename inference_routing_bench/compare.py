"""Which differences between routers held in every run.

Runs with the same repeat number come from the same CI workflow run, whose jobs all start within minutes of each
other, so they share a time window. For each metric and each pair of routers this counts the repeats in which each one was better. A
difference "held" when one router was better in every repeat the two share, and there are at least two of them:
a single run can't tell a router's effect from the machine it happened to run on.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from .results import by_mode, comparable


def _kind_p95(kind: str):
    return lambda r: (r["by_kind"].get(kind) or {}).get("ttft_ms", {}).get("p95")


# (label, getter, unit, lower is better): the headline numbers a README might make a claim about.
METRICS = [
    ("TTFT p50", lambda r: r["summary"]["ttft_ms"]["p50"], "ms", True),
    ("TTFT p95", lambda r: r["summary"]["ttft_ms"]["p95"], "ms", True),
    ("TTFT p99", lambda r: r["summary"]["ttft_ms"]["p99"], "ms", True),
    ("Goodput", lambda r: r["summary"]["goodput"], "%", False),
    ("Prefix-cache hit rate", lambda r: (r.get("pods") or {}).get("prefix_cache_hit_rate"), "%", False),
    ("Load balance", lambda r: (r.get("pods") or {}).get("balance"), "", False),
    ("Chat TTFT p95", _kind_p95("chat"), "ms", True),
    ("RAG TTFT p95", _kind_p95("rag"), "ms", True),
    ("One-off TTFT p95", _kind_p95("single"), "ms", True),
]


@dataclass(frozen=True)
class Pair:
    metric: str
    unit: str
    a: str
    b: str
    a_better: int
    b_better: int
    repeats: int

    @property
    def ties(self) -> int:
        return self.repeats - self.a_better - self.b_better

    @property
    def winner(self) -> str | None:
        """The router that was better in every shared repeat, if there are at least two and one was."""
        if self.repeats < 2:
            return None
        if self.a_better == self.repeats:
            return self.a
        if self.b_better == self.repeats:
            return self.b
        return None


def pairs(runs: list[dict]) -> list[Pair]:
    """Every metric for every pair of routers, in report order, counted over the repeats both routers have."""
    comparable(runs)
    groups = by_mode(runs)
    out = []
    for label, get, unit, lower in METRICS:
        for (a, a_runs), (b, b_runs) in combinations(groups, 2):
            va = {r.get("repeat", 1): get(r) for r in a_runs}
            vb = {r.get("repeat", 1): get(r) for r in b_runs}
            shared = [n for n in sorted(va.keys() & vb.keys()) if va[n] is not None and vb[n] is not None]
            a_better = sum((va[n] < vb[n]) if lower else (va[n] > vb[n]) for n in shared)
            b_better = sum((vb[n] < va[n]) if lower else (vb[n] > va[n]) for n in shared)
            out.append(Pair(label, unit, a, b, a_better, b_better, len(shared)))
    return out


def held(runs: list[dict]) -> list[Pair]:
    """The pairs where one router was better in every shared repeat."""
    return [p for p in pairs(runs) if p.winner is not None]


def table(found: list[Pair]) -> str:
    """Markdown: one row per metric and pair, with how many shared repeats each router was better in."""
    lines = ["| Metric | Routers | Better in (runs) | Ties | Held by |", "|---|---|---|---|---|"]
    for p in found:
        lines.append(f"| {p.metric} | {p.a} vs {p.b} | {p.a} {p.a_better}, {p.b} {p.b_better} of {p.repeats} | "
                     f"{p.ties} | {p.winner or '–'} |")
    return "\n".join(lines) + "\n"
