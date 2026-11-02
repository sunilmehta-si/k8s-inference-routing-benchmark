## eight-pods-speedup-3 (chat-rag-mix): 1,672 requests on 8 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 129 <sub>(113–138)</sub> | **69 <sub>(64–72)</sub>** | 84 <sub>(73–90)</sub> | 73 <sub>(66–76)</sub> | 86 <sub>(76–94)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 644 <sub>(633–656)</sub> | 461 <sub>(448–472)</sub> | 458 <sub>(440–467)</sub> | **396 <sub>(386–399)</sub>** | 411 <sub>(388–414)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 827 <sub>(815–924)</sub> | 614 <sub>(576–652)</sub> | 569 <sub>(550–586)</sub> | 559 <sub>(552–600)</sub> | **534 <sub>(511–545)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,163 <sub>(2,042–2,243)</sub> | **1,837 <sub>(1,787–1,880)</sub>** | 1,850 <sub>(1,736–1,866)</sub> | 1,903 <sub>(1,808–1,968)</sub> | 1,867 <sub>(1,816–1,949)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 15 <sub>(15–16)</sub> | **14** | **14** | 15 <sub>(14–15)</sub> | 15 <sub>(14–15)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.5% <sub>(99.2%–99.8%)</sub> | 99.6% <sub>(99.5%–99.8%)</sub> | **100.0%** | 99.8% <sub>(99.5%–99.9%)</sub> | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 62.6% <sub>(62.1%–63.5%)</sub> | 79.0% <sub>(77.7%–80.0%)</sub> | 79.4% <sub>(78.6%–80.4%)</sub> | **84.6% <sub>(84.4%–84.6%)</sub>** | 84.2% <sub>(83.9%–84.3%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.911 <sub>(0.826–0.941)</sub> | **0.923 <sub>(0.882–0.959)</sub>** | 0.919 <sub>(0.893–0.937)</sub> | 0.635 <sub>(0.563–0.683)</sub> | 0.706 <sub>(0.653–0.774)</sub> |
| Output tokens per second <sub>higher is better</sub> | **658.2 <sub>(623.4–671.5)</sub>** | 654.8 <sub>(641.1–671.7)</sub> | 653.4 <sub>(639.0–684.0)</sub> | 651.3 <sub>(635.1–672.9)</sub> | 649.0 <sub>(629.1–663.3)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| chat | 330 <sub>(316–353)</sub> | 221 <sub>(213–239)</sub> | 243 <sub>(221–250)</sub> | **141 <sub>(130–158)</sub>** | 164 <sub>(150–191)</sub> |
| rag | 681 <sub>(659–687)</sub> | 469 <sub>(455–505)</sub> | 465 <sub>(444–473)</sub> | **96 <sub>(86–100)</sub>** | 117 <sub>(97–141)</sub> |
| single | 573 <sub>(557–605)</sub> | 471 <sub>(457–476)</sub> | 468 <sub>(454–481)</sub> | **443 <sub>(419–452)</sub>** | 449 <sub>(427–465)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p50 | prefix-active vs precise-active | prefix-active 8, precise-active 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Goodput | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| Load balance | round-robin vs prefix-active-p2 | round-robin 8, prefix-active-p2 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs precise-active-p2 | round-robin 8, precise-active-p2 0 of 8 | 0 | round-robin |
| Load balance | prefix-active vs prefix-active-p2 | prefix-active 8, prefix-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Load balance | precise-active vs precise-active-p2 | precise-active 8, precise-active-p2 0 of 8 | 0 | precise-active |
| Load balance | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| One-off TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
