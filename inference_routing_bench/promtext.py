"""Read the model servers' own Prometheus counters, before and after a run.

The client sees latency; the servers see why. vLLM (and the simulator) count prompt tokens looked up in the prefix
cache and the ones found there, and the requests each pod served. Scraping every pod before and after a run and
subtracting gives, per router, the prefix-cache hit rate the cluster achieved and how evenly the load was spread.
"""
from __future__ import annotations

import re

SAMPLE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{[^}]*\})?\s+(\S+)")

HITS = "vllm:prefix_cache_hits_total"
QUERIES = "vllm:prefix_cache_queries_total"
SUCCESS = "vllm:request_success_total"
PROMPT_TOKENS = "vllm:prompt_tokens_total"


def parse(text: str) -> dict[str, float]:
    """Sum every sample of each metric across its labels: {name: value}."""
    totals: dict[str, float] = {}
    for line in text.splitlines():
        if not line or line.startswith("#"):
            continue
        m = SAMPLE.match(line)
        if not m:
            continue
        try:
            value = float(m.group(3))
        except ValueError:
            continue
        totals[m.group(1)] = totals.get(m.group(1), 0.0) + value
    return totals


def delta(before: dict[str, float], after: dict[str, float]) -> dict[str, float]:
    """after minus before for every counter; a pod that restarted (counter went down) counts from zero."""
    out = {}
    for name, value in after.items():
        prev = before.get(name, 0.0)
        out[name] = value - prev if value >= prev else value
    return out


def cluster_view(per_pod: dict[str, dict[str, float]]) -> dict:
    """From {pod: counter deltas}: the prefix-cache hit rate overall and per pod, and how the requests were spread."""
    pods = sorted(per_pod)
    served = {p: per_pod[p].get(SUCCESS, 0.0) for p in pods}
    total = sum(served.values())
    hits = sum(per_pod[p].get(HITS, 0.0) for p in pods)
    queries = sum(per_pod[p].get(QUERIES, 0.0) for p in pods)
    shares = [served[p] / total for p in pods] if total else []
    return {
        "pods": len(pods),
        "prefix_cache_hit_rate": round(hits / queries, 4) if queries else None,
        "requests_served": int(total),
        "per_pod": {p: {"requests": int(served[p]),
                        "prefix_cache_hit_rate": round(per_pod[p].get(HITS, 0.0) / per_pod[p][QUERIES], 4) if per_pod[p].get(QUERIES) else None}
                    for p in pods},
        # 1.0 is a perfectly even spread; 1/n means one pod served everything.
        "balance": round(1.0 / (len(pods) * max(shares)), 3) if shares and max(shares) > 0 else None,
    }
