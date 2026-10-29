# What each scorer gives a pod

The endpoint picker multiplies each scorer's score for a pod by the scorer's weight, adds them up, and the max-score
picker sends the request to the pod with the highest total (pods that tie are taken in turn). So whether a load
scorer can pull a request away from the pod that already holds its prompt's prefix comes down to one comparison: how
far apart can the load scorer put two pods, against how far apart the prefix scorer puts them.

Everything below is read from the llm-d Router source at the pinned commit
[`b9393d1`](https://github.com/llm-d/llm-d-router/tree/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92) (v1.0.0).

| Scorer | Reads | Score for a pod | Widest gap between two pods | Modes |
|---|---|---|---|---|
| [`prefix-cache-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/prefix/plugin.go#L135-L187) | The router's own record of which prompt blocks it sent to which pod | Share of this prompt's blocks the pod holds | 1; about 0.98 for a RAG prompt whose document one pod has seen | every `prefix-*`, `router-default` |
| [`load-aware-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/loadaware/load_aware.go#L100-L116) | Waiting queue, scraped | 0.5 when empty, else 0.5 × (1 − waiting / threshold), threshold 128 | 0.5 | `load-aware`, `prefix-load-*` |
| [`queue-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/queuedepth/queue.go#L88-L117) | Waiting queue, scraped | (longest − its own) / (longest − shortest); 1 for every pod when the queues are equal | 1, but 0 while no pod has a longer queue than another | `prefix-queue`, `router-default` |
| [`running-requests-size-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/runningrequests/runningrequest.go#L88-L117) | Requests running, scraped | The same rescaling, of running counts | 1 | `prefix-running` |
| [`active-request-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/activerequest/active_request.go#L170-L203) | Requests the router sent to the pod and has not seen finish: its own count, not scraped | 1 when idle, else (busiest − its own) / busiest | 1 | `prefix-active` |
| [`kv-cache-utilization-scorer`](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/framework/plugins/scheduling/scorer/kvcacheutilization/kvcache_utilization.go#L86-L96) | KV-cache usage, scraped; the simulator reports the blocks running requests hold over all blocks | 1 − usage | The difference in usage | `router-default` |

"Scraped" means read from the pods' `/metrics`, by default every
[50 ms](https://github.com/llm-d/llm-d-router/blob/b9393d1a9f1d5a72ecd86f8d2b643ab54c2a9b92/pkg/epp/server/options.go#L53),
so requests that arrive between two scrapes are all scored on the same numbers. The active-request count changes as
the router sends each request.

## What the ranges predict

Written before the runs of the last four modes, so the results can prove it wrong.

- At equal weights, a load scorer takes a request away from the pod holding its prefix only when the gap it puts
  between that pod and another is larger than the prefix gap. For a RAG prompt that is close to 1.
- `load-aware` can never do it (at most 0.5), which is what the `prefix-load-2x` and `prefix-load-q8` runs showed.
- The three rescaled scorers can, but only at the extreme: the pod holding the prefix has to be the busiest and the
  other the least busy, because only then is their gap the full 1. They should move some traffic off the busiest pod,
  not spread it evenly.
- `queue-scorer` only acts while some pod has requests waiting. At the load in this trace queues are short, so of the
  three it should change the least.
- `router-default` weights the prefix 3 and each load signal 2, so a full prefix match (about 3) can only be beaten
  when the busy pod is the busiest by both queue and KV-cache usage. Expect it to behave much like `prefix-aware`.

## What happened

Eight runs of each in [one CI run](https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/actions/runs/40650965766)
([results](../results/scorers/README.md)). Two predictions held, two did not.

- **Held: `load-aware` cannot undo the pile-up.** Its balance was again far above prefix-load-aware's (0.95 against
  0.61), and prefix-load-aware again sent most requests to a few pods.
- **Wrong: the rescaled scorers would move only some traffic.** `prefix-running` (balance 0.98) and `prefix-active`
  (0.95) spread the work as evenly as `load-aware`. The prediction got the mechanism right and the frequency wrong:
  a rescaled scorer acts when the pod holding the prefix is the busiest, and a pile-up makes it the busiest, so the
  extreme case is every case that matters. Each request that lands on the busiest pod makes the next one less likely
  to.
- **Held: `queue-scorer` changes the least.** Balance 0.66, close to prefix-load-aware's and below load-aware's in
  every run. Queues rarely differ at this load.
- **Partly wrong: `router-default` would behave like `prefix-aware`.** It kept prefix routing's cache hits (83%, the
  most of any router here) and much of its pile-up (0.68), as predicted, but it beat prefix-load-aware on median,
  p95 and p99 in every run and had the best p95 of all six. A likely reason, not measured here: the weight-3 prefix
  match decides when one pod clearly holds the prompt, and the two load signals at weight 2 decide between pods whose
  matches are close, a case the prediction did not consider.

## Weights around prefix-active

[Eight runs each](../results/active-weights/README.md) of `prefix-active` with the prefix at weight 2, then the
in-flight count at weight 2. The prefix at 2 kept the most cache hits of any router (83%) with the best p95 and p99,
at balance 0.85; the count at 2 spread the work most evenly and was slower at every percentile. The in-flight count
already spans 0 to 1, so doubling it only lets an evenly loaded pod outvote a cached one more often, and a cache miss
costs more than a short wait. Doubling the prefix instead lets the count act only when a pod is far busier than the
rest, which is the pile-up case.
