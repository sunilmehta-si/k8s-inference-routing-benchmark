import statistics
import unittest
from pathlib import Path

from inference_routing_bench.chart import svg
from inference_routing_bench.compare import held
from inference_routing_bench.report import markdown
from inference_routing_bench.results import by_mode, comparable, load

from .test_reproducible import FINGERPRINTS

ROOT = Path(__file__).resolve().parents[1]
MODES = ("round-robin", "load-aware", "prefix-aware", "prefix-load-aware")
CHART_TITLE = "chat-rag-mix on kind: 4 simulated vLLM pods, 1,672 requests, same trace for every router"


class CommittedResultsTests(unittest.TestCase):
    """The committed results are real cluster runs; these keep the report, chart and README honest about them."""

    def setUp(self):
        self.runs = [load(p) for m in MODES for p in sorted((ROOT / "results/chat-rag-mix").glob(f"{m}-r*.json"))]

    def test_every_router_has_the_same_repeats_each_from_a_recorded_ci_run(self):
        groups = dict(by_mode(self.runs))
        self.assertEqual(tuple(groups), MODES)
        repeats = {m: [r["repeat"] for r in rs] for m, rs in groups.items()}
        self.assertEqual(len({tuple(v) for v in repeats.values()}), 1, repeats)
        for r in self.runs:
            with self.subTest(mode=r["mode"], repeat=r["repeat"]):
                self.assertRegex(r["run_url"], r"^https://github\.com/sunilmehta-si/k8s-inference-routing-benchmark/actions/runs/\d+$")
                path = ROOT / "results/chat-rag-mix" / f"{r['mode']}-r{r['repeat']}.json"
                self.assertEqual(load(path), r)                                        # file name matches its contents

    def test_every_router_replayed_the_pinned_trace_against_the_same_servers(self):
        comparable(self.runs)
        self.assertEqual({r["trace"]["fingerprint"] for r in self.runs}, {FINGERPRINTS["chat-rag-mix"]})
        for r in self.runs:
            with self.subTest(mode=r["mode"]):
                self.assertEqual(r["summary"]["errors"], 0)
                self.assertTrue(r["summary"]["client"]["kept_up"])
                self.assertEqual(r["pods"]["requests_served"], r["trace"]["requests"])
                # the pods' counters and the cached tokens each response reported must add up: nothing uncounted
                self.assertAlmostEqual(r["pods"]["prefix_cache_hit_rate"], r["summary"]["server_cached_prompt_share"], delta=0.01)

    def test_report_and_chart_regenerate_exactly(self):
        self.assertEqual((ROOT / "results/chat-rag-mix/README.md").read_text(), markdown(self.runs))
        self.assertEqual((ROOT / "results/chat-rag-mix/chart.svg").read_text(), svg(self.runs, CHART_TITLE))

    def test_the_readme_quotes_the_committed_numbers(self):
        readme = (ROOT / "README.md").read_text()
        for mode, rs in by_mode(self.runs):
            with self.subTest(mode=mode):
                hit = statistics.median(r["pods"]["prefix_cache_hit_rate"] for r in rs)
                p50 = statistics.median(r["summary"]["ttft_ms"]["p50"] for r in rs)
                self.assertIn(f"{hit * 100:.1f}%", readme)
                self.assertIn(f"{p50:,.0f} ms", readme)

    def test_every_claim_the_readme_says_held_in_every_run_did(self):
        # (metric, winner, loser): each "What held in all eight runs" bullet in the README, as data.
        claims = [
            ("Prefix-cache hit rate", "prefix-aware", "round-robin"), ("Prefix-cache hit rate", "prefix-aware", "load-aware"),
            ("Prefix-cache hit rate", "prefix-load-aware", "round-robin"), ("Prefix-cache hit rate", "prefix-load-aware", "load-aware"),
            ("TTFT p50", "prefix-aware", "round-robin"), ("TTFT p50", "prefix-load-aware", "round-robin"),
            ("Load balance", "round-robin", "prefix-aware"), ("Load balance", "round-robin", "prefix-load-aware"),
            ("Load balance", "load-aware", "prefix-aware"), ("Load balance", "load-aware", "prefix-load-aware"),
            ("TTFT p99", "load-aware", "prefix-aware"), ("TTFT p99", "load-aware", "prefix-load-aware"),
            ("Goodput", "load-aware", "prefix-aware"), ("Goodput", "load-aware", "prefix-load-aware"),
            ("TTFT p95", "load-aware", "round-robin"),
            ("One-off TTFT p95", "load-aware", "prefix-aware"), ("One-off TTFT p95", "prefix-load-aware", "prefix-aware"),
        ]
        found = {(p.metric, p.winner, ({p.a, p.b} - {p.winner}).pop()) for p in held(self.runs)}
        for claim in claims:
            with self.subTest(claim=claim):
                self.assertIn(claim, found)
        # and the README's "did not hold" claims really didn't
        for metric in ("TTFT p99", "Goodput", "Load balance"):
            self.assertFalse({(metric, "prefix-load-aware", "prefix-aware"), (metric, "prefix-aware", "prefix-load-aware")} & found)
        self.assertNotIn(("One-off TTFT p95", "round-robin", "prefix-aware"), found)   # seven runs of eight, not all

