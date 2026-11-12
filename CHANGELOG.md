# Changelog

All notable changes to this project. The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

### Added
- Dependabot for the actions and PyYAML, each update 14 days behind its release like the pins `irb versions` checks,
  with `tests/test_dependabot.py` holding the cooldown.
- `irb versions` names an earlier release that is already 14 days old when the newest is not, and `--strict` fails
  on it. Before, such a pin read as "too new" until the newest release aged (the simulator's v1.1.0 would have
  waited behind v1.2.0 until 24 Nov). `--json` adds `adoptable_now`, `ready` and `ready_published`.

### Changed
- The router's Envoy is v1.40.2, was v1.33.2 (seven minor versions behind a release past the 14-day rule; the image was
  built on 2026-10-27). The digest is the OCI index the registry returns for the `distroless-v1.40.2` tag, resolved the
  same way as the one it replaces, which it reproduced exactly. The chart's Envoy bootstrap is unchanged, so a cluster run
  on the branch, three runs each of `load-aware`, `prefix-active` and `precise-active`
  ([run 42758591590](https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/actions/runs/42758591590)), checks
  that it still loads and routes: all 1,672 requests of every run returned 200. Against the committed eight-run ranges,
  TTFT p50 was `load-aware` 106 ms against 109 (99-126) and `prefix-active` 71 ms against 71 (67-74), cache hits 64.0%
  against 64.4% and 77.2% against 76.7%. `precise-active` p50 was 73 ms against 84 (78-86), below the range as in the
  render-server run below, with cache hits 79.1% against 79.1%. Goodput was above the committed range in all six
  `load-aware` and `prefix-active` runs (99.9% and 100% against 99.5% and 99.6%); three runs on one day are too few to
  credit Envoy with that, and the datasets under `results/` stay as measured on v1.33.2.
- The render server is vLLM v0.32.0, was v0.21.0 (eleven minor versions behind a release past the 14-day rule). A cluster
  run on the branch, three runs each of `prefix-active` and `precise-active`
  ([run 41584187886](https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/actions/runs/41584187886)), had no
  errors and landed in the committed eight-run ranges: `precise-active` TTFT p50 76 ms (68-80) against 84 (78-86) and
  cache hits 79.4% against 79.1%, `prefix-active` p50 71 ms against 71. The datasets under `results/` were measured with
  the render server at v0.21.0; it only tokenizes for the precise routers, whose scoring the datasets already compare.
- Tests send bursts to a fake model server that listens with a backlog of 128, not the standard library's 5, which
  dropped connections from a burst of twelve requests.

### Fixed
- `irb versions` reports the newest stable release (the highest plain x.y.z that is not a draft or prerelease), not the
  one GitHub marks latest. vLLM marks release candidates, so the render image was compared with v0.33.0rc3, shown as
  "unknown", and its real lag behind v0.32.0 was hidden.

## [0.6.0] - 2026-11-02

Three datasets under load, 120 cluster runs: the busier the pods, the more the router matters and the less the
routers differ. At three times the trace's rate the Service's median is 3.6x the best router's; at four times it
passes a second and half its requests miss the objective while every router stays under 170 ms, and the routers'
differences stop holding; with eight pods the rate is absorbed and prefix weight 2 trades spread for hits and tail
in every run. Results now record the rate they were replayed at, the versions report checks the kind node image
against the kind release that built it, and the weekly schedule runs six representative routers.

### Added
- `results/speedup-3/`: the trace at three times its rate. The Service's median is 3.6x `prefix-active`'s and a tenth
  of its requests miss the objective; the precise index keeps its tail and goodput in every run.
- `results/speedup-4/`: the trace at four times its rate, where the pods saturate. The Service's median passes a
  second and 47% of its requests miss the objective; among the routers two differences hold.
- `results/eight-pods-speedup-3/`: eight pods at three times the rate. The pool absorbs the load; prefix weight 2 buys
  hits and tail for spread in every run, and the real cache picture on that router has the best p99 and spreads its
  pile-up.
- The weekly schedule runs six representative routers instead of all seventeen; a push still runs every router once.
- The README's dataset index links every CI run a dataset came from, and a "What to use" section gives the four
  choices the datasets support.
- `irb versions` checks that the pinned kind node image, digest and all, is one the pinned kind release's notes list,
  and lists the pins it does not compare with the reason.

### Changed
- Pull requests are reviewed with the code review tool at v0.9.0.

## [0.5.0] - 2026-11-02

Six datasets, 160 cluster runs, that place the real cache picture: it pays where the load scorer is strong enough to
move prompts away from the pod that holds them (prefix weight 1), spreads the approximate router's pile-up at weight 2
instead of adding hits, and keeps its tail advantage on eight pods and on a trace with nothing to cache. Its median
cost is the extra hop to the tokenizer, not tokenizer CPU, and it disappears behind long prompts. Speculative indexing
is a small gain on four pods and a loss on eight. `irb dataset` turns a run's artifact into a committed dataset.

### Added
- Eight runs of `precise-active-spec` beside `precise-active` and `prefix-active` in `results/precise-spec/`: speculative
  indexing is a small gain in seven of eight runs; the median cost that remains is the tokenizer round trip.
- `precise-active-p2`, the best approximate router with the precise producer, and eight runs of the pair in
  `results/precise-p2/`: no hits gain at prefix weight 2, a better tail in every run, the median cost again.
- Eight runs of six routers on eight pods in `results/precise-eight-pods/`: the weight-1 gain holds; at weight 2 the
  precise index spreads the approximate router's pile-up instead of adding hits; speculative indexing hurts.
- `irb dataset`: a committed `results/<name>/` from a run's comparison artifact, in a stated router order, refusing a
  router with the wrong number of runs, a file holding another router's run or runs that are not comparable.
- The cluster workflow stamps each result with its run URL before the report, and takes a `render_cpu` input (default
  500m); a result records the render server's CPU, so runs with different values are refused side by side.
- The README indexes every committed dataset with its question and router count, and a test holds the list.
- `results/render-cpu/` (the render server at 1000m: the median cost is the hop, not tokenizer CPU) and
  `results/precise-control/` (the precise router on the control trace: level medians, a better tail in every run).
- The run script fails within two minutes when the load client cannot be scheduled, with the pod's events and the
  node's allocated resources, instead of waiting out the workflow timeout.

## [0.4.0] - 2026-10-31

The endpoint picker can now score with the pods' real cache contents instead of its own estimate, and the first
dataset says what that is worth: two to three more points of cache hits in every pair and every run, a better tail
where a load scorer sits beside the prefix score, and a tokenizer round trip at the median. A versions report says
which pins have newer releases upstream.

### Added
- The simulated pods publish their KV-cache block events over ZMQ on port 5557, as vLLM does.
- `precise-aware`, `precise-active`, `precise-queue`: `prefix-aware`, `prefix-active` and `prefix-queue` with the
  router's precise prefix-cache producer, which subscribes to every pod's events and indexes the blocks it holds;
  prompts are tokenized on the pods' render server. Same scorers and weights as the counterparts.
- Eight runs of the three pairs in `results/precise/`, with the claims in the README tested against them.
- `precise-active-spec`: `precise-active` with the producer's speculative indexing, which credits the chosen pod with a
  prompt's blocks at once instead of waiting for its event; its runs are the next dataset.
- `irb versions` (and `make versions`): each pin in `deploy/versions.env` against the latest release upstream, with
  the date from which a newer release counts as adoptable (14 days after publication); image pins are compared by the
  release in their tag, and every pin is either compared or listed with the reason it is not. A CI job posts the
  table weekly.
- [docs/scorers.md](docs/scorers.md) explains the approximate and precise producers and what each can get wrong.

### Fixed
- Report tables show the errors row as a count, not `0.000`.

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
