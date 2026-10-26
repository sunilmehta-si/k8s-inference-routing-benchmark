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
