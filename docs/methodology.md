# Methodology

## What is measured

| Metric | Where it comes from | Why |
|---|---|---|
| Time to first token (TTFT) p50 / p95 / p99 | The client: from sending the request to the first streamed content token | What a user waits for; prefill and queueing both land here |
| End-to-end latency p95, time per output token | The client | Decode speed, which a router can only harm by overloading a pod |
| Goodput | The client: share of all requests (failures included) whose TTFT met the objective, 1 s by default | One number that a router cannot improve by dropping slow requests |
| Prefix-cache hit rate | The pods: `vllm:prefix_cache_hits_total / vllm:prefix_cache_queries_total`, after minus before | The mechanism, counted by the servers rather than inferred from latency |
| Load balance | The pods: `vllm:request_success_total` per pod; 1.0 is even, 1/n is one pod doing everything | What prefix affinity costs |
| Client lateness p95 | The client: how much later than scheduled it sent requests | A run over 250 ms is flagged: the client, not the router, was the bottleneck |

Percentiles are nearest-rank over the requests that got an answer; failures are counted separately.

## The workload

[`workloads/chat-rag-mix.yaml`](../workloads/chat-rag-mix.yaml): five minutes, three tenants, 1,672 requests
(about 5.6 a second), prompts of 400 to 2,600 words.

- **support**: a 400-word system prompt; chat sessions of 2 to 8 turns 15 s apart on average, each turn resending
  the conversation; and RAG questions over 16 help-centre articles of 900 to 1,600 words, popular ones asked most
  (Zipf, s = 1.1).
- **legal**: a 600-word system prompt and RAG questions over 24 contracts of 1,200 to 2,000 words.
- **batch**: one-off prompts of 400 to 1,500 words that share nothing; no router can help them, so they show what
  each router costs traffic it cannot accelerate.

Prompt text comes from a fixed vocabulary of common English words that the Qwen and Llama tokenizers encode as one
token each, so words are close to tokens. Arrivals are Poisson. The cluster workflow replays the trace at 2x
(`SPEEDUP`), about 11 requests a second, so the pods run at a load where routing decisions show.

### Shared prefix, exactly

Each prompt is a chain of segments: system prompt, document, then messages in order. A request's
`shared_prefix_words` is the length of the longest leading chain of whole segments that an earlier request in the
trace already sent. A chat turn shares everything up to its previous question, but not the previous answer: the
trace's history is written by the generator, not by the simulator, so that answer is new text to the server. Across
the trace this is 86% of all prompt words: the ceiling for any router's prefix-cache hit rate, before evictions.

## The model servers

Four replicas of the [llm-d vLLM simulator](https://github.com/llm-d/llm-d-inference-sim) v1.0.0, configured in
[`deploy/model-servers.yaml`](../deploy/model-servers.yaml):

- Latency: the simulator's "8B-class model on H100, balanced load" reference profile with the per-token calculator.
  Prefill is 30 ms plus 0.25 ms per prompt token not found in the prefix cache; decode is 12 ms per output token;
  both slow to 2x as a pod reaches its concurrency limit of 8.
- Prefix cache: real token blocks. A vLLM render server tokenizes each prompt with the Qwen2.5 tokenizer and the
  simulator hashes 16-token blocks the way vLLM does. Each pod holds 2,048 blocks (32,768 tokens).
- The cache is small next to a real H100's on purpose. The hot set here (system prompts, the popular documents,
  live sessions) is about twice one pod's cache and fits in all four together, the regime where routing decides the
  hit rate. A larger cache relative to the traffic would make every router look the same; a smaller one, none.

## The routers

`round-robin` is a ClusterIP Service. The others are the [llm-d Router](https://github.com/llm-d/llm-d-router)
v1.0.0 in standalone mode: Envoy in the endpoint picker's pod, asking it over ext_proc where each request should go.
The four configurations in [`deploy/router/`](../deploy/router/) differ only in their scorers and weights:

- `load-aware`: `load-aware-scorer`, from the pods' queue and running counts.
- `prefix-aware`: `prefix-cache-scorer` in its default estimate mode: the picker remembers which pod it sent each
  prompt's blocks to and prefers the pod with the longest match. It does not read the pods' caches.
- `prefix-load-aware`: both, weight 1.0 each, the router's own estimated-prefix sample configuration.
- `prefix-load-2x`: both, with the load scorer at weight 2.0. The equal-weight configuration sent most requests to
  two pods in every run; this asks whether favouring load keeps the cache hits and spreads the work.

Shared settings ([`common.yaml`](../deploy/router/common.yaml)): the simulated pods as the `InferencePool`, fail
closed both in the pool and in Envoy, and resource requests a CI runner can hold (the chart's defaults ask for 12
CPUs; a runner has 4).

## Fairness rules

- Every router runs on its own fresh kind cluster with newly created model servers: no warm caches carried over.
- Every router replays the same trace, checked by sha256 when results are compared.
- Results record the model servers' image and full configuration; comparing different ones is refused.
- The load client runs inside the cluster, not through a port-forward, and records its own lateness.

## Repeats

One run on a shared CI runner is an anecdote: the first two cluster runs of this project agreed on what prefix
scoring does to the cache and disagreed on what it does to median latency. So every router runs several times
(three by default, the `repeats` input of the [cluster workflow](../.github/workflows/cluster.yml)), each time on
its own fresh cluster. Runs with the same repeat number start together, one runner per router, so they share a time
window and runner generation.

`irb report` shows each router's median with the range across its runs, and picks the best value by median. The
README states a difference between two routers only when it held in every repeat; a difference that changes sign
between repeats is reported as no difference, however large one run made it look.

## Limits

- **A simulator is not a GPU.** It reproduces the timing model and the cache, not kernel effects such as batching
  efficiency changing with prompt mix. Conclusions are about routing decisions, not absolute latency.
- **One trace, one cluster size.** Ratios of working set to cache, prompt lengths and load all move the result;
  the workload spec makes each of them a parameter.
- **CI runners are noisy neighbours.** Runs share a 4-CPU machine with the Kubernetes control plane. The pods'
  counters are exact, but what they count moves with timing: a router that weighs live load chooses differently
  when a pod is momentarily slow, so hit rate and balance vary between runs too, if less than the latency tails.
  Hence the repeats.
- **Estimated, not precise, prefix scoring.** The picker guesses where blocks live from its own routing history;
  the precise mode, which reads the pods' KV-cache events, is the next configuration to add.
