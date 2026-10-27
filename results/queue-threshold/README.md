## queue-threshold (chat-rag-mix): 1,672 requests, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | load-aware | prefix-load-aware | prefix-load-q8 |
|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 111 <sub>(104–113)</sub> | **94 <sub>(88–105)</sub>** | **94 <sub>(86–130)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | **679 <sub>(675–694)</sub>** | 755 <sub>(646–886)</sub> | 750 <sub>(669–874)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | **867 <sub>(827–891)</sub>** | 1,232 <sub>(979–1,430)</sub> | 1,132 <sub>(1,053–1,428)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | **2,301 <sub>(2,257–2,401)</sub>** | 2,680 <sub>(2,383–2,886)</sub> | 2,626 <sub>(2,519–2,891)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | **17 <sub>(16–17)</sub>** | 20 <sub>(18–21)</sub> | 20 <sub>(18–22)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | **99.5% <sub>(99.3%–99.8%)</sub>** | 98.1% <sub>(96.8%–99.3%)</sub> | 98.4% <sub>(97.1%–98.8%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.2% <sub>(63.7%–65.0%)</sub> | **80.0% <sub>(77.2%–81.5%)</sub>** | 79.6% <sub>(78.2%–81.9%)</sub> |
| Load balance across pods <sub>higher is better</sub> | **0.948 <sub>(0.907–0.977)</sub>** | 0.554 <sub>(0.526–0.656)</sub> | 0.557 <sub>(0.524–0.615)</sub> |
| Output tokens per second <sub>higher is better</sub> | 441.5 <sub>(425.5–446.7)</sub> | **445.9 <sub>(431.7–461.4)</sub>** | 436.4 <sub>(430.4–445.7)</sub> |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | load-aware | prefix-load-aware | prefix-load-q8 |
|---|---|---|---|
| chat | **351 <sub>(319–388)</sub>** | 557 <sub>(185–706)</sub> | 500 <sub>(398–633)</sub> |
| rag | **707 <sub>(696–723)</sub>** | 816 <sub>(700–952)</sub> | 782 <sub>(684–948)</sub> |
| single | **601 <sub>(583–640)</sub>** | 683 <sub>(631–726)</sub> | 681 <sub>(613–725)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | load-aware vs prefix-load-aware | load-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| TTFT p99 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-load-q8 | load-aware 8, prefix-load-q8 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-load-q8 | load-aware 8, prefix-load-q8 0 of 8 | 0 | load-aware |
| Prefix-cache hit rate | load-aware vs prefix-load-aware | load-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | load-aware vs prefix-load-q8 | load-aware 0, prefix-load-q8 8 of 8 | 0 | prefix-load-q8 |
| Load balance | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-load-q8 | load-aware 8, prefix-load-q8 0 of 8 | 0 | load-aware |
| Chat TTFT p95 | load-aware vs prefix-load-q8 | load-aware 8, prefix-load-q8 0 of 8 | 0 | load-aware |
| RAG TTFT p95 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs prefix-load-q8 | load-aware 8, prefix-load-q8 0 of 8 | 0 | load-aware |
