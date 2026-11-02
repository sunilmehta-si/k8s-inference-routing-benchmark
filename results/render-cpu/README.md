## render-cpu (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | prefix-active | precise-active |
|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | **73 <sub>(69–76)</sub>** | 84 <sub>(78–91)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 531 <sub>(522–548)</sub> | **506 <sub>(489–515)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 686 <sub>(658–708)</sub> | **644 <sub>(611–658)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | **2,014 <sub>(1,979–2,069)</sub>** | 2,018 <sub>(1,971–2,041)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 15 <sub>(15–16)</sub> | 15 <sub>(15–16)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.6% <sub>(99.6%–99.8%)</sub> | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 76.9% <sub>(75.8%–77.3%)</sub> | **79.0% <sub>(78.5%–79.3%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | 0.966 <sub>(0.937–0.974)</sub> | **0.968 <sub>(0.933–0.988)</sub>** |
| Output tokens per second <sub>higher is better</sub> | 435.6 <sub>(422.1–437.5)</sub> | **440.2 <sub>(430.6–450.4)</sub>** |
| Errors <sub>lower is better</sub> | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | prefix-active | precise-active |
|---|---|---|
| chat | **231 <sub>(211–248)</sub>** | 249 <sub>(212–275)</sub> |
| rag | 557 <sub>(534–580)</sub> | **519 <sub>(514–523)</sub>** |
| single | **518 <sub>(489–534)</sub>** | 521 <sub>(497–542)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | prefix-active vs precise-active | prefix-active 8, precise-active 0 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
