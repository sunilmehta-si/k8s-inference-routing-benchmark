## speedup-3 (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 298 <sub>(230–335)</sub> | **83 <sub>(80–88)</sub>** | 93 <sub>(81–103)</sub> | 85 <sub>(82–89)</sub> | 95 <sub>(88–101)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 1,394 <sub>(1,034–2,065)</sub> | 581 <sub>(576–626)</sub> | 566 <sub>(547–594)</sub> | 559 <sub>(544–580)</sub> | **538 <sub>(522–603)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 1,916 <sub>(1,799–3,783)</sub> | 816 <sub>(766–849)</sub> | 742 <sub>(716–783)</sub> | 836 <sub>(797–933)</sub> | **718 <sub>(699–852)</sub>** |
| End-to-end p95 (ms) <sub>lower is better</sub> | 3,190 <sub>(2,961–3,619)</sub> | **2,335 <sub>(2,253–2,407)</sub>** | 2,393 <sub>(2,306–2,447)</sub> | 2,411 <sub>(2,362–2,459)</sub> | 2,410 <sub>(2,350–2,663)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 22 <sub>(21–22)</sub> | **18 <sub>(18–19)</sub>** | **18 <sub>(18–19)</sub>** | 19 <sub>(18–19)</sub> | 19 |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 90.0% <sub>(86.0%–94.3%)</sub> | 99.6% <sub>(99.2%–99.8%)</sub> | **100.0% <sub>(99.9%–100.0%)</sub>** | 99.4% <sub>(99.3%–99.7%)</sub> | **100.0% <sub>(99.6%–100.0%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.1% <sub>(63.6%–65.4%)</sub> | 80.5% <sub>(79.2%–81.0%)</sub> | 81.0% <sub>(80.4%–81.3%)</sub> | **83.1% <sub>(82.8%–83.4%)</sub>** | 83.0% <sub>(82.6%–83.2%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.946 <sub>(0.931–0.981)</sub> | **0.964 <sub>(0.935–0.991)</sub>** | 0.962 <sub>(0.933–0.991)</sub> | 0.898 <sub>(0.850–0.946)</sub> | 0.873 <sub>(0.777–0.925)</sub> |
| Output tokens per second <sub>higher is better</sub> | 654.8 <sub>(635.1–663.7)</sub> | 640.5 <sub>(626.6–666.2)</sub> | **657.0 <sub>(643.6–669.6)</sub>** | 642.8 <sub>(635.3–663.3)</sub> | 653.1 <sub>(624.4–686.2)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| chat | 983 <sub>(728–1,764)</sub> | 223 <sub>(199–250)</sub> | 242 <sub>(215–264)</sub> | **170 <sub>(160–193)</sub>** | 181 <sub>(167–445)</sub> |
| rag | 1,447 <sub>(1,086–2,040)</sub> | 602 <sub>(577–631)</sub> | 551 <sub>(524–596)</sub> | 588 <sub>(533–607)</sub> | **521 <sub>(479–626)</sub>** |
| single | 1,366 <sub>(1,018–2,268)</sub> | 597 <sub>(590–645)</sub> | 617 <sub>(592–660)</sub> | **588 <sub>(564–605)</sub>** | 591 <sub>(578–614)</sub> |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p50 | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| TTFT p50 | prefix-active-p2 vs precise-active-p2 | prefix-active-p2 8, precise-active-p2 0 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Goodput | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Goodput | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | prefix-active vs precise-active-p2 | prefix-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | precise-active vs precise-active-p2 | precise-active 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Load balance | round-robin vs prefix-active-p2 | round-robin 8, prefix-active-p2 0 of 8 | 0 | round-robin |
| Load balance | round-robin vs precise-active-p2 | round-robin 8, precise-active-p2 0 of 8 | 0 | round-robin |
| Load balance | prefix-active vs prefix-active-p2 | prefix-active 8, prefix-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | prefix-active vs precise-active-p2 | prefix-active 8, precise-active-p2 0 of 8 | 0 | prefix-active |
| Load balance | precise-active vs precise-active-p2 | precise-active 8, precise-active-p2 0 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | prefix-active vs prefix-active-p2 | prefix-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | precise-active vs prefix-active-p2 | precise-active 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | prefix-active vs precise-active | prefix-active 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
