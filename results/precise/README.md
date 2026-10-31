## precise (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | prefix-aware | precise-aware | prefix-active | precise-active | prefix-queue | precise-queue |
|---|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 93 <sub>(86–212)</sub> | 91 <sub>(81–105)</sub> | **71 <sub>(67–74)</sub>** | 84 <sub>(78–86)</sub> | 83 <sub>(76–95)</sub> | 88 <sub>(80–100)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 780 <sub>(639–1,098)</sub> | 601 <sub>(569–874)</sub> | 524 <sub>(516–539)</sub> | **497 <sub>(486–522)</sub>** | 610 <sub>(576–725)</sub> | 575 <sub>(525–610)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 1,303 <sub>(1,028–1,650)</sub> | 876 <sub>(764–1,365)</sub> | 693 <sub>(665–721)</sub> | **634 <sub>(625–643)</sub>** | 919 <sub>(821–990)</sub> | 769 <sub>(721–814)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,597 <sub>(2,384–3,098)</sub> | 2,390 <sub>(2,187–2,857)</sub> | **1,990 <sub>(1,948–2,061)</sub>** | 2,016 <sub>(1,968–2,063)</sub> | 2,344 <sub>(2,238–2,567)</sub> | 2,262 <sub>(2,109–2,443)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 19 <sub>(18–23)</sub> | 18 <sub>(17–20)</sub> | **15** | **15 <sub>(15–16)</sub>** | 18 <sub>(17–19)</sub> | 17 <sub>(17–19)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 97.8% <sub>(93.5%–98.9%)</sub> | 99.5% <sub>(96.5%–99.8%)</sub> | 99.6% <sub>(99.6%–99.9%)</sub> | **100.0%** | 99.6% <sub>(99.2%–99.7%)</sub> | 99.9% <sub>(99.6%–100.0%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 79.6% <sub>(74.4%–81.0%)</sub> | **82.6% <sub>(81.2%–83.7%)</sub>** | 76.7% <sub>(76.1%–77.4%)</sub> | 79.1% <sub>(78.6%–79.5%)</sub> | 80.1% <sub>(75.4%–81.1%)</sub> | 82.5% <sub>(81.2%–83.7%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.574 <sub>(0.511–0.661)</sub> | 0.599 <sub>(0.554–0.698)</sub> | 0.950 <sub>(0.933–0.977)</sub> | **0.964 <sub>(0.927–0.988)</sub>** | 0.663 <sub>(0.599–0.768)</sub> | 0.683 <sub>(0.634–0.761)</sub> |
| Output tokens per second <sub>higher is better</sub> | 434.4 <sub>(427.0–452.3)</sub> | 434.0 <sub>(426.4–442.5)</sub> | 437.5 <sub>(427.6–444.2)</sub> | **441.7 <sub>(430.2–450.2)</sub>** | 437.6 <sub>(426.0–445.8)</sub> | 439.2 <sub>(419.5–447.0)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | prefix-aware | precise-aware | prefix-active | precise-active | prefix-queue | precise-queue |
|---|---|---|---|---|---|---|
| chat | 506 <sub>(180–937)</sub> | 398 <sub>(202–684)</sub> | 223 <sub>(203–238)</sub> | 246 <sub>(206–264)</sub> | 194 <sub>(158–302)</sub> | **186 <sub>(153–351)</sub>** |
| rag | 806 <sub>(676–1,114)</sub> | 594 <sub>(508–813)</sub> | 552 <sub>(535–564)</sub> | **512 <sub>(488–534)</sub>** | 635 <sub>(577–744)</sub> | 514 <sub>(382–597)</sub> |
| single | 773 <sub>(623–932)</sub> | 647 <sub>(551–1,053)</sub> | **511 <sub>(493–526)</sub>** | 514 <sub>(492–527)</sub> | 621 <sub>(592–675)</sub> | 660 <sub>(604–726)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p50 | prefix-aware vs prefix-queue | prefix-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| TTFT p50 | precise-aware vs prefix-active | precise-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs precise-active | prefix-active 8, precise-active 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active vs precise-queue | prefix-active 8, precise-queue 0 of 8 | 0 | prefix-active |
| TTFT p50 | precise-active vs precise-queue | precise-active 8, precise-queue 0 of 8 | 0 | precise-active |
| TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | prefix-aware vs precise-queue | prefix-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| TTFT p95 | precise-aware vs prefix-active | precise-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| TTFT p95 | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| TTFT p95 | precise-active vs precise-queue | precise-active 8, precise-queue 0 of 8 | 0 | precise-active |
| TTFT p99 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-aware vs prefix-queue | prefix-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| TTFT p99 | prefix-aware vs precise-queue | prefix-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| TTFT p99 | precise-aware vs prefix-active | precise-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | precise-aware vs precise-queue | precise-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-active vs precise-queue | prefix-active 8, precise-queue 0 of 8 | 0 | prefix-active |
| TTFT p99 | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| TTFT p99 | precise-active vs precise-queue | precise-active 8, precise-queue 0 of 8 | 0 | precise-active |
| TTFT p99 | prefix-queue vs precise-queue | prefix-queue 0, precise-queue 8 of 8 | 0 | precise-queue |
| Goodput | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | prefix-aware vs prefix-queue | prefix-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| Goodput | prefix-aware vs precise-queue | prefix-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| Goodput | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | precise-aware vs precise-queue | precise-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| Goodput | prefix-queue vs precise-queue | prefix-queue 0, precise-queue 8 of 8 | 0 | precise-queue |
| Prefix-cache hit rate | prefix-aware vs precise-aware | prefix-aware 0, precise-aware 8 of 8 | 0 | precise-aware |
| Prefix-cache hit rate | prefix-aware vs precise-queue | prefix-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| Prefix-cache hit rate | precise-aware vs prefix-active | precise-aware 8, prefix-active 0 of 8 | 0 | precise-aware |
| Prefix-cache hit rate | precise-aware vs precise-active | precise-aware 8, precise-active 0 of 8 | 0 | precise-aware |
| Prefix-cache hit rate | precise-aware vs prefix-queue | precise-aware 8, prefix-queue 0 of 8 | 0 | precise-aware |
| Prefix-cache hit rate | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | prefix-active vs precise-queue | prefix-active 0, precise-queue 8 of 8 | 0 | precise-queue |
| Prefix-cache hit rate | precise-active vs precise-queue | precise-active 0, precise-queue 8 of 8 | 0 | precise-queue |
| Prefix-cache hit rate | prefix-queue vs precise-queue | prefix-queue 0, precise-queue 8 of 8 | 0 | precise-queue |
| Load balance | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| Load balance | precise-aware vs prefix-active | precise-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| Load balance | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active vs precise-queue | prefix-active 8, precise-queue 0 of 8 | 0 | prefix-active |
| Load balance | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| Load balance | precise-active vs precise-queue | precise-active 8, precise-queue 0 of 8 | 0 | precise-active |
| Chat TTFT p95 | precise-aware vs prefix-queue | precise-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| RAG TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-aware vs precise-queue | prefix-aware 0, precise-queue 8 of 8 | 0 | precise-queue |
| RAG TTFT p95 | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| RAG TTFT p95 | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| RAG TTFT p95 | prefix-queue vs precise-queue | prefix-queue 0, precise-queue 8 of 8 | 0 | precise-queue |
| One-off TTFT p95 | prefix-aware vs prefix-active | prefix-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-aware vs precise-active | prefix-aware 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | precise-aware vs prefix-active | precise-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | precise-aware vs precise-active | precise-aware 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | prefix-active vs prefix-queue | prefix-active 8, prefix-queue 0 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-active vs precise-queue | prefix-active 8, precise-queue 0 of 8 | 0 | prefix-active |
| One-off TTFT p95 | precise-active vs prefix-queue | precise-active 8, prefix-queue 0 of 8 | 0 | precise-active |
| One-off TTFT p95 | precise-active vs precise-queue | precise-active 8, precise-queue 0 of 8 | 0 | precise-active |
