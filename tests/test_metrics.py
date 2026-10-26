import unittest

from inference_routing_bench import metrics, promtext
from inference_routing_bench.client import Result


def result(id="r", kind="rag", ttft=0.1, e2e=0.5, chunks=11, status=200, lateness=0.0, scheduled=0.0, cached=None, prompt=None, error=None):
    return Result(id, kind, "t", 100, 50, scheduled, lateness, status, ttft, e2e, chunks, prompt, chunks, cached, error)


class SummaryTests(unittest.TestCase):
    def test_percentiles_goodput_and_errors(self):
        rs = [result(f"r{i}", ttft=0.1 * (i + 1), e2e=0.1 * (i + 1) + 0.4, scheduled=float(i)) for i in range(10)]
        rs.append(result("bad", status=503, ttft=None, e2e=0.01, chunks=0, error="busy", scheduled=10.0))
        s = metrics.summarize(rs, ttft_slo_s=0.5)
        self.assertEqual((s["requests"], s["ok"], s["errors"]), (11, 10, 1))
        self.assertEqual(s["error_rate"], round(1 / 11, 4))
        self.assertEqual((s["ttft_ms"]["p50"], s["ttft_ms"]["p95"], s["ttft_ms"]["p99"]), (500.0, 1000.0, 1000.0))
        self.assertEqual(s["goodput"], round(5 / 11, 4))                # the failure counts as missing the objective
        self.assertEqual(s["tpot_ms"]["p50"], 40.0)                     # 0.4 s for the 10 tokens after the first
        self.assertEqual(s["status_counts"], {"200": 10, "503": 1})
        self.assertTrue(s["client"]["kept_up"])
        self.assertNotIn("server_cached_prompt_share", s)

    def test_a_client_that_fell_behind_is_flagged_and_cache_reports_are_summed(self):
        rs = [result(f"r{i}", lateness=1.0, cached=c, prompt=100) for i, c in enumerate((0, 80, 100))]
        s = metrics.summarize(rs)
        self.assertFalse(s["client"]["kept_up"])
        self.assertEqual(s["server_cached_prompt_share"], 0.6)
        self.assertEqual(set(metrics.by_kind(rs + [result("c", kind="chat")])), {"chat", "rag"})
        self.assertEqual(metrics.summarize([])["requests"], 0)


class PromTextTests(unittest.TestCase):
    TEXT = """# HELP vllm:prefix_cache_hits_total Prefix cache hits
# TYPE vllm:prefix_cache_hits_total counter
vllm:prefix_cache_hits_total{engine="0",model_name="m"} 300
vllm:prefix_cache_queries_total{engine="0",model_name="m"} 1000
vllm:request_success_total{finished_reason="length",model_name="m"} 7
vllm:request_success_total{finished_reason="stop",model_name="m"} 3
garbage line
vllm:kv_cache_usage_perc{model_name="m"} NaN
"""

    def test_parse_sums_labels_and_delta_survives_a_restart(self):
        p = promtext.parse(self.TEXT)
        self.assertEqual((p[promtext.HITS], p[promtext.QUERIES], p[promtext.SUCCESS]), (300, 1000, 10))
        self.assertNotIn("garbage", p)
        d = promtext.delta({promtext.HITS: 100, promtext.SUCCESS: 20}, p)
        self.assertEqual(d[promtext.HITS], 200)
        self.assertEqual(d[promtext.SUCCESS], 10)                       # counter reset: counts from zero

    def test_cluster_view_hit_rate_and_balance(self):
        view = promtext.cluster_view({
            "sim-a": {promtext.HITS: 900, promtext.QUERIES: 1000, promtext.SUCCESS: 30},
            "sim-b": {promtext.HITS: 100, promtext.QUERIES: 1000, promtext.SUCCESS: 10},
        })
        self.assertEqual(view["prefix_cache_hit_rate"], 0.5)
        self.assertEqual(view["requests_served"], 40)
        self.assertEqual(view["per_pod"]["sim-a"]["prefix_cache_hit_rate"], 0.9)
        self.assertEqual(view["balance"], round(1 / (2 * 0.75), 3))
        self.assertIsNone(promtext.cluster_view({"x": {}})["prefix_cache_hit_rate"])
