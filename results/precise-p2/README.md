## precise-p2 (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | prefix-active-p2 | precise-active-p2 |
|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | **75 <sub>(72–76)</sub>** | 85 <sub>(76–90)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | **447 <sub>(439–463)</sub>** | 459 <sub>(454–475)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 658 <sub>(608–692)</sub> | **615 <sub>(588–634)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,041 <sub>(1,973–2,127)</sub> | **2,038 <sub>(1,999–2,092)</sub>** |
| Time per output token p50 (ms) <sub>lower is better</sub> | 16 | 16 <sub>(15–16)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.7% <sub>(99.6%–99.9%)</sub> | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | **83.5% <sub>(83.1%–83.9%)</sub>** | 83.0% <sub>(82.9%–83.3%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.814 <sub>(0.781–0.873)</sub> | **0.833 <sub>(0.789–0.869)</sub>** |
| Output tokens per second <sub>higher is better</sub> | 440.1 <sub>(430.9–455.3)</sub> | **442.8 <sub>(431.4–458.5)</sub>** |
| Errors <sub>lower is better</sub> | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | prefix-active-p2 | precise-active-p2 |
|---|---|---|
| chat | **148 <sub>(137–161)</sub>** | 160 <sub>(149–176)</sub> |
| rag | **369 <sub>(106–426)</sub>** | 423 <sub>(378–446)</sub> |
| single | **482 <sub>(473–500)</sub>** | 497 <sub>(485–512)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
