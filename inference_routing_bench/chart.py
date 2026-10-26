"""A dependency-free SVG of the headline: TTFT p50 and p95 per router, with the prefix-cache hit rate beside it.
With repeats, the bars are medians and a whisker spans the p95 range."""
from __future__ import annotations

import statistics
from html import escape

from .results import by_mode, comparable

W, ROW, LEFT, BAR_W = 760, 44, 150, 380
P50, P95, HIT = "#2563eb", "#93c5fd", "#059669"


def _median(runs: list[dict], get) -> float | None:
    values = [v for v in (get(r) for r in runs) if v is not None]
    return statistics.median(values) if values else None


def svg(runs: list[dict], title: str) -> str:
    comparable(runs)
    groups = by_mode(runs)
    p95_max = max((r["summary"]["ttft_ms"]["p95"] or 0) for r in runs)
    scale = BAR_W / (p95_max or 1)
    height = 70 + ROW * len(groups) + 40
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{height}" viewBox="0 0 {W} {height}" '
           f'font-family="Inter, Helvetica, Arial, sans-serif" font-size="13">',
           '<rect width="100%" height="100%" fill="#ffffff"/>',
           f'<text x="16" y="26" font-size="15" font-weight="700" fill="#0f172a">{escape(title)}</text>',
           f'<text x="{LEFT}" y="50" fill="#475569">Time to first token (ms): p50 dark, p95 light</text>',
           f'<text x="{LEFT + BAR_W + 40}" y="50" fill="#475569">Prefix-cache hits</text>']
    for i, (mode, rs) in enumerate(groups):
        y = 66 + i * ROW
        p50 = _median(rs, lambda r: r["summary"]["ttft_ms"]["p50"]) or 0
        p95s = [r["summary"]["ttft_ms"]["p95"] or 0 for r in rs]
        p95 = statistics.median(p95s)
        hit = _median(rs, lambda r: (r.get("pods") or {}).get("prefix_cache_hit_rate"))
        label_x = LEFT + max(p95s) * scale + 6
        out += [f'<text x="16" y="{y + 18}" fill="#0f172a">{escape(mode)}</text>',
                f'<rect x="{LEFT}" y="{y + 4}" width="{p95 * scale:.1f}" height="20" rx="3" fill="{P95}"/>',
                f'<rect x="{LEFT}" y="{y + 4}" width="{p50 * scale:.1f}" height="20" rx="3" fill="{P50}"/>']
        if len(rs) > 1:
            out += [f'<line x1="{LEFT + min(p95s) * scale:.1f}" y1="{y + 14}" x2="{LEFT + max(p95s) * scale:.1f}" y2="{y + 14}" '
                    f'stroke="#1e3a8a" stroke-width="2"/>']
        out += [f'<text x="{label_x:.1f}" y="{y + 19}" fill="#334155">{p50:,.0f} / {p95:,.0f}</text>']
        if hit is not None:
            out += [f'<rect x="{LEFT + BAR_W + 40}" y="{y + 4}" width="{hit * 120:.1f}" height="20" rx="3" fill="{HIT}"/>',
                    f'<text x="{LEFT + BAR_W + 46 + hit * 120:.1f}" y="{y + 19}" fill="#334155">{hit * 100:.0f}%</text>']
    n = sorted({len(rs) for _, rs in groups})
    runs_note = "" if n == [1] else f", median of {'/'.join(map(str, n))} runs per router (whisker: p95 range)"
    out += [f'<text x="16" y="{height - 14}" fill="#64748b">{escape(runs[0]["trace"]["name"])}, '
            f'{runs[0]["trace"]["requests"]:,} requests, same trace for every router{runs_note}</text>', "</svg>"]
    return "\n".join(out) + "\n"
