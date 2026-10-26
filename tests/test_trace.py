import json
import random
import tempfile
import unittest
from pathlib import Path

from inference_routing_bench import text
from inference_routing_bench.trace import Request, TraceError, dump, fingerprint, load, stats


def request(id="r1", at=0.0, kind="single", content="hello world", shared=0, **kw):
    return Request(id=id, at=at, kind=kind, tenant=kw.get("tenant", "t"), group=kw.get("group", id),
                   messages=({"role": "user", "content": content},), max_tokens=kw.get("max_tokens", 16), shared_prefix_words=shared)


class TextTests(unittest.TestCase):
    def test_same_seed_same_words_and_one_word_per_vocabulary_entry(self):
        a, b = text.words(random.Random(1), 50), text.words(random.Random(1), 50)
        self.assertEqual(a, b)
        self.assertEqual(text.count(a), 50)
        self.assertTrue(set(a.split()) <= set(text.VOCABULARY))
        self.assertEqual(len(set(text.VOCABULARY)), len(text.VOCABULARY))
        self.assertEqual(text.words(random.Random(1), 0), "")
        with self.assertRaises(ValueError):
            text.words(random.Random(1), -1)


class TraceFileTests(unittest.TestCase):
    def test_round_trip_and_fingerprint(self):
        reqs = [request("a", 0.0), request("b", 1.5, content="one two three", shared=2)]
        with tempfile.TemporaryDirectory() as d:
            path = Path(d, "t.jsonl")
            dump(reqs, path)
            self.assertEqual(load(path), reqs)
            self.assertRegex(fingerprint(path), r"^sha256:[0-9a-f]{64}$")
            self.assertNotIn('"extra"', path.read_text())

    def test_bad_traces_are_refused_with_the_line(self):
        good = json.loads(request().to_json())
        cases = [
            ({**good, "kind": "batch"}, "kind must be one of"),
            ({**good, "at": -1}, "'at' must be"),
            ({**good, "max_tokens": 0}, "'max_tokens'"),
            ({**good, "messages": [{"role": "assistant", "content": "x"}]}, "the last message must come from the user"),
            ({**good, "messages": [{"role": "tool", "content": "x"}]}, "every message needs a role"),
            ({**good, "shared_prefix_words": 99}, "shared_prefix_words must be between"),
            ({**good, "colour": "blue"}, "unknown field"),
            ({k: v for k, v in good.items() if k != "group"}, "missing 'group'"),
        ]
        with tempfile.TemporaryDirectory() as d:
            for raw, message in cases:
                with self.subTest(message=message):
                    path = Path(d, "t.jsonl")
                    path.write_text(json.dumps(raw) + "\n")
                    with self.assertRaisesRegex(TraceError, "line 1: " + message):
                        load(path)
            path = Path(d, "t.jsonl")
            path.write_text(request("a", 2.0).to_json() + "\n" + request("b", 1.0).to_json() + "\n")
            with self.assertRaisesRegex(TraceError, "line 2: requests must be in arrival order"):
                load(path)
            path.write_text(request("a").to_json() + "\n" + request("a", 1.0).to_json() + "\n")
            with self.assertRaisesRegex(TraceError, "duplicate id"):
                load(path)
            path.write_text("\n")
            with self.assertRaisesRegex(TraceError, "no requests"):
                load(path)

    def test_stats_count_the_mix_and_the_repeated_text(self):
        reqs = [request("a", 0.0, content="w " * 100), request("b", 10.0, kind="rag", content="w " * 100, shared=60, group="doc")]
        s = stats(reqs)
        self.assertEqual((s["requests"], s["duration_s"], s["rate_per_s"]), (2, 10.0, 0.2))
        self.assertEqual(s["by_kind"], {"rag": 1, "single": 1})
        self.assertEqual(s["prompt_words"]["total"], 200)
        self.assertEqual(s["shared_prefix_share"], 0.3)
