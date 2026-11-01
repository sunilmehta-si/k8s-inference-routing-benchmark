## precise-eight-pods (chat-rag-mix): 1,672 requests on 8 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-active | precise-active | precise-active-spec | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 118 <sub>(105–130)</sub> | **67 <sub>(65–70)</sub>** | 77 <sub>(65–79)</sub> | 80 <sub>(72–84)</sub> | 69 <sub>(64–71)</sub> | 78 <sub>(73–84)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 584 <sub>(572–595)</sub> | 475 <sub>(463–494)</sub> | 463 <sub>(450–469)</sub> | 476 <sub>(462–494)</sub> | **381 <sub>(376–389)</sub>** | 391 <sub>(386–400)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 723 <sub>(697–811)</sub> | 597 <sub>(588–607)</sub> | 562 <sub>(543–570)</sub> | 578 <sub>(555–587)</sub> | 523 <sub>(516–564)</sub> | **512 <sub>(505–521)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 1,975 <sub>(1,944–2,097)</sub> | 1,757 <sub>(1,732–1,808)</sub> | **1,725 <sub>(1,675–1,779)</sub>** | 1,782 <sub>(1,720–1,858)</sub> | 1,826 <sub>(1,774–1,875)</sub> | 1,808 <sub>(1,750–1,832)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 14 | **13** | **13** | **13 <sub>(13–14)</sub>** | 14 | 14 |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.6% <sub>(99.3%–99.9%)</sub> | 99.6% <sub>(99.6%–99.9%)</sub> | **100.0%** | **100.0%** | 99.7% <sub>(99.6%–99.9%)</sub> | **100.0%** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 62.3% <sub>(61.7%–63.0%)</sub> | 74.0% <sub>(72.7%–75.2%)</sub> | 75.9% <sub>(75.0%–76.3%)</sub> | 73.4% <sub>(72.3%–74.8%)</sub> | **84.4% <sub>(84.4%–84.6%)</sub>** | 84.1% <sub>(84.0%–84.4%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.911 <sub>(0.864–0.937)</sub> | **0.929 <sub>(0.897–0.954)</sub>** | 0.921 <sub>(0.901–0.954)</sub> | 0.850 <sub>(0.757–0.901)</sub> | 0.522 <sub>(0.472–0.666)</sub> | 0.684 <sub>(0.559–0.726)</sub> |
| Output tokens per second <sub>higher is better</sub> | 437.8 <sub>(426.3–455.0)</sub> | 434.6 <sub>(420.7–450.7)</sub> | 437.5 <sub>(422.8–449.5)</sub> | **445.6 <sub>(437.2–454.0)</sub>** | 437.8 <sub>(428.2–447.9)</sub> | 441.6 <sub>(430.3–459.1)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-active | precise-active | precise-active-spec | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|---|
| chat | 315 <sub>(295–320)</sub> | 230 <sub>(227–245)</sub> | 233 <sub>(224–260)</sub> | 252 <sub>(235–276)</sub> | **140 <sub>(131–165)</sub>** | 164 <sub>(143–200)</sub> |
| rag | 607 <sub>(585–621)</sub> | 509 <sub>(503–521)</sub> | 495 <sub>(475–510)</sub> | 510 <sub>(501–526)</sub> | **87 <sub>(83–91)</sub>** | 98 <sub>(93–109)</sub> |
| single | 516 <sub>(488–533)</sub> | 432 <sub>(426–440)</sub> | 438 <sub>(426–450)</sub> | 442 <sub>(429–448)</sub> | **417 <sub>(408–422)</sub>** | 429 <sub>(421–433)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p50 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p50 | prefix-active vs precise-active-spec | prefix-active 8, precise-active-spec 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| TTFT p50 | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | precise-active-spec vs precise-active-p2 | precise-active-spec 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| TTFT p99 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | precise-active-spec vs precise-active-p2 | precise-active-spec 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Goodput | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-active vs precise-active-spec | prefix-active 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Goodput | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Goodput | precise-active-spec vs prefix-active-p2 | precise-active-spec 8, prefix-active-p2 0 of 8 | 0 | precise-active-spec |
| Goodput | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | precise-active vs precise-active-spec | precise-active 8, precise-active-spec 0 of 8 | 0 | precise-active |
| Prefix-cache hit rate | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | precise-active-spec vs precise-active-p2 | precise-active-spec 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| Load balance | round-robin vs prefix-active-p2 | round-robin 8, prefix-active-p2 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs precise-active-p2 | round-robin 8, precise-active-p2 0 of 8 | 0 | round-robin |
| Load balance | prefix-active vs precise-active-spec | prefix-active 8, precise-active-spec 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active vs prefix-active-p2 | prefix-active 8, prefix-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | precise-active vs precise-active-spec | precise-active 8, precise-active-spec 0 of 8 | 0 | precise-active |
| Load balance | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Load balance | precise-active vs precise-active-p2 | precise-active 8, precise-active-p2 0 of 8 | 0 | precise-active |
| Load balance | precise-active-spec vs prefix-active-p2 | precise-active-spec 8, prefix-active-p2 0 of 8 | 0 | precise-active-spec |
| Load balance | precise-active-spec vs precise-active-p2 | precise-active-spec 8, precise-active-p2 0 of 8 | 0 | precise-active-spec |
| Load balance | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | precise-active-spec vs precise-active-p2 | precise-active-spec 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | precise-active-spec vs precise-active-p2 | precise-active-spec 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs precise-active-spec | round-robin 0, precise-active-spec 8 of 8 | 0 | precise-active-spec |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| One-off TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | precise-active-spec vs prefix-active-p2 | precise-active-spec 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
