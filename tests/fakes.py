"""A fake OpenAI-compatible streaming server for the client tests: it remembers prompts like a prefix cache, so a
repeated prompt answers faster, and it can be told to fail."""
from __future__ import annotations

import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer


class FakeLLM(BaseHTTPRequestHandler):
    prefill_s = 0.05          # first token after this, unless the prompt was seen before
    cached_prefill_s = 0.005
    token_s = 0.002
    status = 200              # answer with this status instead of streaming
    seen: set = set()
    bodies: list = []
    lock = threading.Lock()

    def do_POST(self):                                         # noqa: N802
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        with FakeLLM.lock:
            FakeLLM.bodies.append(body)
            prompt = json.dumps(body["messages"])
            hit = prompt in FakeLLM.seen
            FakeLLM.seen.add(prompt)
        if FakeLLM.status != 200:
            data = b'{"error": "overloaded"}'
            self.send_response(FakeLLM.status)
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.end_headers()
        time.sleep(FakeLLM.cached_prefill_s if hit else FakeLLM.prefill_s)
        tokens = body["max_tokens"]
        for i in range(tokens):
            chunk = {"choices": [{"index": 0, "delta": {"content": f"tok{i} "}}]}
            self.wfile.write(b"data: " + json.dumps(chunk).encode() + b"\n\n")
            self.wfile.flush()
            time.sleep(FakeLLM.token_s)
        prompt_tokens = sum(len(m["content"].split()) for m in body["messages"])
        usage = {"choices": [], "usage": {"prompt_tokens": prompt_tokens, "completion_tokens": tokens,
                                          "prompt_tokens_details": {"cached_tokens": prompt_tokens if hit else 0}}}
        self.wfile.write(b"data: " + json.dumps(usage).encode() + b"\n\ndata: [DONE]\n\n")

    def log_message(self, *args):
        pass


def start() -> tuple[ThreadingHTTPServer, str]:
    FakeLLM.seen, FakeLLM.bodies, FakeLLM.status = set(), [], 200
    server = ThreadingHTTPServer(("127.0.0.1", 0), FakeLLM)
    server.daemon_threads = True
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_port}"
