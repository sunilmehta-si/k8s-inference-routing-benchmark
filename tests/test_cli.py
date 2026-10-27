import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from inference_routing_bench import __version__
from inference_routing_bench.cli import main
from inference_routing_bench.results import ResultsError, load

from .fakes import start

ROOT = Path(__file__).resolve().parents[1]


def quiet(argv):
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        code = main(argv)
    return code, out.getvalue(), err.getvalue()


class CliTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.d = Path(self.dir.name)
        self.server, self.url = start()
        spec = self.d / "tiny.yaml"
        spec.write_text("name: tiny\nseed: 3\nduration_s: 4\nmax_tokens: [3, 5]\ntenants:\n"
                        "  - name: t\n    system_prompt_words: 20\n"
                        "    rag: {queries_per_minute: 240, documents: 2, document_words: [30, 40], question_words: [3, 5]}\n")
        self.trace = self.d / "tiny.jsonl"
        code, _, err = quiet(["trace", "generate", str(spec), "-o", str(self.trace)])
        self.assertEqual(code, 0, err)

    def tearDown(self):
        self.server.shutdown()
        self.dir.cleanup()

    def test_generate_stats_run_report_and_chart_end_to_end(self):
        code, out, _ = quiet(["trace", "stats", str(self.trace)])
        self.assertEqual(code, 0)
        n = json.loads(out)["requests"]
        self.assertGreater(n, 5)
        runs = []
        for mode in ("round-robin", "prefix-aware"):
            path = self.d / f"{mode}.json"
            code, _, err = quiet(["run", "--url", self.url, "--model", "m", "--trace", str(self.trace), "--mode", mode,
                                  "--speedup", "4", "--scrape", f"pod-0={self.url}/metrics", "--raw", str(self.d / f"{mode}.jsonl"),
                                  "-o", str(path)])
            self.assertEqual(code, 0, err)
            self.assertIn("prefix-cache hits", err)
            runs.append(path)
        run = load(runs[0])
        self.assertEqual((run["mode"], run["trace"]["requests"], run["summary"]["ok"]), ("round-robin", n, n))
        self.assertEqual(run["pods"]["requests_served"], n)
        self.assertEqual(run["tool_version"], __version__)
        self.assertEqual(len((self.d / "round-robin.jsonl").read_text().splitlines()), n)
        code, out, _ = quiet(["report", *map(str, runs), "--title", "tiny"])
        self.assertEqual(code, 0)
        self.assertIn("| Metric | round-robin | prefix-aware |", out)
        self.assertIn("Prefix-cache hit rate", out)
        self.assertIn("**TTFT p95 by kind of traffic (ms)**", out)
        self.assertNotRegex(out.split("by kind of traffic")[1], r"\d\.\d")              # whole milliseconds
        code, _, _ = quiet(["chart", *map(str, runs), "--title", "tiny", "-o", str(self.d / "c.svg")])
        self.assertEqual(code, 0)
        self.assertTrue((self.d / "c.svg").read_text().startswith("<svg"))

    def test_results_from_different_traces_or_duplicate_routers_are_not_compared(self):
        path = self.d / "a.json"
        quiet(["run", "--url", self.url, "--model", "m", "--trace", str(self.trace), "--mode", "a", "--speedup", "8", "-o", str(path)])
        other = json.loads(path.read_text())
        other["trace"]["fingerprint"] = "sha256:" + "0" * 64
        other["mode"] = "b"
        (self.d / "b.json").write_text(json.dumps(other))
        code, _, err = quiet(["report", str(path), str(self.d / "b.json")])
        self.assertEqual(code, 2)
        self.assertIn("different traces", err)
        code, _, err = quiet(["report", str(path), str(path)])
        self.assertIn("more than one result for the same router and repeat", err)
        (self.d / "old.json").write_text(json.dumps({**other, "schema": 0}))
        with self.assertRaisesRegex(ResultsError, "schema"):
            load(self.d / "old.json")

    def test_repeats_of_a_router_are_reported_as_median_and_range(self):
        paths = []
        for n, (p50, p95) in enumerate([(100.0, 700.0), (140.0, 900.0), (120.0, 650.0)], start=1):
            path = self.d / f"rr-r{n}.json"
            if n == 1:
                code, _, _ = quiet(["run", "--url", self.url, "--model", "m", "--trace", str(self.trace), "--mode", "rr",
                                    "--repeat", "1", "--speedup", "8", "-o", str(path)])
                self.assertEqual(code, 0)
                base = json.loads(path.read_text())
                self.assertEqual(base["repeat"], 1)
            run = json.loads(json.dumps(base))
            run["repeat"] = n
            run["summary"]["ttft_ms"]["p50"], run["summary"]["ttft_ms"]["p95"] = p50, p95
            path.write_text(json.dumps(run))
            paths.append(path)
        other = json.loads(json.dumps(base))
        other["mode"], other["summary"]["ttft_ms"]["p50"] = "pa", 90.0
        (self.d / "pa-r1.json").write_text(json.dumps(other))
        code, out, err = quiet(["report", *map(str, paths), str(self.d / "pa-r1.json")])
        self.assertEqual(code, 0, err)
        self.assertIn("| Metric | rr | pa |", out)                                     # one column per router, not per run
        self.assertIn("median of 1/3 runs per router", out)
        self.assertIn("| TTFT p95 (ms) <sub>lower is better</sub> | 700 <sub>(650–900)</sub> |", out)
        self.assertIn("| 120 <sub>(100–140)</sub> | **90** |", out)                       # best picked by median
        self.assertIn("None: no router was better than another in every shared run.", out)  # pa has one run
        errors = next(line for line in out.splitlines() if line.startswith("| Errors"))
        self.assertTrue(errors.endswith("| 0 | 0 |"), errors)                              # no (0–0), and a tie isn't bold
        p99 = next(line for line in out.splitlines() if line.startswith("| TTFT p99"))
        self.assertNotIn("**", p99)
        code, out, _ = quiet(["compare", *map(str, paths), str(self.d / "pa-r1.json")])
        self.assertEqual(code, 0)
        self.assertIn("| TTFT p50 | rr vs pa | rr 0, pa 1 of 1 | 0 | – |", out)   # one shared run holds nothing
        code, out, _ = quiet(["compare", "--held", *map(str, paths), str(self.d / "pa-r1.json")])
        self.assertEqual(out.count("\n"), 2)                                       # header only
        code, _, _ = quiet(["chart", *map(str, paths), "--title", "t", "-o", str(self.d / "c.svg")])
        svg = (self.d / "c.svg").read_text()
        self.assertEqual(code, 0)
        self.assertIn("120 / 700", svg)
        self.assertIn("median of 3 runs per router", svg)

    def test_a_dead_endpoint_fails_the_run_and_bad_input_is_a_usage_error(self):
        code, _, err = quiet(["run", "--url", "http://127.0.0.1:9", "--model", "m", "--trace", str(self.trace), "--mode", "x",
                              "--speedup", "8", "--timeout", "2", "-o", str(self.d / "x.json")])
        self.assertEqual(code, 1)
        self.assertEqual(load(self.d / "x.json")["summary"]["ok"], 0)
        code, _, err = quiet(["run", "--url", self.url, "--model", "m", "--trace", str(self.trace), "--mode", "x",
                              "--scrape", "nourl", "-o", str(self.d / "y.json")])
        self.assertEqual(code, 2)
        self.assertIn("--scrape wants NAME=", err)
        code, _, err = quiet(["trace", "stats", str(self.d / "missing.jsonl")])
        self.assertEqual(code, 2)

    def test_committed_workloads_generate_through_the_cli(self):
        code, out, _ = quiet(["trace", "generate", str(ROOT / "workloads/smoke.yaml")])
        self.assertEqual(code, 0)
        self.assertGreater(len(out.splitlines()), 50)
