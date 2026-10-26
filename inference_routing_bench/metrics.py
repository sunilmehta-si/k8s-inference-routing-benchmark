"""Summaries of a run: what users felt (TTFT, end-to-end), what the cluster did (throughput, errors), and whether the
client kept up.

Percentiles are nearest-rank over the requests that got an answer. Failed requests are counted separately rather
than averaged in, and goodput counts a failure as missing the objective, so a router can't look fast by dropping
the slow requests.
"""
from __future__ import annotations

import math

from .client import Result
from .trace import KINDS

# A client that started requests this much later than scheduled (p95) was itself the bottleneck; the run is not a
# measurement of the router.
MAX_CLIENT_LATENESS_S = 0.25


def pct(values: list[float], p: float) -> float | None:
    if not values:
        return None
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, max(0, math.ceil(p / 100 * len(ordered)) - 1))]


def _ms(value: float | None) -> float | None:
    return None if value is None else round(value * 1000, 1)


def summarize(results: list[Result], ttft_slo_s: float = 1.0) -> dict:
    ok = [r for r in results if r.ok]
    ttft = [r.ttft_s for r in ok]
    e2e = [r.e2e_s for r in ok]
    tpot = [(r.e2e_s - r.ttft_s) / (r.output_chunks - 1) for r in ok if r.output_chunks > 1]
    span = max((r.scheduled_s + r.lateness_s + (r.e2e_s or 0) for r in results), default=0.0) - min(
        (r.scheduled_s + r.lateness_s for r in results), default=0.0)
    lateness = pct([r.lateness_s for r in results], 95) or 0.0
    cached = [r for r in ok if r.cached_tokens is not None and r.prompt_tokens]
    out = {
        "requests": len(results),
        "ok": len(ok),
        "errors": len(results) - len(ok),
        "error_rate": round((len(results) - len(ok)) / len(results), 4) if results else 0.0,
        "ttft_ms": {"p50": _ms(pct(ttft, 50)), "p90": _ms(pct(ttft, 90)), "p95": _ms(pct(ttft, 95)), "p99": _ms(pct(ttft, 99)),
                    "mean": _ms(sum(ttft) / len(ttft)) if ttft else None},
        "e2e_ms": {"p50": _ms(pct(e2e, 50)), "p95": _ms(pct(e2e, 95))},
        "tpot_ms": {"p50": _ms(pct(tpot, 50)), "p95": _ms(pct(tpot, 95))},
        "throughput": {"requests_per_s": round(len(ok) / span, 2) if span > 0 else None,
                       "output_tokens_per_s": round(sum(r.output_chunks for r in ok) / span, 1) if span > 0 else None},
        "ttft_slo_ms": round(ttft_slo_s * 1000),
        "goodput": round(sum(1 for r in ok if r.ttft_s <= ttft_slo_s) / len(results), 4) if results else 0.0,
        "client": {"lateness_p95_ms": _ms(lateness), "kept_up": lateness <= MAX_CLIENT_LATENESS_S},
        "status_counts": {str(s): sum(1 for r in results if r.status == s) for s in sorted({r.status for r in results})},
    }
    if cached:
        out["server_cached_prompt_share"] = round(sum(r.cached_tokens for r in cached) / sum(r.prompt_tokens for r in cached), 4)
    return out


def by_kind(results: list[Result], ttft_slo_s: float = 1.0) -> dict:
    return {k: summarize([r for r in results if r.kind == k], ttft_slo_s) for k in KINDS if any(r.kind == k for r in results)}
