"""Turn a cluster run's comparison artifact into a committed dataset: results/<name>/ with the result files, the
report and the chart, in a stated router order, exactly as the dataset tests expect to regenerate them.

Every dataset so far was assembled by hand (copy the files, set the run URL, run report and chart in the right order),
and twice the hand version disagreed with the tests on order or title. This is that procedure, once.
"""
from __future__ import annotations

import shutil
from pathlib import Path

from .chart import svg
from .report import markdown
from .results import ResultsError, comparable, load, save


def assemble(source: Path, dest: Path, modes: list[str], title: str, report_title: str | None = None,
             run_url: str | None = None, repeats: int = 8) -> list[dict]:
    """Copy each mode's `<mode>-rN.json` from source into dest, in the given order, and write README.md and chart.svg.

    `run_url` is written into each result when given, for artifacts from before the workflow stamped it. Every mode
    must have exactly `repeats` runs, and the runs must be comparable (same trace, same servers); a missing or odd
    file is an error before anything is written."""
    runs = []
    for mode in modes:
        files = sorted(source.glob(f"{mode}-r*.json"), key=lambda p: int(p.stem.rsplit("-r", 1)[1]))
        if len(files) != repeats:
            raise ResultsError(f"{mode}: {len(files)} result files in {source}, expected {repeats}")
        for f in files:
            run = load(f)
            if run["mode"] != mode:
                raise ResultsError(f"{f}: holds a run of {run['mode']!r}, not {mode!r}")
            if run_url:
                run["run_url"] = run_url
            if not run.get("run_url"):
                raise ResultsError(f"{f}: no run_url; pass --run-url for an artifact the workflow did not stamp")
            runs.append(run)
    comparable(runs)
    dest.mkdir(parents=True, exist_ok=True)
    for run in runs:
        save(run, dest / f"{run['mode']}-r{run['repeat']}.json")
    (dest / "README.md").write_text(markdown(runs, report_title or f"{dest.name} ({runs[0]['trace']['name']})"))
    (dest / "chart.svg").write_text(svg(runs, title))
    return runs
