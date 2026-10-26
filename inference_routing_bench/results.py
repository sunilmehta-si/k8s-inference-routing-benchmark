"""One result file per router run: what was replayed, against what, and what came back.

A result names its trace by fingerprint and its cluster by the pinned versions and model-server settings, so two
results can only be compared when they replayed the same requests against the same servers.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .client import Result
from .metrics import by_kind, summarize

SCHEMA = 1


class ResultsError(ValueError):
    pass


def build(mode: str, trace_name: str, trace_fingerprint: str, results: list[Result], pods: dict | None,
          cluster: dict | None = None, ttft_slo_s: float = 1.0, description: str = "", repeat: int = 1) -> dict:
    return {
        "schema": SCHEMA,
        "tool_version": __version__,
        "mode": mode,
        "repeat": repeat,
        "description": description,
        "finished_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "trace": {"name": trace_name, "fingerprint": trace_fingerprint, "requests": len(results)},
        "cluster": cluster or {},
        "summary": summarize(results, ttft_slo_s),
        "by_kind": by_kind(results, ttft_slo_s),
        "pods": pods,
    }


def save(run: dict, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(run, indent=2, sort_keys=True) + "\n")


def load(path: str | Path) -> dict:
    try:
        run = json.loads(Path(path).read_text())
    except ValueError as exc:
        raise ResultsError(f"{path}: not JSON: {exc}") from exc
    if run.get("schema") != SCHEMA:
        raise ResultsError(f"{path}: result schema {run.get('schema')!r}, this version reads {SCHEMA}")
    for key in ("mode", "trace", "summary", "by_kind"):
        if key not in run:
            raise ResultsError(f"{path}: missing '{key}'")
    return run


def comparable(runs: list[dict]) -> None:
    """Refuse to put results side by side unless they replayed the same trace against the same servers."""
    if not runs:
        raise ResultsError("no results to compare")
    fingerprints = {r["trace"]["fingerprint"] for r in runs}
    if len(fingerprints) > 1:
        raise ResultsError("the results replayed different traces: " + ", ".join(sorted(f"{r['mode']}={r['trace']['fingerprint'][:19]}" for r in runs)))
    servers = {json.dumps(r.get("cluster", {}).get("model_server", {}), sort_keys=True) for r in runs}
    if len(servers) > 1:
        raise ResultsError("the results ran against differently configured model servers")
    keys = [(r["mode"], r.get("repeat", 1)) for r in runs]
    if len(set(keys)) != len(keys):
        raise ResultsError("more than one result for the same router and repeat: " + ", ".join(f"{m}#{n}" for m, n in keys))


def by_mode(runs: list[dict]) -> list[tuple[str, list[dict]]]:
    """Runs grouped by router, routers in the order first seen, repeats in repeat order."""
    groups: dict[str, list[dict]] = {}
    for r in runs:
        groups.setdefault(r["mode"], []).append(r)
    return [(mode, sorted(rs, key=lambda r: r.get("repeat", 1))) for mode, rs in groups.items()]
