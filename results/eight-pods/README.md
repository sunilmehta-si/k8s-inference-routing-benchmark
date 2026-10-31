## eight-pods (chat-rag-mix): 1,672 requests on 8 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | load-aware | prefix-aware | router-default | prefix-active | prefix-active-p2 |
|---|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 116 <sub>(104–140)</sub> | 123 <sub>(116–142)</sub> | 89 <sub>(83–98)</sub> | 78 <sub>(75–81)</sub> | **67 <sub>(63–70)</sub>** | **67 <sub>(64–70)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | 574 <sub>(557–595)</sub> | 592 <sub>(572–599)</sub> | 731 <sub>(611–874)</sub> | 423 <sub>(391–468)</sub> | 475 <sub>(457–500)</sub> | **380 <sub>(376–389)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 717 <sub>(684–758)</sub> | 719 <sub>(690–738)</sub> | 1,081 <sub>(986–1,370)</sub> | 839 <sub>(653–875)</sub> | 588 <sub>(573–618)</sub> | **517 <sub>(504–538)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 1,919 <sub>(1,894–1,983)</sub> | 2,004 <sub>(1,943–2,046)</sub> | 2,450 <sub>(2,373–2,792)</sub> | 2,128 <sub>(2,003–2,198)</sub> | **1,746 <sub>(1,700–1,782)</sub>** | 1,802 <sub>(1,727–1,850)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 14 | 14 | 18 <sub>(18–20)</sub> | 16 | **13** | 14 |
| Goodput (TTFT within objective) <sub>higher is better</sub> | **99.6% <sub>(99.6%–99.9%)</sub>** | **99.6% <sub>(99.5%–99.9%)</sub>** | 98.6% <sub>(96.8%–99.0%)</sub> | 99.5% <sub>(99.2%–99.8%)</sub> | **99.6% <sub>(99.6%–99.9%)</sub>** | **99.6% <sub>(99.6%–99.9%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 62.7% <sub>(61.2%–63.2%)</sub> | 62.4% <sub>(61.9%–62.6%)</sub> | 80.9% <sub>(78.8%–81.2%)</sub> | 82.9% <sub>(82.7%–84.6%)</sub> | 74.6% <sub>(72.0%–75.2%)</sub> | **84.4% <sub>(84.3%–84.5%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | 0.911 <sub>(0.889–0.968)</sub> | 0.901 <sub>(0.839–0.917)</sub> | 0.289 <sub>(0.270–0.332)</sub> | 0.364 <sub>(0.355–0.372)</sub> | **0.931 <sub>(0.889–0.941)</sub>** | 0.595 <sub>(0.486–0.649)</sub> |
| Output tokens per second <sub>higher is better</sub> | 433.4 <sub>(425.8–452.7)</sub> | **444.2 <sub>(426.2–454.7)</sub>** | 431.8 <sub>(425.6–449.6)</sub> | 440.3 <sub>(432.6–458.4)</sub> | 435.7 <sub>(431.7–448.9)</sub> | 438.0 <sub>(423.6–448.8)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | router-default | prefix-active | prefix-active-p2 |
|---|---|---|---|---|---|---|
| chat | 305 <sub>(284–311)</sub> | 312 <sub>(295–328)</sub> | 489 <sub>(195–794)</sub> | **144 <sub>(140–157)</sub>** | 236 <sub>(205–242)</sub> | 155 <sub>(143–168)</sub> |
| rag | 597 <sub>(588–613)</sub> | 616 <sub>(602–626)</sub> | 769 <sub>(666–948)</sub> | 525 <sub>(241–549)</sub> | 507 <sub>(498–522)</sub> | **83 <sub>(82–90)</sub>** |
| single | 506 <sub>(482–518)</sub> | 513 <sub>(488–532)</sub> | 593 <sub>(548–736)</sub> | **412 <sub>(407–422)</sub>** | 437 <sub>(431–452)</sub> | 415 <sub>(411–422)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| TTFT p50 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| TTFT p50 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | router-default vs prefix-active | router-default 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| TTFT p95 | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p99 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | router-default vs prefix-active | router-default 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Goodput | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Goodput | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Goodput | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Goodput | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-aware vs prefix-active | prefix-aware 8, prefix-active 0 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs router-default | round-robin 8, router-default 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs prefix-active-p2 | round-robin 8, prefix-active-p2 0 of 8 | 0 | round-robin |
| Load balance | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs router-default | load-aware 8, router-default 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-active-p2 | load-aware 8, prefix-active-p2 0 of 8 | 0 | load-aware |
| Load balance | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Load balance | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | router-default vs prefix-active | router-default 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Load balance | prefix-active vs prefix-active-p2 | prefix-active 8, prefix-active-p2 0 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| Chat TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| RAG TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| RAG TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | router-default vs prefix-active-p2 | router-default 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| One-off TTFT p95 | round-robin vs router-default | round-robin 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | load-aware vs prefix-active-p2 | load-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | prefix-aware vs router-default | prefix-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-aware vs prefix-active-p2 | prefix-aware 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
