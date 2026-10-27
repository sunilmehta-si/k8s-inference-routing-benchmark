# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- `irb compare`: per metric and pair of routers, in how many shared runs each was better; `--held` keeps only the
  differences that held in every run. Reports with repeated runs list those differences too, and a test checks every
  claim the README makes against them.
- The `prefix-load-2x` router: the same scorers as `prefix-load-aware` with load weighted twice, and eight runs of all
  five routers from one CI run in `results/load-weight/`. Doubling the weight kept the cache hits and the median and
  did not spread the work: the load scorer's 128-request queue threshold leaves almost nothing to weigh.
- The cluster workflow takes a `modes` input to run some of the routers.

## [0.1.0] - 2026-10-26

First results, from eight cluster runs of every router on the chat-rag-mix trace. In every run, prefix-aware routing
(the llm-d Router) lifted the pods' prefix-cache hit rate from 64% to 80% and cut median time to first token 27%
against a Kubernetes Service, while sending most requests to two of the four pods; load-aware routing had the best
tail and goodput. Prefix plus load at equal weight did not reliably beat either, which the first run alone had
suggested it did.

### Added
- Workload specs and seeded traces of chat, RAG and one-off traffic, with each request's shared prefix worked out
  exactly; `irb trace generate` and `irb trace stats`.
- An open-loop streaming load client that times TTFT per request and records its own lateness; run summaries with
  goodput; the model servers' prefix-cache and request counters read before and after every run.
- Result files that name their trace and model servers, `irb report` (refusing unfair comparisons) and `irb chart`.
- Four routers on kind, each on its own cluster with fresh simulated vLLM pods: a Kubernetes Service, and the llm-d
  Router v1.0.0 with load-aware, prefix-aware and combined scoring, fail closed; in CI on every code change.
- Repeated runs: the cluster workflow runs every router three times, each on its own cluster; `irb run --repeat`
  labels a run, and `irb report` and `irb chart` show each router's median with its range.
- Committed results, eight runs of each of the four routers, with a report and chart the tests regenerate exactly.

### Fixed (found by the first cluster runs)
- The vLLM render server crashed in a loop as an unprivileged user: importing vLLM asks for a user name the UID has
  no passwd entry for. It now gets one, and writable caches, and stays non-root.
- The simulators exit at startup when the render server is not answering yet; it is now started and awaited first.
- The router's pods were refused by the namespace's Pod Security "restricted" profile; the chart's security
  contexts are now set.

[0.1.0]: https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/releases/tag/v0.1.0
