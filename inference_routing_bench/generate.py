"""Seeded request traces from a workload spec (workloads/*.yaml).

Three kinds of traffic, chosen because they differ in how much prompt text repeats:

* chat: multi-turn sessions. Every turn resends the tenant's system prompt and the whole conversation so far, so
  turn k shares everything but its newest message with turn k-1 of the same session.
* rag: questions over a tenant's documents. The system prompt and the document repeat across every question about
  that document; popular documents (Zipf) repeat most.
* single: one-off prompts with nothing in common, the control: no router can find a prefix to reuse.

A request's prompt is a chain of segments (system prompt, document, messages). Its shared_prefix_words is the
length of the longest leading chain of whole segments some earlier request already sent, which is what a perfect
prefix cache could skip.
"""
from __future__ import annotations

import random
from dataclasses import dataclass
from pathlib import Path

import yaml

from .text import words
from .trace import Request


class SpecError(ValueError):
    pass


@dataclass(frozen=True)
class Range:
    low: int
    high: int

    @classmethod
    def parse(cls, value, what: str) -> "Range":
        if isinstance(value, int):
            value = [value, value]
        if not (isinstance(value, list) and len(value) == 2 and all(isinstance(v, int) for v in value) and 0 <= value[0] <= value[1]):
            raise SpecError(f"{what} must be an integer or [low, high] with 0 <= low <= high")
        return cls(value[0], value[1])

    def draw(self, rng: random.Random) -> int:
        return rng.randint(self.low, self.high)


SPEC_KEYS = {"name", "seed", "duration_s", "max_tokens", "tenants"}
TENANT_KEYS = {"name", "system_prompt_words", "chat", "rag", "single"}
CHAT_KEYS = {"sessions_per_minute", "turns", "think_time_s", "user_words", "reply_words"}
RAG_KEYS = {"queries_per_minute", "documents", "document_words", "question_words", "zipf"}
SINGLE_KEYS = {"per_minute", "words"}


def _keys(data: dict, allowed: set[str], where: str) -> None:
    if not isinstance(data, dict):
        raise SpecError(f"{where} must be a mapping")
    unknown = set(data) - allowed
    if unknown:
        raise SpecError(f"{where}: unknown key(s) {', '.join(sorted(unknown))}")


def load_spec(path: str | Path) -> dict:
    spec = yaml.safe_load(Path(path).read_text())
    _keys(spec, SPEC_KEYS, str(path))
    for key in ("name", "seed", "duration_s", "max_tokens", "tenants"):
        if key not in spec:
            raise SpecError(f"{path}: missing '{key}'")
    if not isinstance(spec["duration_s"], (int, float)) or spec["duration_s"] <= 0:
        raise SpecError("duration_s must be a positive number of seconds")
    Range.parse(spec["max_tokens"], "max_tokens")
    if not isinstance(spec["tenants"], list) or not spec["tenants"]:
        raise SpecError("tenants must be a non-empty list")
    names = set()
    for t in spec["tenants"]:
        where = f"tenant {t.get('name', '?') if isinstance(t, dict) else '?'}"
        _keys(t, TENANT_KEYS, where)
        if not t.get("name") or t["name"] in names:
            raise SpecError(f"{where}: every tenant needs a unique name")
        names.add(t["name"])
        Range.parse(t.get("system_prompt_words", 0), f"{where}: system_prompt_words")
        if not any(k in t for k in ("chat", "rag", "single")):
            raise SpecError(f"{where}: needs at least one of chat, rag or single")
        if "chat" in t:
            _keys(t["chat"], CHAT_KEYS, f"{where}: chat")
            for k in ("turns", "user_words", "reply_words"):
                Range.parse(t["chat"][k], f"{where}: chat.{k}")
            if Range.parse(t["chat"]["turns"], "turns").low < 1:
                raise SpecError(f"{where}: chat.turns must start at 1 or more")
        if "rag" in t:
            _keys(t["rag"], RAG_KEYS, f"{where}: rag")
            for k in ("document_words", "question_words"):
                Range.parse(t["rag"][k], f"{where}: rag.{k}")
            if not isinstance(t["rag"]["documents"], int) or t["rag"]["documents"] < 1:
                raise SpecError(f"{where}: rag.documents must be a positive integer")
        if "single" in t:
            _keys(t["single"], SINGLE_KEYS, f"{where}: single")
            Range.parse(t["single"]["words"], f"{where}: single.words")
    return spec


def _arrivals(rng: random.Random, per_minute: float, duration: float) -> list[float]:
    """Poisson arrival times in [0, duration)."""
    if per_minute <= 0:
        return []
    out, t = [], 0.0
    while True:
        t += rng.expovariate(per_minute / 60.0)
        if t >= duration:
            return out
        out.append(t)


def _zipf_choice(rng: random.Random, n: int, s: float) -> int:
    weights = [1.0 / (i + 1) ** s for i in range(n)]
    return rng.choices(range(n), weights=weights)[0]


@dataclass
class _Draft:
    at: float
    id: str
    kind: str
    tenant: str
    group: str
    segments: list[tuple[str, int]]       # (segment id, words) in prompt order
    messages: list[dict]
    max_tokens: int


def _tenant(spec: dict, t: dict, seed) -> list[_Draft]:
    name, duration = t["name"], float(spec["duration_s"])
    max_tokens = Range.parse(spec["max_tokens"], "max_tokens")
    rng = random.Random(f"{seed}/{name}/system")
    system_words = Range.parse(t.get("system_prompt_words", 0), "system_prompt_words").draw(rng)
    system = words(rng, system_words)
    head = [{"role": "system", "content": system}] if system_words else []
    head_segments = [(f"{name}/system", system_words)] if system_words else []
    drafts: list[_Draft] = []

    if "chat" in t:
        c = t["chat"]
        rng = random.Random(f"{seed}/{name}/chat")
        turns, user, reply = Range.parse(c["turns"], ""), Range.parse(c["user_words"], ""), Range.parse(c["reply_words"], "")
        for s, start in enumerate(_arrivals(rng, c["sessions_per_minute"], duration)):
            session = f"{name}-chat-{s:04d}"
            history: list[dict] = []
            segments = list(head_segments)
            at = start
            for k in range(1, turns.draw(rng) + 1):
                if k > 1:
                    at += rng.expovariate(1.0 / c["think_time_s"])
                if at >= duration:
                    break
                n_user = user.draw(rng)
                question = {"role": "user", "content": words(rng, n_user)}
                drafts.append(_Draft(at, f"{session}-t{k}", "chat", name, session, segments + [(f"{session}/u{k}", n_user)],
                                     head + history + [question], max_tokens.draw(rng)))
                n_reply = reply.draw(rng)
                history += [question, {"role": "assistant", "content": words(rng, n_reply)}]
                segments += [(f"{session}/u{k}", n_user), (f"{session}/a{k}", n_reply)]

    if "rag" in t:
        r = t["rag"]
        rng = random.Random(f"{seed}/{name}/rag")
        doc_words, question = Range.parse(r["document_words"], ""), Range.parse(r["question_words"], "")
        documents = []
        for d in range(r["documents"]):
            n = doc_words.draw(rng)
            documents.append((f"{name}/doc{d:02d}", n, words(rng, n)))
        for q, at in enumerate(_arrivals(rng, r["queries_per_minute"], duration)):
            doc_id, n_doc, text = documents[_zipf_choice(rng, len(documents), float(r.get("zipf", 1.0)))]
            n_q = question.draw(rng)
            content = f"{text} {words(rng, n_q)}"
            drafts.append(_Draft(at, f"{name}-rag-{q:05d}", "rag", name, doc_id, head_segments + [(doc_id, n_doc), (f"{name}/q{q}", n_q)],
                                 head + [{"role": "user", "content": content}], max_tokens.draw(rng)))

    if "single" in t:
        o = t["single"]
        rng = random.Random(f"{seed}/{name}/single")
        size = Range.parse(o["words"], "")
        for i, at in enumerate(_arrivals(rng, o["per_minute"], duration)):
            n = size.draw(rng)
            rid = f"{name}-single-{i:05d}"
            drafts.append(_Draft(at, rid, "single", name, rid, [(rid, n)], [{"role": "user", "content": words(rng, n)}], max_tokens.draw(rng)))
    return drafts


def generate(spec: dict, seed=None) -> list[Request]:
    """The trace for spec, in arrival order. The same spec and seed always give the same trace."""
    seed = spec["seed"] if seed is None else seed
    drafts = sorted((d for t in spec["tenants"] for d in _tenant(spec, t, seed)), key=lambda d: (d.at, d.id))
    seen: set[tuple[str, ...]] = set()
    out = []
    for d in drafts:
        chain, shared, total = [], 0, 0
        for seg_id, n in d.segments:
            chain.append(seg_id)
            total += n
            key = tuple(chain)
            if key in seen:
                shared = total
            seen.add(key)
        out.append(Request(id=d.id, at=round(d.at, 3), kind=d.kind, tenant=d.tenant, group=d.group,
                           messages=tuple(d.messages), max_tokens=d.max_tokens, shared_prefix_words=shared))
    return out
