# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.1.0] - 2026-10-26

First results, from a green cluster run: on the chat-rag-mix trace, prefix plus load routing (the llm-d Router)
cut median time to first token 38% against a Kubernetes Service and lifted the pods' prefix-cache hit rate from
64% to 82%; prefix-only routing overloaded pods and raised p99 by 36%.

### Added
- Workload specs and seeded traces of chat, RAG and one-off traffic, with each request's shared prefix worked out
  exactly; `irb trace generate` and `irb trace stats`.
- An open-loop streaming load client that times TTFT per request and records its own lateness; run summaries with
  goodput; the model servers' prefix-cache and request counters read before and after every run.
- Result files that name their trace and model servers, `irb report` (refusing unfair comparisons) and `irb chart`.
- Four routers on kind, each on its own cluster with fresh simulated vLLM pods: a Kubernetes Service, and the llm-d
  Router v1.0.0 with load-aware, prefix-aware and combined scoring, fail closed; in CI on every push.
- Committed results for the four routers, with a report and chart the tests regenerate exactly.

### Fixed (found by the first cluster runs)
- The vLLM render server crashed in a loop as an unprivileged user: importing vLLM asks for a user name the UID has
  no passwd entry for. It now gets one, and writable caches, and stays non-root.
- The simulators exit at startup when the render server is not answering yet; it is now started and awaited first.
- The router's pods were refused by the namespace's Pod Security "restricted" profile; the chart's security
  contexts are now set.

[0.1.0]: https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/releases/tag/v0.1.0
