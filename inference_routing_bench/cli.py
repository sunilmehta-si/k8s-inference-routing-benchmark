"""`irb` command line."""
from __future__ import annotations

import argparse
import json
import sys
import urllib.request
from pathlib import Path

from . import __version__


def _parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="irb", description="Benchmark LLM request routing on Kubernetes on identical chat and RAG traces.")
    p.add_argument("--version", action="version", version=f"k8s-inference-routing-benchmark {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    tr = sub.add_parser("trace", help="Generate or summarise request traces.")
    tsub = tr.add_subparsers(dest="trace_command", required=True)
    g = tsub.add_parser("generate", help="Write the seeded trace for a workload spec (JSON lines).")
    g.add_argument("spec", help="Workload spec, e.g. workloads/chat-rag-mix.yaml.")
    g.add_argument("--seed", type=int, help="Override the spec's seed.")
    g.add_argument("--output", "-o", help="Write here instead of stdout.")
    st = tsub.add_parser("stats", help="What a trace asks of the cluster: volume, mix, prompt sizes, repeated text.")
    st.add_argument("trace")

    rn = sub.add_parser("run", help="Replay a trace against an OpenAI-compatible endpoint and write a result file.")
    rn.add_argument("--url", required=True, help="Base URL of the router or service, e.g. http://router:8081.")
    rn.add_argument("--model", required=True, help="Model name to send.")
    rn.add_argument("--trace", required=True)
    rn.add_argument("--mode", required=True, help="Name of the router setup under test, e.g. round-robin.")
    rn.add_argument("--description", default="", help="One line saying what the router does.")
    rn.add_argument("--repeat", type=int, default=1, help="Which repeat of this router this run is (default: 1).")
    rn.add_argument("--speedup", type=float, default=1.0, help="Replay this many times faster than the trace (default: 1).")
    rn.add_argument("--ttft-slo-ms", type=float, default=1000.0, help="TTFT objective for goodput (default: 1000).")
    rn.add_argument("--timeout", type=float, default=120.0, help="Seconds to wait on a stream before giving up.")
    rn.add_argument("--workers", type=int, default=512, help="Most requests in flight at once (default: 512).")
    rn.add_argument("--scrape", action="append", default=[], metavar="NAME=URL",
                    help="A model server's /metrics to read before and after the run (repeat per pod).")
    rn.add_argument("--cluster", help="JSON file describing the cluster and model servers, stored with the result.")
    rn.add_argument("--raw", help="Also write every request's measurements here (JSON lines).")
    rn.add_argument("--output", "-o", required=True)

    rp = sub.add_parser("report", help="Markdown comparison of result files from the same trace.")
    rp.add_argument("results", nargs="+")
    rp.add_argument("--title")
    rp.add_argument("--output", "-o")

    cp = sub.add_parser("compare", help="In how many runs each router beat each other one, per metric.")
    cp.add_argument("results", nargs="+")
    cp.add_argument("--held", action="store_true", help="Only the differences that held in every shared run.")
    cp.add_argument("--output", "-o")

    vs = sub.add_parser("versions", help="Compare the pins in deploy/versions.env with upstream's latest releases.")
    vs.add_argument("--strict", action="store_true",
                    help="Exit 1 when a newer release is old enough to adopt (releases younger than 14 days only warn).")
    vs.add_argument("--output", "-o", help="Write the Markdown table here instead of stdout.")
    vs.add_argument("--json", metavar="PATH", help="Also write the rows as JSON here.")
    ds = sub.add_parser("dataset", help="Assemble a committed dataset from a cluster run's comparison artifact.")
    ds.add_argument("name", help="Dataset name: results/<name>/ is written.")
    ds.add_argument("--from", dest="source", required=True, help="Folder holding the artifact's <mode>-rN.json files.")
    ds.add_argument("--modes", required=True, help="Routers in column order, comma-separated.")
    ds.add_argument("--title", required=True, help="Chart title.")
    ds.add_argument("--report-title", help="Report title (default: '<name> (<trace>)').")
    ds.add_argument("--run-url", help="Set run_url on every result (for artifacts from before the workflow stamped it).")
    ds.add_argument("--repeats", type=int, default=8, help="Runs each router must have (default 8).")
    ds.add_argument("--results-dir", default="results", help="Where datasets live (default: results).")
    ch = sub.add_parser("chart", help="SVG of TTFT and prefix-cache hits per router.")
    ch.add_argument("results", nargs="+")
    ch.add_argument("--title", required=True)
    ch.add_argument("--output", "-o", required=True)
    return p


def _write(text: str, output: str | None) -> None:
    if output:
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        Path(output).write_text(text)
    else:
        sys.stdout.write(text)


def _scrape(targets: list[str], timeout: float = 10.0) -> dict[str, dict[str, float]]:
    from .promtext import parse
    out = {}
    for target in targets:
        name, sep, url = target.partition("=")
        if not sep or not url.startswith("http"):
            raise ValueError(f"--scrape wants NAME=http://host:port/metrics, got {target!r}")
        with urllib.request.urlopen(url, timeout=timeout) as resp:          # noqa: S310 - in-cluster pod URLs given by the operator
            out[name] = parse(resp.read().decode())
    return out


def _cmd_run(args) -> int:
    from . import client, results
    from .promtext import cluster_view, delta
    from .trace import fingerprint, load
    requests = load(args.trace)
    before = _scrape(args.scrape)
    print(f"irb: replaying {len(requests):,} requests against {args.url} as '{args.mode}'", file=sys.stderr)
    measured = client.run(args.url, args.model, requests, speedup=args.speedup, timeout=args.timeout, workers=args.workers)
    pods = None
    if args.scrape:
        after = _scrape(args.scrape)
        pods = cluster_view({name: delta(before.get(name, {}), after[name]) for name in after})
    cluster = json.loads(Path(args.cluster).read_text()) if args.cluster else None
    run = results.build(args.mode, Path(args.trace).stem, fingerprint(args.trace), measured, pods, cluster,
                        args.ttft_slo_ms / 1000, args.description, args.repeat, speedup=args.speedup)
    results.save(run, args.output)
    if args.raw:
        Path(args.raw).write_text("".join(json.dumps(r.to_dict()) + "\n" for r in measured))
    s = run["summary"]
    hit = (pods or {}).get("prefix_cache_hit_rate")
    print(f"irb: {s['ok']:,}/{s['requests']:,} ok, TTFT p50 {s['ttft_ms']['p50']} ms p95 {s['ttft_ms']['p95']} ms, "
          f"goodput {s['goodput']:.1%}" + (f", prefix-cache hits {hit:.1%}" if hit is not None else "")
          + ("" if s["client"]["kept_up"] else " (the client fell behind; latencies include its delay)"), file=sys.stderr)
    return 0 if s["errors"] == 0 and s["client"]["kept_up"] else 1


def _cmd_versions(args: argparse.Namespace) -> int:
    from datetime import date

    from .versions import VersionsError, as_json, markdown, node_image_listed, read_pins, report
    today = date.today()
    try:
        pins = read_pins()
        rows = report(pins, today=today)
        node_ok = node_image_listed(pins)
    except (OSError, VersionsError) as exc:
        print(f"irb: {exc}", file=sys.stderr)
        return 2
    text = markdown(rows, today, node_ok)
    if args.json:
        Path(args.json).write_text(as_json(rows, today, node_ok))
    _write(text, args.output)
    waiting = [r for r in rows if r.too_new(today)]
    if waiting:
        print("irb: too new to adopt yet: " + ", ".join(
            f"{r.name} {r.latest.tag} from {r.adoptable_on}" + (f" ({r.ready.tag} is adoptable now)" if r.ready else "")
            for r in waiting), file=sys.stderr)
    ready = [r for r in rows if r.adoptable_now(today)]
    if not node_ok:
        print("irb: KIND_NODE_IMAGE is not an image the pinned kind release lists", file=sys.stderr)
    return 1 if (args.strict and ready) or not node_ok else 0


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "trace" and args.trace_command == "generate":
            from .generate import generate, load_spec
            reqs = generate(load_spec(args.spec), args.seed)
            _write("".join(r.to_json() + "\n" for r in reqs), args.output)
            if args.output:
                print(f"irb: wrote {len(reqs):,} requests to {args.output}", file=sys.stderr)
            return 0
        if args.command == "trace" and args.trace_command == "stats":
            from .trace import load, stats
            _write(json.dumps(stats(load(args.trace)), indent=2) + "\n", None)
            return 0
        if args.command == "run":
            return _cmd_run(args)
        if args.command == "report":
            from .report import markdown
            from .results import load
            _write(markdown([load(p) for p in args.results], args.title), args.output)
            return 0
        if args.command == "compare":
            from .compare import held, pairs, table
            from .results import load
            runs = [load(p) for p in args.results]
            _write(table(held(runs) if args.held else pairs(runs)), args.output)
            return 0
        if args.command == "versions":
            return _cmd_versions(args)
        if args.command == "dataset":
            from .dataset import assemble
            dest = Path(args.results_dir) / args.name
            runs = assemble(Path(args.source), dest, args.modes.split(","), args.title, args.report_title, args.run_url, args.repeats)
            print(f"irb: wrote {len(runs)} runs of {len(args.modes.split(','))} routers, README.md and chart.svg to {dest}", file=sys.stderr)
            return 0
        if args.command == "chart":
            from .chart import svg
            from .results import load
            _write(svg([load(p) for p in args.results], args.title), args.output)
            return 0
    except (ValueError, OSError) as exc:
        print(f"irb: {exc}", file=sys.stderr)
        return 2
    return 2
