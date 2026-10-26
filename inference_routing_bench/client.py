"""Replay a trace against an OpenAI-compatible endpoint, open loop, and time every streamed response.

Open loop means each request is sent at its arrival time whatever happened to the earlier ones, the way real users
arrive; a closed loop that waits for answers would hide exactly the queueing a bad router causes. Each request
streams, so time to first token (TTFT) is measured where the user feels it: from sending the request to the first
content token arriving.

Standard library only (http.client in a thread pool), so the client image needs nothing but Python. A thread waits
until its request's time; how late it actually started is recorded, and a run whose client fell behind says so
instead of passing off its own delay as the router's.
"""
from __future__ import annotations

import http.client
import json
import socket
import ssl
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from urllib.parse import urlsplit

from .trace import Request

CHAT_PATH = "/v1/chat/completions"


@dataclass
class Result:
    id: str
    kind: str
    tenant: str
    prompt_words: int
    shared_prefix_words: int
    scheduled_s: float              # when the trace says it arrives, after the start (scaled by speedup)
    lateness_s: float               # how much later than that the client actually sent it
    status: int                     # HTTP status; 0 means no answer at all (connection error or timeout)
    ttft_s: float | None            # send to first content token
    e2e_s: float | None             # send to the end of the stream
    output_chunks: int              # streamed content chunks, about one token each
    prompt_tokens: int | None = None
    completion_tokens: int | None = None
    cached_tokens: int | None = None   # from usage.prompt_tokens_details, when the server reports it
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status == 200 and self.error is None and self.ttft_s is not None

    def to_dict(self) -> dict:
        return asdict(self)


class _Endpoint:
    def __init__(self, url: str, timeout: float):
        parts = urlsplit(url)
        if parts.scheme not in ("http", "https") or not parts.hostname:
            raise ValueError(f"endpoint must be an http(s) URL, got {url!r}")
        self.https = parts.scheme == "https"
        self.host, self.port = parts.hostname, parts.port or (443 if self.https else 80)
        self.base = parts.path.rstrip("/")
        self.timeout = timeout

    def connect(self) -> http.client.HTTPConnection:
        if self.https:
            return http.client.HTTPSConnection(self.host, self.port, timeout=self.timeout, context=ssl.create_default_context())
        return http.client.HTTPConnection(self.host, self.port, timeout=self.timeout)


def _body(req: Request, model: str) -> bytes:
    return json.dumps({"model": model, "messages": list(req.messages), "max_tokens": req.max_tokens, "temperature": 0,
                       "stream": True, "stream_options": {"include_usage": True}}).encode()


def _send(endpoint: _Endpoint, req: Request, model: str, start: float, scheduled: float, headers: dict) -> Result:
    now = time.monotonic()
    if start + scheduled > now:
        time.sleep(start + scheduled - now)
    sent = time.monotonic()
    result = Result(req.id, req.kind, req.tenant, req.prompt_words, req.shared_prefix_words, round(scheduled, 3),
                    round(max(0.0, sent - start - scheduled), 3), 0, None, None, 0)
    conn = endpoint.connect()
    try:
        conn.request("POST", endpoint.base + CHAT_PATH, body=_body(req, model),
                     headers={"Content-Type": "application/json", "Accept": "text/event-stream", **headers})
        resp = conn.getresponse()
        result.status = resp.status
        if resp.status != 200:
            result.error = resp.read(300).decode(errors="replace").strip() or resp.reason
            result.e2e_s = round(time.monotonic() - sent, 4)
            return result
        for raw in resp:
            line = raw.strip()
            if not line.startswith(b"data:"):
                continue
            data = line[5:].strip()
            if data == b"[DONE]":
                break
            chunk = json.loads(data)
            for choice in chunk.get("choices") or []:
                if (choice.get("delta") or {}).get("content"):
                    if result.ttft_s is None:
                        result.ttft_s = round(time.monotonic() - sent, 4)
                    result.output_chunks += 1
            usage = chunk.get("usage")
            if usage:
                result.prompt_tokens = usage.get("prompt_tokens")
                result.completion_tokens = usage.get("completion_tokens")
                result.cached_tokens = (usage.get("prompt_tokens_details") or {}).get("cached_tokens")
        result.e2e_s = round(time.monotonic() - sent, 4)
        if result.ttft_s is None:
            result.error = "the stream ended without a content token"
    except (OSError, http.client.HTTPException, ValueError, socket.timeout) as exc:
        result.status = 0 if result.status == 200 or not result.status else result.status
        result.error = f"{type(exc).__name__}: {exc}"[:300]
        result.e2e_s = round(time.monotonic() - sent, 4)
    finally:
        conn.close()
    return result


def run(url: str, model: str, requests: list[Request], speedup: float = 1.0, timeout: float = 120.0,
        workers: int = 512, headers: dict | None = None, lead_s: float = 1.0) -> list[Result]:
    """Send every request at its arrival time (divided by speedup) and return the results in trace order.

    workers bounds the requests in flight; it must exceed the peak concurrency the trace produces, or requests
    start late, which the results record as lateness."""
    if speedup <= 0 or workers < 1:
        raise ValueError("speedup must be positive and workers at least 1")
    endpoint = _Endpoint(url, timeout)
    first = requests[0].at
    start = time.monotonic() + lead_s
    with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="irb") as pool:
        futures = [pool.submit(_send, endpoint, r, model, start, (r.at - first) / speedup, headers or {}) for r in requests]
        return [f.result() for f in futures]
