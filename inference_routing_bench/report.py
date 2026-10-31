"""Markdown comparison of router runs on the same trace: one column per router, best value in bold, and no bold
where the best is a tie at the precision shown.

With several repeats of a router, each cell is the median across them with the range beside it, and the best value
is picked by median: one run on a shared CI machine is an anecdote, the spread says how much to trust a difference.
"""
from __future__ import annotations

import statistics

from .compare import held, table
from .results import by_mode, comparable

# (label, getter, unit, lower is better)
ROWS = [
    ("TTFT p50", lambda r: r["summary"]["ttft_ms"]["p50"], "ms", True),
    ("TTFT p95", lambda r: r["summary"]["ttft_ms"]["p95"], "ms", True),
    ("TTFT p99", lambda r: r["summary"]["ttft_ms"]["p99"], "ms", True),
    ("End-to-end p95", lambda r: r["summary"]["e2e_ms"]["p95"], "ms", True),
    ("Time per output token p50", lambda r: r["summary"]["tpot_ms"]["p50"], "ms", True),
    ("Goodput (TTFT within objective)", lambda r: r["summary"]["goodput"], "%", False),
    ("Prefix-cache hit rate (from the pods)", lambda r: (r.get("pods") or {}).get("prefix_cache_hit_rate"), "%", False),
    ("Load balance across pods", lambda r: (r.get("pods") or {}).get("balance"), "", False),
    ("Output tokens per second", lambda r: r["summary"]["throughput"]["output_tokens_per_s"], "", False),
    ("Errors", lambda r: r["summary"]["errors"], "n", True),
]


def _fmt(value, unit: str) -> str:
    if value is None:
        return "n/a"
    if unit == "%":
        return f"{value * 100:.1f}%"
    if unit in ("ms", "n"):                           # a count's median is still shown as a count
        return f"{value:,.0f}"
    if isinstance(value, float):
        return f"{value:,.3f}" if value < 10 else f"{value:,.1f}"
    return f"{value:,}"


def _cell(values: list, unit: str) -> tuple[float | None, str]:
    """(median, text) for one router's repeats: the value itself for one run, median and range for several."""
    present = [v for v in values if v is not None]
    if not present:
        return None, "n/a"
    median = statistics.median(present)
    low, high = _fmt(min(present), unit), _fmt(max(present), unit)
    if low == high:                                  # one run, or runs that agree to the precision shown
        return median, _fmt(median, unit)
    return median, f"{_fmt(median, unit)} <sub>({low}–{high})</sub>"


def _row(label: str, get, unit: str, lower: bool, groups: list[tuple[str, list[dict]]]) -> str:
    cells = [_cell([get(r) for r in runs], unit) for _, runs in groups]
    medians = [m for m, _ in cells if m is not None]
    # Compared as shown: 16.9 and 17.2 ms both read 17, and bolding one of them would claim a difference nobody can see.
    best = _fmt(min(medians) if lower else max(medians), unit) if len({_fmt(m, unit) for m in medians}) > 1 else None
    cells = [f"**{text}**" if m is not None and _fmt(m, unit) == best else text for m, text in cells]
    hint = "lower is better" if lower else "higher is better"
    name = f"{label} ({unit})" if unit == "ms" else label
    return f"| {name} <sub>{hint}</sub> | " + " | ".join(cells) + " |"


def markdown(runs: list[dict], title: str | None = None) -> str:
    comparable(runs)
    groups = by_mode(runs)
    first = runs[0]
    summary = first["summary"]
    repeats = sorted({len(rs) for _, rs in groups})
    pods = {(r.get("cluster") or {}).get("model_server", {}).get("replicas") for r in runs} - {None}
    where = f" on {pods.pop()} simulated vLLM pods" if len(pods) == 1 else ""
    lines = [f"## {title or first['trace']['name']}: {first['trace']['requests']:,} requests{where}, TTFT objective {summary['ttft_slo_ms']:,} ms", ""]
    if repeats != [1]:
        lines += [f"Each cell is the median of {'/'.join(map(str, repeats))} runs per router, with the range in brackets; "
                  "every run had its own cluster and fresh model servers.", ""]
    lines += ["| Metric | " + " | ".join(m for m, _ in groups) + " |", "|---" * (len(groups) + 1) + "|"]
    lines += [_row(label, get, unit, lower, groups) for label, get, unit, lower in ROWS]
    kinds = [k for k in ("chat", "rag", "single") if all(k in r["by_kind"] for r in runs)]
    if kinds:
        lines += ["", "**TTFT p95 by kind of traffic (ms)**", "", "| Kind | " + " | ".join(m for m, _ in groups) + " |",
                  "|---" * (len(groups) + 1) + "|"]
        for k in kinds:
            lines.append(_row(k, lambda r, k=k: r["by_kind"][k]["ttft_ms"]["p95"], "ms", True, groups).replace(f"| {k} (ms) <sub>lower is better</sub>", f"| {k}"))
    if max(repeats) > 1:
        found = held(runs)
        lines += ["", "**Differences that held in every run both routers had**", ""]
        lines.append(table(found).rstrip("\n") if found else "None: no router was better than another in every shared run.")
    late = sorted({r["mode"] for r in runs if not r["summary"]["client"]["kept_up"]})
    if late:
        lines += ["", f"> The load client fell behind during: {', '.join(late)}. Those latencies include the client's own delay."]
    lines.append("")
    return "\n".join(lines)
