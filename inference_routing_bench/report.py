"""Markdown comparison of router runs on the same trace: one column per router, best value in bold."""
from __future__ import annotations

from .results import comparable

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
    ("Errors", lambda r: r["summary"]["errors"], "", True),
]


def _fmt(value, unit: str) -> str:
    if value is None:
        return "n/a"
    if unit == "%":
        return f"{value * 100:.1f}%"
    if unit == "ms":
        return f"{value:,.0f}"
    if isinstance(value, float):
        return f"{value:,.3f}" if value < 10 else f"{value:,.1f}"
    return f"{value:,}"


def _row(label: str, get, unit: str, lower: bool, runs: list[dict]) -> str:
    values = [get(r) for r in runs]
    present = [v for v in values if v is not None]
    best = (min(present) if lower else max(present)) if present and len(set(present)) > 1 else None
    cells = [f"**{_fmt(v, unit)}**" if v is not None and v == best else _fmt(v, unit) for v in values]
    hint = "lower is better" if lower else "higher is better"
    name = f"{label} ({unit})" if unit == "ms" else label
    return f"| {name} <sub>{hint}</sub> | " + " | ".join(cells) + " |"


def markdown(runs: list[dict], title: str | None = None) -> str:
    comparable(runs)
    first = runs[0]
    summary = first["summary"]
    lines = [f"## {title or first['trace']['name']}: {first['trace']['requests']:,} requests, TTFT objective {summary['ttft_slo_ms']:,} ms", ""]
    lines += ["| Metric | " + " | ".join(r["mode"] for r in runs) + " |", "|---" * (len(runs) + 1) + "|"]
    lines += [_row(label, get, unit, lower, runs) for label, get, unit, lower in ROWS]
    kinds = [k for k in ("chat", "rag", "single") if all(k in r["by_kind"] for r in runs)]
    if kinds:
        lines += ["", "**TTFT p95 by kind of traffic (ms)**", "", "| Kind | " + " | ".join(r["mode"] for r in runs) + " |",
                  "|---" * (len(runs) + 1) + "|"]
        for k in kinds:
            lines.append(_row(k, lambda r, k=k: r["by_kind"][k]["ttft_ms"]["p95"], "", True, runs).replace(f"| {k} <sub>lower is better</sub>", f"| {k}"))
    late = [r["mode"] for r in runs if not r["summary"]["client"]["kept_up"]]
    if late:
        lines += ["", f"> The load client fell behind during: {', '.join(late)}. Those latencies include the client's own delay."]
    lines.append("")
    return "\n".join(lines)
