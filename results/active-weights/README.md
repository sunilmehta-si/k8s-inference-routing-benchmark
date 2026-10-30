## active-weights (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | prefix-active | prefix-active-p2 | prefix-active-a2 |
|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | **71 <sub>(68–77)</sub>** | 75 <sub>(73–77)</sub> | 80 <sub>(74–84)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 523 <sub>(503–538)</sub> | **461 <sub>(454–472)</sub>** | 587 <sub>(568–604)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 704 <sub>(665–718)</sub> | **657 <sub>(626–685)</sub>** | 724 <sub>(709–767)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | **2,008 <sub>(1,942–2,065)</sub>** | 2,072 <sub>(2,024–2,097)</sub> | 2,124 <sub>(1,983–2,156)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | **15 <sub>(15–16)</sub>** | 16 | 16 <sub>(15–16)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | **99.7% <sub>(99.6%–99.9%)</sub>** | 99.6% <sub>(99.5%–99.8%)</sub> | 99.6% <sub>(99.6%–99.9%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 76.7% <sub>(76.2%–78.2%)</sub> | **83.4% <sub>(82.8%–83.5%)</sub>** | 69.4% <sub>(68.5%–71.2%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.948 <sub>(0.931–0.970)</sub> | 0.846 <sub>(0.732–0.921)</sub> | **0.971 <sub>(0.950–0.984)</sub>** |
| Output tokens per second <sub>higher is better</sub> | 434.1 <sub>(421.4–439.1)</sub> | **439.6 <sub>(432.1–448.1)</sub>** | 438.0 <sub>(427.4–455.3)</sub> |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | prefix-active | prefix-active-p2 | prefix-active-a2 |
|---|---|---|---|
| chat | 239 <sub>(218–256)</sub> | **154 <sub>(142–178)</sub>** | 288 <sub>(267–312)</sub> |
| rag | 551 <sub>(531–573)</sub> | **425 <sub>(345–440)</sub>** | 618 <sub>(590–639)</sub> |
| single | 506 <sub>(494–529)</sub> | **491 <sub>(478–508)</sub>** | 534 <sub>(512–546)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
| Load balance | prefix-active vs prefix-active-p2 | prefix-active 8, prefix-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 0, prefix-active-a2 8 of 8 | 0 | prefix-active-a2 |
| Chat TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| Chat TTFT p95 | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | prefix-active vs prefix-active-a2 | prefix-active 8, prefix-active-a2 0 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-active-p2 vs prefix-active-a2 | prefix-active-p2 8, prefix-active-a2 0 of 8 | 0 | prefix-active-p2 |
