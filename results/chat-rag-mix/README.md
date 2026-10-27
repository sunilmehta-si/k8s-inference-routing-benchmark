## chat-rag-mix: 1,672 requests, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 121 <sub>(116–140)</sub> | 109 <sub>(99–126)</sub> | **88 <sub>(84–95)</sub>** | 92 <sub>(81–122)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 717 <sub>(673–731)</sub> | **683 <sub>(642–693)</sub>** | 752 <sub>(614–954)</sub> | 718 <sub>(630–862)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 952 <sub>(850–1,179)</sub> | **863 <sub>(825–897)</sub>** | 1,255 <sub>(991–1,475)</sub> | 1,102 <sub>(982–1,601)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,385 <sub>(2,260–2,520)</sub> | **2,333 <sub>(2,208–2,388)</sub>** | 2,583 <sub>(2,395–2,646)</sub> | 2,531 <sub>(2,352–2,836)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | **17** | **17 <sub>(16–17)</sub>** | 19 <sub>(18–20)</sub> | 19 <sub>(18–22)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.2% <sub>(98.6%–99.5%)</sub> | **99.5% <sub>(99.3%–99.8%)</sub>** | 98.0% <sub>(95.8%–99.0%)</sub> | 98.6% <sub>(97.0%–99.1%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 63.9% <sub>(63.3%–64.6%)</sub> | 64.3% <sub>(63.3%–65.0%)</sub> | **79.9% <sub>(78.9%–82.4%)</sub>** | 79.8% <sub>(78.9%–82.3%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.961 <sub>(0.931–0.970)</sub> | **0.971 <sub>(0.917–0.993)</sub>** | 0.599 <sub>(0.532–0.682)</sub> | 0.564 <sub>(0.498–0.697)</sub> |
| Output tokens per second <sub>higher is better</sub> | **440.6 <sub>(431.3–451.9)</sub>** | 434.3 <sub>(422.3–450.2)</sub> | 430.8 <sub>(421.6–447.3)</sub> | 436.3 <sub>(422.4–458.6)</sub> |
| Errors <sub>lower is better</sub> | 0.000 | 0.000 | 0.000 | 0.000 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| chat | 383 <sub>(334–449)</sub> | **358 <sub>(325–387)</sub>** | 486 <sub>(204–694)</sub> | 378 <sub>(195–661)</sub> |
| rag | 745 <sub>(715–756)</sub> | **712 <sub>(673–724)</sub>** | 770 <sub>(646–1,004)</sub> | 762 <sub>(660–965)</sub> |
| single | 629 <sub>(587–717)</sub> | **620 <sub>(578–640)</sub>** | 814 <sub>(672–954)</sub> | 660 <sub>(615–719)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| TTFT p50 | round-robin vs prefix-load-aware | round-robin 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| TTFT p50 | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| TTFT p95 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| TTFT p99 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| TTFT p99 | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Goodput | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Goodput | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Goodput | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| Prefix-cache hit rate | round-robin vs prefix-aware | round-robin 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | round-robin vs prefix-load-aware | round-robin 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Prefix-cache hit rate | load-aware vs prefix-aware | load-aware 0, prefix-aware 8 of 8 | 0 | prefix-aware |
| Prefix-cache hit rate | load-aware vs prefix-load-aware | load-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
| Load balance | round-robin vs prefix-aware | round-robin 8, prefix-aware 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs prefix-load-aware | round-robin 8, prefix-load-aware 0 of 8 | 0 | round-robin |
| Load balance | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| Load balance | load-aware vs prefix-load-aware | load-aware 8, prefix-load-aware 0 of 8 | 0 | load-aware |
| RAG TTFT p95 | round-robin vs load-aware | round-robin 0, load-aware 8 of 8 | 0 | load-aware |
| One-off TTFT p95 | load-aware vs prefix-aware | load-aware 8, prefix-aware 0 of 8 | 0 | load-aware |
| One-off TTFT p95 | prefix-aware vs prefix-load-aware | prefix-aware 0, prefix-load-aware 8 of 8 | 0 | prefix-load-aware |
