import time
import unittest

from inference_routing_bench import client
from inference_routing_bench.trace import Request

from .fakes import FakeLLM, start


def req(id, at, content="one two three", max_tokens=5):
    return Request(id=id, at=at, kind="rag", tenant="t", group="g", messages=({"role": "user", "content": content},),
                   max_tokens=max_tokens)


class ClientTests(unittest.TestCase):
    def setUp(self):
        self.server, self.url = start()

    def tearDown(self):
        self.server.shutdown()

    def test_streams_are_timed_and_usage_is_recorded(self):
        results = client.run(self.url, "m", [req("a", 0.0), req("b", 0.2)], lead_s=0.1)
        self.assertEqual([r.id for r in results], ["a", "b"])
        a, b = results
        self.assertTrue(a.ok and b.ok)
        self.assertEqual((a.status, a.output_chunks, a.completion_tokens, a.prompt_tokens), (200, 5, 5, 3))
        self.assertGreaterEqual(a.ttft_s, FakeLLM.prefill_s)
        self.assertLess(b.ttft_s, a.ttft_s)                       # same prompt again: the fake's cache answers faster
        self.assertEqual((a.cached_tokens, b.cached_tokens), (0, 3))
        self.assertGreater(a.e2e_s, a.ttft_s)
        body = FakeLLM.bodies[0]
        self.assertEqual((body["model"], body["stream"], body["max_tokens"], body["stream_options"]),
                         ("m", True, 5, {"include_usage": True}))

    def test_requests_go_out_at_their_arrival_times_and_lateness_is_recorded(self):
        t0 = time.monotonic()
        results = client.run(self.url, "m", [req("a", 10.0), req("b", 10.3), req("c", 10.6)], lead_s=0.05)
        self.assertGreater(time.monotonic() - t0, 0.6)            # the first arrival is the start, not 10 s later
        self.assertEqual([r.scheduled_s for r in results], [0.0, 0.3, 0.6])
        self.assertTrue(all(r.lateness_s < 0.1 for r in results))
        fast = client.run(self.url, "m", [req("x", 0.0), req("y", 1.0)], speedup=10, lead_s=0.05)
        self.assertEqual(fast[1].scheduled_s, 0.1)
        starved = client.run(self.url, "m", [req(f"s{i}", 0.0, max_tokens=20) for i in range(4)], workers=1, lead_s=0.05)
        self.assertGreater(starved[-1].lateness_s, 0.05)           # one worker: the last request waited for the others

    def test_errors_and_dead_endpoints_are_results_not_crashes(self):
        FakeLLM.status = 503
        r = client.run(self.url, "m", [req("a", 0.0)], lead_s=0.05)[0]
        self.assertEqual(r.status, 503)
        self.assertFalse(r.ok)
        self.assertIn("overloaded", r.error)
        dead = client.run("http://127.0.0.1:9/", "m", [req("a", 0.0)], timeout=2, lead_s=0.05)[0]
        self.assertEqual(dead.status, 0)
        self.assertIn("Error", dead.error)
        with self.assertRaisesRegex(ValueError, "http"):
            client.run("ftp://x", "m", [req("a", 0.0)])
        with self.assertRaises(ValueError):
            client.run(self.url, "m", [req("a", 0.0)], speedup=0)
