# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [0.3.0] - 2026-10-30

Three more datasets, 144 cluster runs, that place the earlier results: the prefix routers' pile-up grows with the
pool while `prefix-active` stays even; on a control trace with nothing to cache, the routers that pair prefix
scoring with a rescaled load scorer keep their whole latency advantage, so that advantage is the load scoring; and
the two best routers were not reliably different in the same run. The workflow can now run any pool size, a push
never cancels an experiment, and report titles name the pool.

### Added
- `workloads/one-off-heavy`: a control trace of 1,472 requests, 94% of them one-off prompts, with 3% shared prefix
  against chat-rag-mix's 86%, pinned by fingerprint like the others.
- The cluster workflow takes a `replicas` input, so the same trace can run on a larger pool of simulated pods, and
  report titles name the pool size.
- Eight runs of six routers on eight pods in `results/eight-pods/`: the prefix routers' pile-up grows with the pool
  (prefix-only at 0.29 balance, the chart's default at 0.36), `prefix-active` stays even at 0.93 while beating
  round-robin and load-aware on median, p99 and hits in every run, and load-aware's edge over round-robin is gone.

- Eight runs of six routers on `one-off-heavy` in `results/one-off-heavy/`. With cache hits at 3 to 4% for every
  router, the chart's default, `prefix-active` and `prefix-active-p2` still beat round-robin and load-aware on
  median and p95 in every run and on p99 in all but one: their gain is the load scoring, not the cache. Prefix
  scoring alone cost spread, not time.

### Fixed
- A simulated pod requested 250m CPU; eight of them left the router Pending on a 4-CPU runner and the run failed
  without measuring anything. They request 100m now, and a test holds the whole deployment to 3 CPUs.
- A push cancelled a dispatched experiment in progress (48 jobs, 29 finished). Pushes and dispatches are separate
  concurrency groups now, and only a push cancels a push.

### Added
- Eight runs of `prefix-active-p2` and `router-default` in the same CI run, with prefix-only and round-robin, in
  `results/head-to-head/`. Between the two nothing held on latency or hits; p2 spread the work better in seven runs
  of eight, and one of its runs had a p99 of 3.3 s.

## [0.2.0] - 2026-10-29

The load scorer that spreads the work. Tuning the router's `load-aware` scorer never undid the pile-up prefix routing
causes; swapping it for a scorer that rescales load across the pods did, and `prefix-active` with the prefix at
weight 2 now holds the best p95 and the most cache hits of any router measured. Every claim is checked against the
runs by a test, and `irb compare` shows which differences held in every run.

### Added
- `irb compare`: per metric and pair of routers, in how many shared runs each was better; `--held` keeps only the
  differences that held in every run. Reports with repeated runs list those differences too, and a test checks every
  claim the README makes against them.
- The `prefix-load-2x` router: the same scorers as `prefix-load-aware` with load weighted twice, and eight runs of all
  five routers from one CI run in `results/load-weight/`. Doubling the weight kept the cache hits and the median and
  did not spread the work: the load scorer's 128-request queue threshold leaves almost nothing to weigh.
- The `prefix-load-q8` router: equal weights with the load scorer's queue threshold at 8, the pods' concurrency, and
  eight runs of it beside load-aware and prefix-load-aware in `results/queue-threshold/`. The spread did not change
  either: the load score tops out at 0.5 while a held prefix scores near 1, so weight and threshold have to move
  together.
- The cluster workflow takes a `modes` input to run some of the routers.
- Routers `prefix-queue`, `prefix-running` and `prefix-active`: `prefix-load-aware` with the load scorer swapped for
  the router's queue, running-requests or active-request scorer, which rescale their signal across the pods to 0-1.
- Router `router-default`: the chart's default scoring (queue 2, KV-cache utilization 2, prefix 3). The CI chart job
  fails if the pinned chart's default stops matching it.
- The CI chart job fails when a router configuration names a plugin type the pinned router does not register, before
  any cluster run.
- `docs/scorers.md`: what each scorer reads and how far apart it can put two pods, at the pinned commit, with the
  predictions written before the runs and what the runs showed.
- Eight runs each of the four new routers beside load-aware and prefix-load-aware in `results/scorers/`. The rescaled
  scorers spread the work: `prefix-active` beat prefix-load-aware on median, p95 and p99 time to first token, goodput
  and balance in every run, at four points less hit rate; `prefix-running` spread it most evenly; the chart's default
  kept the most cache hits.

- Routers `prefix-active-p2` and `prefix-active-a2`: `prefix-active` with the prefix, then the in-flight count, at
  weight 2.
- The chart shows each router's load balance beside its prefix-cache hits.
- Eight runs each of the two weight variants beside `prefix-active` in `results/active-weights/`: the prefix at
  weight 2 gave the most cache hits of any router here (83%) and the best p95 and p99, at some spread; the in-flight
  count at weight 2 spread the work most evenly and was slower at every percentile.

### Fixed
- The cluster report compared six routers named by hand; it now compares every router the run measured.
- The README and methodology said `load-aware` reads queued and running work; it reads the waiting queue only.
- One request in 1,672 could fail with a broken pipe: the render server closed idle connections after vLLM's 5 s
  default while the simulators reuse them for 90 s. It now keeps them for 120 s.

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
