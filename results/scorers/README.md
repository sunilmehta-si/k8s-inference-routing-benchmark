## scorers (chat-rag-mix): 1,672 requests, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | load-aware | prefix-load-aware | router-default | prefix-queue | prefix-running | prefix-active |
|---|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 110 <sub>(101–116)</sub> | 91 <sub>(84–112)</sub> | 78 <sub>(72–87)</sub> | 84 <sub>(80–90)</sub> | 80 <sub>(74–82)</sub> | **74 <sub>(69–75)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | 685 <sub>(646–695)</sub> | 680 <sub>(661–818)</sub> | **478 <sub>(447–595)</sub>** | 612 <sub>(593–715)</sub> | 595 <sub>(578–612)</sub> | 536 <sub>(510–543)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 874 <sub>(829–905)</sub> | 1,007 <sub>(939–1,358)</sub> | 808 <sub>(680–1,034)</sub> | 902 <sub>(827–1,067)</sub> | 754 <sub>(733–771)</sub> | **692 <sub>(678–717)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,270 <sub>(2,200–2,349)</sub> | 2,540 <sub>(2,413–2,759)</sub> | 2,147 <sub>(2,063–2,417)</sub> | 2,347 <sub>(2,274–2,434)</sub> | 2,071 <sub>(2,037–2,171)</sub> | **1,989 <sub>(1,946–2,058)</sub>** |
| Time per output token p50 (ms) <sub>lower is better</sub> | 17 | 19 <sub>(18–22)</sub> | 17 <sub>(16–18)</sub> | 18 | 16 | **15 <sub>(15–16)</sub>** |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.5% <sub>(99.4%–99.7%)</sub> | 98.9% <sub>(97.3%–99.3%)</sub> | 99.5% <sub>(98.9%–99.8%)</sub> | 99.2% <sub>(98.7%–99.7%)</sub> | 99.6% <sub>(99.6%–99.9%)</sub> | **99.7% <sub>(99.6%–99.8%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.2% <sub>(63.7%–65.4%)</sub> | 80.2% <sub>(78.4%–81.1%)</sub> | **82.9% <sub>(81.0%–83.4%)</sub>** | 80.7% <sub>(76.8%–81.2%)</sub> | 69.5% <sub>(68.1%–70.8%)</sub> | 76.4% <sub>(76.0%–77.7%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.945 <sub>(0.937–0.972)</sub> | 0.609 <sub>(0.525–0.633)</sub> | 0.683 <sub>(0.604–0.780)</sub> | 0.661 <sub>(0.622–0.766)</sub> | **0.978 <sub>(0.946–0.986)</sub>** | 0.950 <sub>(0.935–0.981)</sub> |
| Output tokens per second <sub>higher is better</sub> | 432.1 <sub>(421.0–440.1)</sub> | 439.2 <sub>(428.7–442.1)</sub> | 433.5 <sub>(427.2–462.5)</sub> | **439.9 <sub>(428.6–448.7)</sub>** | 435.6 <sub>(424.2–452.0)</sub> | 435.7 <sub>(427.9–446.6)</sub> |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | load-aware | prefix-load-aware | router-default | prefix-queue | prefix-running | prefix-active |
|---|---|---|---|---|---|---|
| chat | 358 <sub>(314–394)</sub> | 321 <sub>(176–635)</sub> | **158 <sub>(139–191)</sub>** | 202 <sub>(161–335)</sub> | 296 <sub>(276–316)</sub> | 239 <sub>(208–252)</sub> |
| rag | 715 <sub>(666–733)</sub> | 724 <sub>(695–896)</sub> | **507 <sub>(428–678)</sub>** | 634 <sub>(607–782)</sub> | 631 <sub>(608–643)</sub> | 561 <sub>(535–572)</sub> |
| single | 618 <sub>(575–639)</sub> | 642 <sub>(608–711)</sub> | **488 <sub>(467–500)</sub>** | 643 <sub>(611–680)</sub> | 536 <sub>(515–560)</sub> | 517 <sub>(502–536)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | load-aware vs prefix-queue | load-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| TTFT p50 | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p50 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p50 | prefix-load-aware vs prefix-queue | prefix-load-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| TTFT p50 | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p50 | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p95 | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p95 | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | router-default vs prefix-running | router-default 8, prefix-running 0 of 8 | 0 | router-default |
| TTFT p95 | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | prefix-running vs prefix-active | prefix-running 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p99 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| TTFT p99 | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p99 | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-queue vs prefix-running | prefix-queue 0, prefix-running 8 of 8 | 0 | prefix-running |
| TTFT p99 | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | prefix-running vs prefix-active | prefix-running 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| Goodput | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | load-aware vs prefix-load-aware | load-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | load-aware vs prefix-queue | load-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| Prefix-cache hit rate | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| Prefix-cache hit rate | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-load-aware vs prefix-running | prefix-load-aware 8, prefix-running 0 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | prefix-load-aware vs prefix-active | prefix-load-aware 8, prefix-active 0 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | router-default vs prefix-running | router-default 8, prefix-running 0 of 8 | 0 | router-default |
| Prefix-cache hit rate | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| Prefix-cache hit rate | prefix-queue vs prefix-running | prefix-queue 8, prefix-running 0 of 8 | 0 | prefix-queue |
| Prefix-cache hit rate | prefix-queue vs prefix-active | prefix-queue 8, prefix-active 0 of 8 | 0 | prefix-queue |
| Prefix-cache hit rate | prefix-running vs prefix-active | prefix-running 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs router-default | load-aware 8, router-default 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-queue | load-aware 8, prefix-queue 0 of 8 | 0 | load-aware |
| Load balance | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| Load balance | prefix-load-aware vs prefix-queue | prefix-load-aware 0, prefix-queue 8 of 8 | 0 | prefix-queue |
| Load balance | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| Load balance | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | router-default vs prefix-running | router-default 0, prefix-running 8 of 8 | 0 | prefix-running |
| Load balance | router-default vs prefix-active | router-default 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | prefix-queue vs prefix-running | prefix-queue 0, prefix-running 8 of 8 | 0 | prefix-running |
| Load balance | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| Load balance | prefix-running vs prefix-active | prefix-running 8, prefix-active 0 of 8 | 0 | prefix-running |
| Chat TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| Chat TTFT p95 | router-default vs prefix-running | router-default 8, prefix-running 0 of 8 | 0 | router-default |
| Chat TTFT p95 | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| Chat TTFT p95 | prefix-running vs prefix-active | prefix-running 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| RAG TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| RAG TTFT p95 | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| RAG TTFT p95 | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | prefix-running vs prefix-active | prefix-running 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs router-default | load-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | load-aware vs prefix-running | load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| One-off TTFT p95 | load-aware vs prefix-active | load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | prefix-load-aware vs router-default | prefix-load-aware 0, router-default 8 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-load-aware vs prefix-running | prefix-load-aware 0, prefix-running 8 of 8 | 0 | prefix-running |
| One-off TTFT p95 | prefix-load-aware vs prefix-active | prefix-load-aware 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | router-default vs prefix-queue | router-default 8, prefix-queue 0 of 8 | 0 | router-default |
| One-off TTFT p95 | router-default vs prefix-running | router-default 8, prefix-running 0 of 8 | 0 | router-default |
| One-off TTFT p95 | router-default vs prefix-active | router-default 8, prefix-active 0 of 8 | 0 | router-default |
| One-off TTFT p95 | prefix-queue vs prefix-running | prefix-queue 0, prefix-running 8 of 8 | 0 | prefix-running |
| One-off TTFT p95 | prefix-queue vs prefix-active | prefix-queue 0, prefix-active 8 of 8 | 0 | prefix-active |
