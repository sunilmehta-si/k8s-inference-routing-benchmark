## precise-control (one-off-heavy): 1,472 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-active | precise-active |
|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 366 <sub>(356–371)</sub> | **345 <sub>(339–348)</sub>** | 347 <sub>(336–352)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 654 <sub>(618–685)</sub> | 545 <sub>(536–557)</sub> | **543 <sub>(531–548)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 917 <sub>(767–1,279)</sub> | 650 <sub>(618–742)</sub> | **606 <sub>(596–617)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,433 <sub>(2,314–2,566)</sub> | 2,237 <sub>(2,115–2,290)</sub> | **2,184 <sub>(2,042–2,219)</sub>** |
| Time per output token p50 (ms) <sub>lower is better</sub> | 17 | **16 <sub>(15–16)</sub>** | **16 <sub>(15–16)</sub>** |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.3% <sub>(98.6%–99.7%)</sub> | 99.5% <sub>(99.4%–99.9%)</sub> | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 3.4% <sub>(3.3%–3.5%)</sub> | **4.0% <sub>(3.9%–4.1%)</sub>** | **4.0% <sub>(4.0%–4.1%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | 0.946 <sub>(0.918–0.979)</sub> | 0.970 <sub>(0.941–0.984)</sub> | **0.976 <sub>(0.956–0.987)</sub>** |
| Output tokens per second <sub>higher is better</sub> | **386.4 <sub>(374.5–407.9)</sub>** | 386.1 <sub>(363.5–398.3)</sub> | 383.7 <sub>(363.3–395.2)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-active | precise-active |
|---|---|---|---|
| chat | 354 <sub>(320–431)</sub> | 291 <sub>(258–315)</sub> | **278 <sub>(264–294)</sub>** |
| single | 657 <sub>(623–694)</sub> | 548 <sub>(538–561)</sub> | **545 <sub>(532–549)</sub>** |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
