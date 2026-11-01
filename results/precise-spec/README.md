## precise-spec (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | prefix-active | precise-active | precise-active-spec |
|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | **72 <sub>(67–76)</sub>** | 83 <sub>(77–88)</sub> | 78 <sub>(71–85)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 534 <sub>(508–544)</sub> | 503 <sub>(490–523)</sub> | **487 <sub>(479–512)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 713 <sub>(668–733)</sub> | **631 <sub>(611–646)</sub>** | 637 <sub>(613–662)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,031 <sub>(1,950–2,123)</sub> | **1,967 <sub>(1,900–1,999)</sub>** | 1,993 <sub>(1,930–2,036)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 15 <sub>(15–16)</sub> | 15 <sub>(15–16)</sub> | 15 <sub>(15–16)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.6% <sub>(99.6%–99.8%)</sub> | **100.0%** | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 76.9% <sub>(75.9%–77.4%)</sub> | 79.1% <sub>(78.5%–79.7%)</sub> | **79.3% <sub>(79.0%–79.9%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | **0.966 <sub>(0.937–0.986)</sub>** | 0.947 <sub>(0.921–0.986)</sub> | 0.961 <sub>(0.909–0.988)</sub> |
| Output tokens per second <sub>higher is better</sub> | 440.0 <sub>(425.8–456.3)</sub> | 430.4 <sub>(427.6–442.5)</sub> | **440.8 <sub>(432.6–449.8)</sub>** |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | prefix-active | precise-active | precise-active-spec |
|---|---|---|---|
| chat | 240 <sub>(217–275)</sub> | 232 <sub>(218–265)</sub> | **218 <sub>(200–238)</sub>** |
| rag | 563 <sub>(537–574)</sub> | 520 <sub>(510–530)</sub> | **498 <sub>(482–520)</sub>** |
| single | 517 <sub>(496–539)</sub> | 514 <sub>(497–543)</sub> | **509 <sub>(485–529)</sub>** |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | prefix-active vs precise-active | prefix-active 8, precise-active 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs precise-active-spec | prefix-active 8, precise-active-spec 0 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Prefix-cache hit rate | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| RAG TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
