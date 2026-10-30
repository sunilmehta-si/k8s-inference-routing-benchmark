import hashlib
import unittest
from pathlib import Path

from inference_routing_bench.generate import generate, load_spec
from inference_routing_bench.trace import stats

ROOT = Path(__file__).resolve().parents[1]
# sha256 of each workload's generated trace. Traces are not committed (the full one is ~17 MB); these pin them
# instead, so a change to the generator that changes the traffic shows up here, on every Python version CI runs.
FINGERPRINTS = {
    "smoke": "sha256:28c149d236ddb2b6f397456c47f7567c944f54d85bd181a0c0f5e0e13f1805f1",
    "chat-rag-mix": "sha256:bc470acc83d6afbed70a27d05517c9ff855f93e97f455fda2752a1db0fc1fada",
    "one-off-heavy": "sha256:ff889bc8f7e009d9974469fc51e66dff82512c37f1d6170e6668c10e43d96c26",
}


def trace_sha(name: str) -> str:
    reqs = generate(load_spec(ROOT / "workloads" / f"{name}.yaml"))
    return "sha256:" + hashlib.sha256("".join(r.to_json() + "\n" for r in reqs).encode()).hexdigest()


class ReproducibleTraceTests(unittest.TestCase):
    def test_every_workload_generates_its_pinned_trace(self):
        self.assertEqual(set(FINGERPRINTS), {p.stem for p in (ROOT / "workloads").glob("*.yaml")})
        for name, expected in FINGERPRINTS.items():
            with self.subTest(workload=name):
                self.assertEqual(trace_sha(name), expected)

    def test_the_documented_workload_numbers(self):
        s = stats(generate(load_spec(ROOT / "workloads/chat-rag-mix.yaml")))
        self.assertEqual(s["requests"], 1672)                                  # docs/methodology.md
        self.assertEqual(s["shared_prefix_share"], 0.856)                      # README: 86% of prompt text

    def test_the_control_workload_shares_a_fifth_of_the_prefix_text(self):
        s = stats(generate(load_spec(ROOT / "workloads/one-off-heavy.yaml")))
        self.assertEqual(s["requests"], 1472)                              # the README's traces table
        self.assertEqual(round(s["rate_per_s"], 1), 4.9)
        self.assertLess(s["shared_prefix_share"], 0.2)                     # against 0.86 for chat-rag-mix
        self.assertGreater(s["by_kind"]["single"] / s["requests"], 0.9)    # almost all one-off prompts
        self.assertNotIn("rag", s["by_kind"])
