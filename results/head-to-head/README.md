## head-to-head (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-aware | router-default | prefix-active-p2 |
|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 115 <sub>(106–129)</sub> | 94 <sub>(80–120)</sub> | 77 <sub>(75–85)</sub> | **75 <sub>(74–76)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | 706 <sub>(688–726)</sub> | 858 <sub>(704–944)</sub> | 481 <sub>(452–518)</sub> | **462 <sub>(439–647)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 958 <sub>(844–1,015)</sub> | 1,348 <sub>(1,173–1,532)</sub> | 803 <sub>(717–852)</sub> | **660 <sub>(650–3,315)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,373 <sub>(2,234–2,513)</sub> | 2,719 <sub>(2,484–2,906)</sub> | 2,194 <sub>(2,007–2,267)</sub> | **2,060 <sub>(2,026–2,269)</sub>** |
| Time per output token p50 (ms) <sub>lower is better</sub> | 17 | 20 <sub>(18–22)</sub> | 17 <sub>(16–17)</sub> | **16** |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.1% <sub>(98.9%–99.5%)</sub> | 97.1% <sub>(95.8%–98.4%)</sub> | 99.5% <sub>(99.4%–99.8%)</sub> | **99.7% <sub>(96.7%–99.9%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.3% <sub>(63.1%–64.8%)</sub> | 79.0% <sub>(77.5%–81.0%)</sub> | 82.7% <sub>(82.0%–83.8%)</sub> | **83.3% <sub>(82.6%–83.5%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | **0.947 <sub>(0.901–0.981)</sub>** | 0.572 <sub>(0.514–0.647)</sub> | 0.719 <sub>(0.676–0.818)</sub> | 0.833 <sub>(0.793–0.917)</sub> |
| Output tokens per second <sub>higher is better</sub> | 438.6 <sub>(422.5–451.2)</sub> | 438.5 <sub>(421.6–476.5)</sub> | 438.6 <sub>(429.9–452.3)</sub> | **446.0 <sub>(436.0–457.7)</sub>** |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-aware | router-default | prefix-active-p2 |
|---|---|---|---|---|
| chat | 361 <sub>(345–383)</sub> | 553 <sub>(352–858)</sub> | **152 <sub>(140–167)</sub>** | 158 <sub>(140–164)</sub> |
| rag | 740 <sub>(718–755)</sub> | 899 <sub>(733–998)</sub> | 509 <sub>(423–597)</sub> | **411 <sub>(393–675)</sub>** |
| single | 647 <sub>(596–663)</sub> | 784 <sub>(646–976)</sub> | 489 <sub>(474–539)</sub> | **488 <sub>(478–891)</sub>** |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| TTFT p99 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Goodput | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Goodput | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs router-default | round-robin 8, router-default 0 of 8 | 0 | round-robin |
| Load balance | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Load balance | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| One-off TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
