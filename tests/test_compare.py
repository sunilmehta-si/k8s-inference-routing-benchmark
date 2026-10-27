import unittest

from inference_routing_bench.compare import held, pairs
from inference_routing_bench.results import ResultsError


def run(mode, repeat, p50, hit=0.5, chat=None):
    return {
        "mode": mode, "repeat": repeat,
        "trace": {"name": "t", "fingerprint": "sha256:" + "0" * 64, "requests": 10},
        "cluster": {"model_server": {"image": "sim"}},
        "summary": {"ttft_ms": {"p50": p50, "p95": p50 * 4, "p99": p50 * 6}, "goodput": 0.99},
        "by_kind": {"chat": {"ttft_ms": {"p95": chat}}} if chat is not None else {},
        "pods": {"prefix_cache_hit_rate": hit, "balance": 0.9},
    }


class CompareTests(unittest.TestCase):
    def test_a_difference_holds_only_when_one_router_wins_every_shared_repeat(self):
        runs = [run("rr", 1, 120), run("rr", 2, 130), run("rr", 3, 110),
                run("pa", 1, 90), run("pa", 2, 95), run("pa", 3, 85),
                run("la", 1, 100), run("la", 2, 140), run("la", 3, 105)]
        p50 = {(p.a, p.b): p for p in pairs(runs) if p.metric == "TTFT p50"}
        self.assertEqual((p50["rr", "pa"].a_better, p50["rr", "pa"].b_better, p50["rr", "pa"].repeats), (0, 3, 3))
        self.assertEqual(p50["rr", "pa"].winner, "pa")
        self.assertIsNone(p50["rr", "la"].winner)                    # la won two of three: not every run
        self.assertEqual(p50["rr", "la"].b_better, 2)
        self.assertIn(("TTFT p50", "pa"), {(p.metric, p.winner) for p in held(runs)})

    def test_higher_is_better_metrics_and_ties(self):
        runs = [run("rr", 1, 100, hit=0.64), run("rr", 2, 100, hit=0.63),
                run("pa", 1, 100, hit=0.80), run("pa", 2, 100, hit=0.79)]
        by_metric = {p.metric: p for p in pairs(runs)}
        self.assertEqual(by_metric["Prefix-cache hit rate"].winner, "pa")
        self.assertEqual(by_metric["TTFT p50"].ties, 2)               # equal in both: nobody holds
        self.assertIsNone(by_metric["TTFT p50"].winner)

    def test_only_shared_repeats_count_and_one_run_proves_nothing(self):
        runs = [run("rr", 1, 120), run("rr", 2, 120), run("pa", 2, 90), run("pa", 5, 90)]
        pair = next(p for p in pairs(runs) if p.metric == "TTFT p50")
        self.assertEqual(pair.repeats, 1)                             # only repeat 2 is shared
        self.assertIsNone(pair.winner)

    def test_a_metric_a_run_lacks_is_skipped_for_that_repeat(self):
        runs = [run("rr", 1, 120, chat=300), run("rr", 2, 120), run("pa", 1, 90, chat=200), run("pa", 2, 90, chat=210)]
        chat = next(p for p in pairs(runs) if p.metric == "Chat TTFT p95")
        self.assertEqual(chat.repeats, 1)

    def test_runs_that_replayed_different_traffic_are_refused(self):
        other = run("pa", 1, 90)
        other["trace"]["fingerprint"] = "sha256:" + "1" * 64
        with self.assertRaises(ResultsError):
            pairs([run("rr", 1, 120), other])
