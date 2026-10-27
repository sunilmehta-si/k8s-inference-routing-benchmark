## load-weight (chat-rag-mix): 1,672 requests, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | load-aware | prefix-aware | prefix-load-aware | prefix-load-2x |
|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 117 <sub>(103–131)</sub> | 113 <sub>(104–124)</sub> | 92 <sub>(86–195)</sub> | 93 <sub>(86–120)</sub> | **91 <sub>(88–103)</sub>** |
| TTFT p95 (ms) <sub>lower is better</sub> | 694 <sub>(679–717)</sub> | **685 <sub>(665–712)</sub>** | 779 <sub>(696–1,025)</sub> | 754 <sub>(670–828)</sub> | 709 <sub>(671–802)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 924 <sub>(869–1,042)</sub> | **854 <sub>(819–950)</sub>** | 1,226 <sub>(1,032–1,486)</sub> | 1,163 <sub>(952–1,350)</sub> | 1,095 <sub>(968–1,333)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,368 <sub>(2,241–2,510)</sub> | **2,326 <sub>(2,220–2,376)</sub>** | 2,679 <sub>(2,523–3,060)</sub> | 2,711 <sub>(2,452–2,956)</sub> | 2,545 <sub>(2,458–2,780)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | **17** | **17** | 20 <sub>(19–23)</sub> | 21 <sub>(19–22)</sub> | 19 <sub>(18–21)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.4% <sub>(98.6%–99.6%)</sub> | **99.5% <sub>(99.2%–99.6%)</sub>** | 97.8% <sub>(94.3%–98.7%)</sub> | 98.1% <sub>(97.3%–99.2%)</sub> | 98.5% <sub>(97.7%–99.1%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.1% <sub>(63.5%–65.0%)</sub> | 64.1% <sub>(63.4%–64.7%)</sub> | 80.0% <sub>(76.3%–80.1%)</sub> | 79.7% <sub>(78.3%–81.2%)</sub> | **80.6% <sub>(78.9%–81.2%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | **0.968 <sub>(0.931–0.993)</sub>** | 0.960 <sub>(0.929–0.993)</sub> | 0.571 <sub>(0.535–0.627)</sub> | 0.554 <sub>(0.515–0.620)</sub> | 0.567 <sub>(0.524–0.629)</sub> |
| Output tokens per second <sub>higher is better</sub> | 436.9 <sub>(426.3–446.4)</sub> | 435.4 <sub>(420.8–454.5)</sub> | **442.9 <sub>(439.3–445.1)</sub>** | 440.9 <sub>(437.6–448.9)</sub> | 438.5 <sub>(425.4–449.9)</sub> |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | prefix-load-aware | prefix-load-2x |
|---|---|---|---|---|---|
| chat | 368 <sub>(345–431)</sub> | **353 <sub>(338–416)</sub>** | 624 <sub>(364–798)</sub> | 569 <sub>(264–802)</sub> | 506 <sub>(265–599)</sub> |
| rag | 728 <sub>(710–751)</sub> | **717 <sub>(683–746)</sub>** | 797 <sub>(696–1,044)</sub> | 814 <sub>(706–895)</sub> | 750 <sub>(700–878)</sub> |
| single | 635 <sub>(610–709)</sub> | **603 <sub>(595–636)</sub>** | 829 <sub>(728–1,088)</sub> | 681 <sub>(640–722)</sub> | 666 <sub>(603–682)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-load-aware | round-robin 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| TTFT p50 | round-robin vs prefix-load-2x | round-robin 0, prefix-load-2x 8 of 8 | 0 | prefix-load-2x |
| TTFT p50 | load-aware vs prefix-load-2x | load-aware 0, prefix-load-2x 8 of 8 | 0 | prefix-load-2x |
| TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| TTFT p99 | round-robin vs prefix-load-2x | round-robin 8, prefix-load-2x 0 of 8 | 0 | round-robin |
| TTFT p99 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-load-2x | load-aware 8, prefix-load-2x 0 of 8 | 0 | load-aware |
| Goodput | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Goodput | round-robin vs prefix-load-2x | round-robin 8, prefix-load-2x 0 of 8 | 0 | round-robin |
| Goodput | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-load-2x | load-aware 8, prefix-load-2x 0 of 8 | 0 | load-aware |
| Prefix-cache hit rate | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | round-robin vs prefix-load-aware | round-robin 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | round-robin vs prefix-load-2x | round-robin 0, prefix-load-2x 8 of 8 | 0 | prefix-load-2x |
| Prefix-cache hit rate | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | load-aware vs prefix-load-aware | load-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | load-aware vs prefix-load-2x | load-aware 0, prefix-load-2x 8 of 8 | 0 | prefix-load-2x |
| Load balance | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs prefix-load-aware | round-robin 8, prefix-load-aware 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs prefix-load-2x | round-robin 8, prefix-load-2x 0 of 8 | 0 | round-robin |
| Load balance | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-load-2x | load-aware 8, prefix-load-2x 0 of 8 | 0 | load-aware |
| Chat TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| One-off TTFT p95 | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| One-off TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs prefix-load-2x | load-aware 8, prefix-load-2x 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | prefix-aware vs prefix-load-aware | prefix-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| One-off TTFT p95 | prefix-aware vs prefix-load-2x | prefix-aware 0, prefix-load-2x 8 of 8 | 0 | prefix-load-2x |
