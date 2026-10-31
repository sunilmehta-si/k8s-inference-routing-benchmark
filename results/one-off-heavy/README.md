## one-off-heavy: 1,472 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | load-aware | prefix-aware | router-default | prefix-active | prefix-active-p2 |
|---|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 366 <sub>(355–368)</sub> | 364 <sub>(355–371)</sub> | 366 <sub>(361–377)</sub> | 345 <sub>(338–356)</sub> | 342 <sub>(336–349)</sub> | **340 <sub>(335–349)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | 646 <sub>(636–654)</sub> | 614 <sub>(609–640)</sub> | 624 <sub>(607–652)</sub> | 565 <sub>(540–585)</sub> | **542 <sub>(536–554)</sub>** | **542 <sub>(526–552)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 894 <sub>(784–1,105)</sub> | 766 <sub>(718–836)</sub> | 779 <sub>(710–942)</sub> | 695 <sub>(645–754)</sub> | 636 <sub>(604–657)</sub> | **610 <sub>(597–666)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,444 <sub>(2,335–2,601)</sub> | 2,378 <sub>(2,307–2,497)</sub> | 2,445 <sub>(2,357–2,592)</sub> | 2,238 <sub>(2,121–2,321)</sub> | **2,169 <sub>(2,134–2,280)</sub>** | 2,187 <sub>(2,128–2,285)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 17 <sub>(16–17)</sub> | 17 <sub>(16–17)</sub> | 17 | **16** | **16 <sub>(15–16)</sub>** | **16 <sub>(15–16)</sub>** |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.3% <sub>(98.7%–99.7%)</sub> | 99.6% <sub>(99.2%–99.8%)</sub> | 99.6% <sub>(99.2%–99.9%)</sub> | **99.7% <sub>(99.4%–99.7%)</sub>** | **99.7% <sub>(99.5%–100.0%)</sub>** | **99.7% <sub>(99.5%–99.9%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 3.4% <sub>(3.3%–3.5%)</sub> | 3.4% <sub>(3.3%–3.6%)</sub> | **4.2% <sub>(4.1%–4.2%)</sub>** | **4.2% <sub>(4.2%–4.3%)</sub>** | 4.0% <sub>(3.8%–4.1%)</sub> | **4.2% <sub>(4.2%–4.3%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | 0.931 <sub>(0.885–0.976)</sub> | 0.957 <sub>(0.909–0.984)</sub> | 0.849 <sub>(0.812–0.878)</sub> | 0.922 <sub>(0.893–0.946)</sub> | **0.964 <sub>(0.939–0.992)</sub>** | 0.919 <sub>(0.882–0.963)</sub> |
| Output tokens per second <sub>higher is better</sub> | 385.9 <sub>(367.7–405.7)</sub> | 385.9 <sub>(379.0–400.6)</sub> | **391.4 <sub>(380.1–401.0)</sub>** | 382.8 <sub>(373.4–398.0)</sub> | 379.1 <sub>(372.0–395.7)</sub> | 383.4 <sub>(370.9–399.9)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | router-default | prefix-active | prefix-active-p2 |
|---|---|---|---|---|---|---|
| chat | 367 <sub>(341–502)</sub> | 343 <sub>(295–398)</sub> | 322 <sub>(286–415)</sub> | 278 <sub>(271–302)</sub> | 280 <sub>(273–286)</sub> | **275 <sub>(265–285)</sub>** |
| single | 649 <sub>(641–656)</sub> | 617 <sub>(613–646)</sub> | 626 <sub>(610–658)</sub> | 570 <sub>(543–587)</sub> | 545 <sub>(538–558)</sub> | **544 <sub>(527–555)</sub>** |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| TTFT p99 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p99 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-aware vs prefix-active | prefix-aware 8, prefix-active 0 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Load balance | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Load balance | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Load balance | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | router-default vs prefix-active | router-default 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| One-off TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
