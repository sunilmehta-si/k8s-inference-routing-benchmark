import tempfile
import unittest
from pathlib import Path

import yaml

from inference_routing_bench.generate import SpecError, generate, load_spec
from inference_routing_bench.trace import stats

ROOT = Path(__file__).resolve().parents[1]


def spec(**tenant):
    return {"name": "t", "seed": 1, "duration_s": 600, "max_tokens": [16, 32],
            "tenants": [{"name": "acme", "system_prompt_words": 50, **tenant}]}


class GenerateTests(unittest.TestCase):
    def test_same_spec_same_trace_and_another_seed_another_trace(self):
        s = spec(rag={"queries_per_minute": 30, "documents": 3, "document_words": [100, 200], "question_words": [5, 10]})
        self.assertEqual(generate(s), generate(s))
        self.assertNotEqual(generate(s), generate(s, seed=2))

    def test_chat_turns_resend_the_conversation_and_share_all_but_the_new_message(self):
        s = spec(chat={"sessions_per_minute": 2, "turns": [3, 3], "think_time_s": 5, "user_words": [10, 10], "reply_words": [20, 20]})
        trace = generate(s)
        session = [r for r in trace if r.group == trace[0].group]
        self.assertEqual([r.id[-2:] for r in session], ["t1", "t2", "t3"])
        self.assertEqual([len(r.messages) for r in session], [2, 4, 6])               # system + history + question
        self.assertEqual(session[1].messages[:2], session[0].messages)                 # turn 2 starts with turn 1's prompt
        self.assertEqual([r.prompt_words for r in session], [60, 90, 120])
        # turn 2 can reuse the system prompt and turn 1's question, but not the reply, which it sends for the first time
        self.assertEqual(session[1].shared_prefix_words, 60)
        self.assertEqual(session[2].shared_prefix_words, 90)
        self.assertTrue(all(a.at <= b.at for a, b in zip(trace, trace[1:])))

    def test_rag_questions_share_the_system_prompt_and_their_document(self):
        s = spec(rag={"queries_per_minute": 60, "documents": 2, "document_words": [300, 300], "question_words": [10, 10]})
        trace = generate(s)
        self.assertEqual(trace[0].shared_prefix_words, 0)
        later = trace[1:]
        self.assertTrue(all(r.shared_prefix_words in (50, 350) for r in later))       # system only, or system + document
        first_per_doc = {}
        for r in trace:
            first_per_doc.setdefault(r.group, r)
        self.assertTrue(all(first.shared_prefix_words < 350 for first in first_per_doc.values()))
        self.assertGreater(stats(trace)["shared_prefix_share"], 0.8)

    def test_single_prompts_share_nothing(self):
        trace = generate({"name": "t", "seed": 1, "duration_s": 600, "max_tokens": 8,
                          "tenants": [{"name": "batch", "single": {"per_minute": 10, "words": [100, 200]}}]})
        self.assertGreater(len(trace), 50)
        self.assertEqual({r.shared_prefix_words for r in trace}, {0})
        self.assertTrue(all(len(r.messages) == 1 for r in trace))

    def test_bad_specs_are_refused(self):
        cases = [
            ({"duration_s": 0}, "duration_s must be"),
            ({"max_tokens": [5, 1]}, "max_tokens must be"),
            ({"tenants": []}, "tenants must be a non-empty list"),
            ({"tenants": [{"name": "a"}]}, "needs at least one of"),
            ({"tenants": [{"name": "a", "single": {"per_minute": 1, "words": 5}}] * 2}, "unique name"),
            ({"tenants": [{"name": "a", "chat": {"sessions_per_minute": 1, "turns": [0, 2], "think_time_s": 1,
                                                 "user_words": 5, "reply_words": 5}}]}, "turns must start at 1"),
            ({"tenants": [{"name": "a", "single": {"per_minute": 1, "words": 5, "colour": 1}}]}, "unknown key"),
            ({"budget": 1}, "unknown key"),
        ]
        with tempfile.TemporaryDirectory() as d:
            for change, message in cases:
                with self.subTest(message=message):
                    path = Path(d, "s.yaml")
                    path.write_text(yaml.safe_dump({**spec(single={"per_minute": 1, "words": 5}), **change}))
                    with self.assertRaisesRegex(SpecError, message):
                        load_spec(path)

    def test_committed_workloads_load(self):
        for path in sorted((ROOT / "workloads").glob("*.yaml")):
            with self.subTest(workload=path.name):
                s = load_spec(path)
                self.assertEqual(s["name"], path.stem)
                self.assertGreater(len(generate(s)), 10)
