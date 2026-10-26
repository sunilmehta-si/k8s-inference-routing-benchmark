import unittest
from pathlib import Path

from inference_routing_bench.chart import svg
from inference_routing_bench.report import markdown
from inference_routing_bench.results import comparable, load

from .test_reproducible import FINGERPRINTS

ROOT = Path(__file__).resolve().parents[1]
MODES = ("round-robin", "load-aware", "prefix-aware", "prefix-load-aware")
CHART_TITLE = "chat-rag-mix on kind: 4 simulated vLLM pods, 1,672 requests, same trace for every router"


class CommittedResultsTests(unittest.TestCase):
    """The committed results are a real cluster run; these keep the report, chart and README honest about them."""

    def setUp(self):
        self.runs = [load(ROOT / "results/chat-rag-mix" / f"{m}.json") for m in MODES]

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
        by = {r["mode"]: r for r in self.runs}
        for mode in MODES:
            with self.subTest(mode=mode):
                self.assertIn(f"{by[mode]['pods']['prefix_cache_hit_rate'] * 100:.1f}%", readme)
                self.assertIn(f"{by[mode]['summary']['ttft_ms']['p50']:,.0f} ms", readme)
