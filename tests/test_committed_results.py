import statistics
import unittest
from pathlib import Path

from inference_routing_bench.chart import svg
from inference_routing_bench.compare import held, pairs
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



class _OneRunDataset:
    """A dataset from one CI run: eight clean repeats of each router, a report and chart that regenerate exactly."""
    DIR = MODES_HERE = TITLE = REPORT_TITLE = None

    def setUp(self):
        self.dir = ROOT / "results" / self.DIR
        self.runs = [load(p) for m in self.MODES_HERE for p in sorted(self.dir.glob(f"{m}-r*.json"))]
        self.found = {(p.metric, p.winner, ({p.a, p.b} - {p.winner}).pop()) for p in held(self.runs)}

    TRACE = "chat-rag-mix"

    CI_RUNS = 1      # dispatches the repeats came from; more than one when a run's repeats were split over dispatches

    def test_one_clean_ci_run_with_eight_repeats_of_every_router(self):
        comparable(self.runs)
        self.assertEqual({r["trace"]["fingerprint"] for r in self.runs}, {FINGERPRINTS[self.TRACE]})
        self.assertEqual(len({r["run_url"] for r in self.runs}), self.CI_RUNS)
        groups = dict(by_mode(self.runs))
        self.assertEqual(tuple(groups), self.MODES_HERE)
        for mode, rs in groups.items():
            with self.subTest(mode=mode):
                self.assertEqual([r["repeat"] for r in rs], list(range(1, 9)))
                for r in rs:
                    self.assertEqual(r["summary"]["errors"], 0)
                    self.assertTrue(r["summary"]["client"]["kept_up"])
                    self.assertEqual(r["pods"]["requests_served"], r["trace"]["requests"])

    PODS = 4

    def test_report_and_chart_regenerate_exactly(self):
        self.assertEqual((self.dir / "README.md").read_text(), markdown(self.runs, self.REPORT_TITLE))
        self.assertIn(f" on {self.PODS} simulated vLLM pods,", (self.dir / "README.md").read_text().splitlines()[0])
        self.assertEqual({r["cluster"]["model_server"]["replicas"] for r in self.runs}, {self.PODS})
        self.assertEqual((self.dir / "chart.svg").read_text(), svg(self.runs, self.TITLE))


class LoadWeightResultsTests(_OneRunDataset, unittest.TestCase):
    """Does weighting load twice the prefix spread the work?"""
    DIR, REPORT_TITLE = "load-weight", "load-weight (chat-rag-mix)"
    MODES_HERE = MODES + ("prefix-load-2x",)
    TITLE = "Load weighted 2x next to the prefix scorer: 4 simulated vLLM pods, 1,672 requests"

    def test_what_the_readme_says_about_doubling_the_load_weight(self):
        for baseline in ("round-robin", "load-aware"):
            with self.subTest(baseline=baseline):
                # it keeps what prefix scoring buys...
                self.assertIn(("Prefix-cache hit rate", "prefix-load-2x", baseline), self.found)
                self.assertIn(("TTFT p50", "prefix-load-2x", baseline), self.found)
                # ...and still piles work onto a few pods, with the tail that comes with it
                for metric in ("Load balance", "TTFT p99", "Goodput"):
                    self.assertIn((metric, baseline, "prefix-load-2x"), self.found)
        # and against equal weights it changed nothing that held in every run
        self.assertEqual({f for f in self.found if {f[1], f[2]} == {"prefix-load-aware", "prefix-load-2x"}}, set())


class QueueThresholdResultsTests(_OneRunDataset, unittest.TestCase):
    """Does a queue threshold at the pods' concurrency let load count?"""
    DIR, REPORT_TITLE = "queue-threshold", "queue-threshold (chat-rag-mix)"
    MODES_HERE = ("load-aware", "prefix-load-aware", "prefix-load-q8")
    TITLE = "Load scorer queue threshold 8 instead of 128: 4 simulated vLLM pods, 1,672 requests"

    def test_what_the_readme_says_about_the_queue_threshold(self):
        # load-aware still spreads the work and has the tail; the threshold did not move prefix-load-q8 off the pile-up
        for metric in ("Load balance", "TTFT p99", "Goodput"):
            self.assertIn((metric, "load-aware", "prefix-load-q8"), self.found)
        self.assertIn(("Prefix-cache hit rate", "prefix-load-q8", "load-aware"), self.found)
        self.assertEqual({f for f in self.found if {f[1], f[2]} == {"prefix-load-aware", "prefix-load-q8"}}, set())


class ScorerResultsTests(_OneRunDataset, unittest.TestCase):
    """Do the router's other load scorers, which rescale across the pods, spread the work?"""
    DIR, REPORT_TITLE = "scorers", "scorers (chat-rag-mix)"
    MODES_HERE = ("load-aware", "prefix-load-aware", "router-default", "prefix-queue", "prefix-running", "prefix-active")
    TITLE = "The router's load scorers next to the prefix scorer: 4 simulated vLLM pods, 1,672 requests"

    def test_what_the_readme_says_about_the_other_load_scorers(self):
        others = set(self.MODES_HERE)
        # prefix-active: better than prefix-load-aware on latency, goodput and balance, and than load-aware on latency,
        # goodput and hits, at the same balance; prefix-load-aware keeps more hits
        for metric in ("TTFT p50", "TTFT p95", "TTFT p99", "Goodput", "Load balance"):
            self.assertIn((metric, "prefix-active", "prefix-load-aware"), self.found)
        for metric in ("TTFT p50", "TTFT p95", "TTFT p99", "Goodput", "Prefix-cache hit rate"):
            self.assertIn((metric, "prefix-active", "load-aware"), self.found)
        self.assertIn(("Prefix-cache hit rate", "prefix-load-aware", "prefix-active"), self.found)
        self.assertNotIn("Load balance", {f[0] for f in self.found if {f[1], f[2]} == {"load-aware", "prefix-active"}})
        # prefix-running: most even of the prefix routers, fewest hits of them; prefix-active beats it on tail and hits
        for other in others - {"load-aware", "prefix-running"}:
            self.assertIn(("Load balance", "prefix-running", other), self.found)
            self.assertIn(("Prefix-cache hit rate", other, "prefix-running"), self.found)
        for metric in ("TTFT p95", "TTFT p99", "Prefix-cache hit rate"):
            self.assertIn((metric, "prefix-active", "prefix-running"), self.found)
        # prefix-queue: balance near prefix-load-aware's and below load-aware's; lower median than prefix-load-aware
        self.assertIn(("Load balance", "load-aware", "prefix-queue"), self.found)
        self.assertIn(("TTFT p50", "prefix-queue", "prefix-load-aware"), self.found)
        # router-default: more hits than every router but prefix-queue in every run (against prefix-queue only by
        # median), better latencies than prefix-load-aware, still less even than load-aware
        for other in others - {"router-default", "prefix-queue"}:
            self.assertIn(("Prefix-cache hit rate", "router-default", other), self.found)
        self.assertNotIn("Prefix-cache hit rate", {f[0] for f in self.found if {f[1], f[2]} == {"router-default", "prefix-queue"}})
        for metric in ("TTFT p50", "TTFT p95", "TTFT p99"):
            self.assertIn((metric, "router-default", "prefix-load-aware"), self.found)
        self.assertIn(("Load balance", "load-aware", "router-default"), self.found)


class ActiveWeightResultsTests(_OneRunDataset, unittest.TestCase):
    """What does weighting the prefix, then the in-flight count, twice buy prefix-active?"""
    DIR, REPORT_TITLE = "active-weights", "active-weights (chat-rag-mix)"
    MODES_HERE = ("prefix-active", "prefix-active-p2", "prefix-active-a2")
    TITLE = "prefix-active with the prefix, then the in-flight count, weighted twice: 4 simulated vLLM pods, 1,672 requests"

    def test_what_the_readme_says_about_the_weights(self):
        for metric in ("TTFT p95", "Prefix-cache hit rate", "Chat TTFT p95", "RAG TTFT p95"):
            self.assertIn((metric, "prefix-active-p2", "prefix-active"), self.found)
        wins = {p.metric: {p.a: p.a_better, p.b: p.b_better} for p in pairs(self.runs)
                if {p.a, p.b} == {"prefix-active", "prefix-active-p2"}}
        self.assertEqual(wins["TTFT p99"]["prefix-active-p2"], 7)             # "seven of eight"
        self.assertEqual(wins["One-off TTFT p95"]["prefix-active-p2"], 6)     # "six of eight"
        self.assertEqual((wins["TTFT p50"]["prefix-active"], wins["Goodput"]["prefix-active"]), (7, 6))
        self.assertIn(("Load balance", "prefix-active", "prefix-active-p2"), self.found)
        for metric in ("TTFT p50", "TTFT p95", "TTFT p99", "Prefix-cache hit rate"):
            self.assertIn((metric, "prefix-active", "prefix-active-a2"), self.found)
        self.assertIn(("Load balance", "prefix-active-a2", "prefix-active-p2"), self.found)
        self.assertNotIn("TTFT p50", {f[0] for f in self.found if {f[1], f[2]} == {"prefix-active", "prefix-active-p2"}})


class HeadToHeadResultsTests(_OneRunDataset, unittest.TestCase):
    """The two routers with the most cache hits in the same run, beside prefix-only and round-robin."""
    DIR, REPORT_TITLE = "head-to-head", "head-to-head (chat-rag-mix)"
    MODES_HERE = ("round-robin", "prefix-aware", "router-default", "prefix-active-p2")
    TITLE = "The two routers with the most cache hits, next to prefix-only and round-robin: 4 simulated vLLM pods, 1,672 requests"

    def test_what_the_readme_says_about_the_head_to_head(self):
        wins = {p.metric: {p.a: p.a_better, p.b: p.b_better} for p in pairs(self.runs)
                if {p.a, p.b} == {"router-default", "prefix-active-p2"}}
        self.assertEqual({f[0] for f in self.found if {f[1], f[2]} == {"router-default", "prefix-active-p2"}}, set())
        self.assertEqual((wins["TTFT p50"]["prefix-active-p2"], wins["Prefix-cache hit rate"]["prefix-active-p2"],
                          wins["TTFT p99"]["prefix-active-p2"], wins["Load balance"]["prefix-active-p2"]), (5, 5, 7, 7))
        for best in ("router-default", "prefix-active-p2"):
            for other in ("prefix-aware", "round-robin"):
                self.assertIn(("TTFT p50", best, other), self.found)
                self.assertIn(("Prefix-cache hit rate", best, other), self.found)
        self.assertIn(("Load balance", "prefix-active-p2", "prefix-aware"), self.found)
        p99 = sorted(r["summary"]["ttft_ms"]["p99"] for r in self.runs if r["mode"] == "prefix-active-p2")
        self.assertGreater(p99[-1], 3000)
        self.assertLess(p99[-2], 750)


class EightPodResultsTests(_OneRunDataset, unittest.TestCase):
    """The same trace on eight pods instead of four: does the pile-up grow with the pool, and does spreading still pay?"""
    DIR, REPORT_TITLE, PODS = "eight-pods", "eight-pods (chat-rag-mix)", 8
    MODES_HERE = ("round-robin", "load-aware", "prefix-aware", "router-default", "prefix-active", "prefix-active-p2")
    TITLE = "Eight simulated vLLM pods instead of four: chat-rag-mix, 1,672 requests"

    def test_what_the_readme_says_about_eight_pods(self):
        prefix_routers = ("prefix-aware", "router-default", "prefix-active-p2")
        for even in ("round-robin", "load-aware"):
            for piled in prefix_routers:
                self.assertIn(("Load balance", even, piled), self.found)
            for metric in ("TTFT p50", "TTFT p99", "Prefix-cache hit rate"):
                self.assertIn((metric, "prefix-active", even), self.found)
            self.assertNotIn("Load balance", {f[0] for f in self.found if {f[1], f[2]} == {"prefix-active", even}})
        for piled in prefix_routers:
            self.assertIn(("Load balance", "prefix-active", piled), self.found)
        for metric in ("TTFT p99", "Prefix-cache hit rate"):
            self.assertIn((metric, "prefix-active-p2", "prefix-active"), self.found)
        wins = {p.metric: {p.a: p.a_better, p.b: p.b_better} for p in pairs(self.runs) if {p.a, p.b} == {"prefix-active", "prefix-active-p2"}}
        self.assertEqual(wins["TTFT p50"]["prefix-active-p2"], 5)
        self.assertEqual({f[0] for f in self.found if {f[1], f[2]} == {"round-robin", "load-aware"}}, set())
        for metric in ("TTFT p99", "Goodput"):
            self.assertIn((metric, "round-robin", "prefix-aware"), self.found)
        medians = {m: sorted(r["pods"]["balance"] for r in self.runs if r["mode"] == m)[3:5] for m in prefix_routers}
        for m, (lo, hi) in medians.items():
            self.assertLess((lo + hi) / 2, 0.61, m)                                # the pile-up numbers in the table


class PreciseResultsTests(_OneRunDataset, unittest.TestCase):
    """The picker's estimate of each pod's cache against the pods' real contents, read from their KV-cache events:
    three approximate routers and their precise counterparts, same scorers and weights."""
    DIR, REPORT_TITLE = "precise", "precise (chat-rag-mix)"
    MODES_HERE = ("prefix-aware", "precise-aware", "prefix-active", "precise-active", "prefix-queue", "precise-queue")
    TITLE = "Real cache contents instead of the picker's estimate: 4 simulated vLLM pods, 1,672 requests"
    CI_RUNS = 2      # repeats 1-3 and 4-8 were two dispatches of the same commit, hours apart

    def test_what_the_readme_says_about_the_precise_index(self):
        pairs_here = (("precise-aware", "prefix-aware"), ("precise-active", "prefix-active"), ("precise-queue", "prefix-queue"))
        for precise, approximate in pairs_here:
            self.assertIn(("Prefix-cache hit rate", precise, approximate), self.found)        # every pair, every run
        for precise, approximate in pairs_here[1:]:
            for metric in ("TTFT p99", "Goodput", "RAG TTFT p95"):
                self.assertIn((metric, precise, approximate), self.found)
        # the cost: a tokenizer round trip per request; prefix-active keeps the better median in every run
        self.assertIn(("TTFT p50", "prefix-active", "precise-active"), self.found)
        wins = {(p.metric, frozenset((p.a, p.b))): {p.a: p.a_better, p.b: p.b_better} for p in pairs(self.runs)}
        self.assertEqual(wins[("TTFT p99", frozenset(pairs_here[0]))]["precise-aware"], 7)
        self.assertEqual(wins[("TTFT p50", frozenset(pairs_here[2]))]["precise-queue"], 1)
        # no pair settles the load balance; the precise index changes where prompts go, not how the load scorer pulls
        self.assertEqual({f[0] for f in self.found if {f[1], f[2]} in [set(p) for p in pairs_here]} & {"Load balance"}, set())
        hits = {m: sorted(r["pods"]["prefix_cache_hit_rate"] for r in self.runs if r["mode"] == m)[3:5] for m in self.MODES_HERE}
        for precise, approximate in pairs_here:
            gain = sum(hits[precise]) / 2 - sum(hits[approximate]) / 2
            self.assertTrue(0.02 <= gain <= 0.035, (precise, gain))                     # "two to three points" in the README


class OneOffHeavyResultsTests(_OneRunDataset, unittest.TestCase):
    """The control: a trace where almost nothing repeats. Which gains survive without a cache to find?"""
    DIR, REPORT_TITLE, TRACE = "one-off-heavy", None, "one-off-heavy"
    MODES_HERE = ("round-robin", "load-aware", "prefix-aware", "router-default", "prefix-active", "prefix-active-p2")
    TITLE = "one-off-heavy, the control: 4 simulated vLLM pods, 1,472 requests that mostly share nothing"

    def test_what_the_readme_says_about_the_control(self):
        for r in self.runs:
            self.assertLess(r["pods"]["prefix_cache_hit_rate"], 0.05)              # 3 to 4%: nothing to find
        for winner in ("router-default", "prefix-active", "prefix-active-p2"):
            for base in ("round-robin", "load-aware"):
                for metric in ("TTFT p50", "TTFT p95"):
                    self.assertIn((metric, winner, base), self.found)
                if (winner, base) != ("router-default", "load-aware"):
                    self.assertIn(("TTFT p99", winner, base), self.found)
        p99 = {p.a: p.a_better, p.b: p.b_better} if (p := next(p for p in pairs(self.runs) if p.metric == "TTFT p99" and {p.a, p.b} == {"router-default", "load-aware"})) else {}
        self.assertEqual(p99["router-default"], 7)                                   # "seven of eight"
        for metric in ("TTFT p95", "TTFT p99"):
            self.assertIn((metric, "load-aware", "round-robin"), self.found)
        wins = {p.metric: {p.a: p.a_better, p.b: p.b_better} for p in pairs(self.runs) if {p.a, p.b} == {"round-robin", "load-aware"}}
        self.assertEqual(wins["TTFT p50"]["load-aware"], 5)
        for even in ("round-robin", "load-aware"):
            self.assertIn(("Load balance", even, "prefix-aware"), self.found)
            self.assertEqual({f[0] for f in self.found if {f[1], f[2]} == {even, "prefix-aware"}} - {"Load balance", "Prefix-cache hit rate"}, set())
        self.assertEqual({f for f in self.found if f[0] == "Goodput"}, set())
