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
