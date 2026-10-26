"""Request traces: one JSON object per line, in arrival order.

A request carries the chat messages to send and what is known about them in advance: when it arrives, which kind
of traffic it is (chat, rag or single), which session or document it belongs to, and how many of its leading words
an earlier request already sent. That last number is what a prefix-aware router can exploit and a round-robin one
cannot, so the report can say how much of the possible saving each router actually got.
"""
from __future__ import annotations

import math

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path

from .text import count

KINDS = ("chat", "rag", "single")


class TraceError(ValueError):
    pass


@dataclass(frozen=True)
class Request:
    id: str
    at: float                       # seconds after the start of the trace
    kind: str                       # chat, rag or single
    tenant: str
    group: str                      # the chat session or RAG document whose prefix it shares; the id for single
    messages: tuple[dict, ...]      # OpenAI chat messages: {"role": ..., "content": ...}
    max_tokens: int
    shared_prefix_words: int = 0    # leading prompt words an earlier request in the trace already sent
    extra: dict = field(default_factory=dict, compare=False)

    @property
    def prompt_words(self) -> int:
        return sum(count(m["content"]) for m in self.messages)

    def to_json(self) -> str:
        data = asdict(self)
        data["messages"] = list(self.messages)
        if not data["extra"]:
            del data["extra"]
        return json.dumps(data, separators=(",", ":"))


def _check(raw: dict, line: int) -> Request:
    where = f"line {line}"
    for key in ("id", "at", "kind", "tenant", "group", "messages", "max_tokens"):
        if key not in raw:
            raise TraceError(f"{where}: missing '{key}'")
    unknown = set(raw) - {"id", "at", "kind", "tenant", "group", "messages", "max_tokens", "shared_prefix_words", "extra"}
    if unknown:
        raise TraceError(f"{where}: unknown field(s) {', '.join(sorted(unknown))}")
    if raw["kind"] not in KINDS:
        raise TraceError(f"{where}: kind must be one of {', '.join(KINDS)}, got {raw['kind']!r}")
    if not isinstance(raw["at"], (int, float)) or raw["at"] < 0:
        raise TraceError(f"{where}: 'at' must be a number of seconds >= 0")
    if not isinstance(raw["max_tokens"], int) or raw["max_tokens"] < 1:
        raise TraceError(f"{where}: 'max_tokens' must be a positive integer")
    messages = raw["messages"]
    if not isinstance(messages, list) or not messages:
        raise TraceError(f"{where}: 'messages' must be a non-empty list")
    for m in messages:
        if not isinstance(m, dict) or m.get("role") not in ("system", "user", "assistant") or not isinstance(m.get("content"), str):
            raise TraceError(f"{where}: every message needs a role (system, user or assistant) and string content")
    if messages[-1]["role"] != "user":
        raise TraceError(f"{where}: the last message must come from the user")
    req = Request(id=str(raw["id"]), at=float(raw["at"]), kind=raw["kind"], tenant=str(raw["tenant"]), group=str(raw["group"]),
                  messages=tuple(messages), max_tokens=raw["max_tokens"],
                  shared_prefix_words=int(raw.get("shared_prefix_words", 0)), extra=dict(raw.get("extra") or {}))
    if not 0 <= req.shared_prefix_words <= req.prompt_words:
        raise TraceError(f"{where}: shared_prefix_words must be between 0 and the prompt's {req.prompt_words} words")
    return req


def load(path: str | Path) -> list[Request]:
    requests: list[Request] = []
    seen: set[str] = set()
    for n, line in enumerate(Path(path).read_text().splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except ValueError as exc:
            raise TraceError(f"line {n}: not JSON: {exc}") from exc
        req = _check(raw, n)
        if req.id in seen:
            raise TraceError(f"line {n}: duplicate id {req.id!r}")
        if requests and req.at < requests[-1].at:
            raise TraceError(f"line {n}: requests must be in arrival order")
        seen.add(req.id)
        requests.append(req)
    if not requests:
        raise TraceError(f"{path}: no requests")
    return requests


def dump(requests: list[Request], path: str | Path) -> None:
    Path(path).write_text("".join(r.to_json() + "\n" for r in requests))


def fingerprint(path: str | Path) -> str:
    """sha256 of the trace file, recorded with every result so a result names exactly what it replayed."""
    return "sha256:" + hashlib.sha256(Path(path).read_bytes()).hexdigest()


def stats(requests: list[Request]) -> dict:
    """What a trace asks of the cluster: volume, mix, prompt sizes and how much of the prompt text repeats."""
    def pct(values: list[int], p: float) -> int:
        ordered = sorted(values)
        return ordered[min(len(ordered) - 1, max(0, math.ceil(p / 100 * len(ordered)) - 1))]

    words = [r.prompt_words for r in requests]
    shared = sum(r.shared_prefix_words for r in requests)
    duration = requests[-1].at - requests[0].at
    by_kind = {k: sum(1 for r in requests if r.kind == k) for k in KINDS}
    return {
        "requests": len(requests),
        "duration_s": round(duration, 1),
        "rate_per_s": round(len(requests) / duration, 2) if duration > 0 else None,
        "by_kind": {k: v for k, v in by_kind.items() if v},
        "tenants": len({r.tenant for r in requests}),
        "groups": len({r.group for r in requests}),
        "prompt_words": {"p50": pct(words, 50), "p95": pct(words, 95), "max": max(words), "total": sum(words)},
        "max_tokens_total": sum(r.max_tokens for r in requests),
        "shared_prefix_share": round(shared / sum(words), 3) if words else 0.0,
    }
