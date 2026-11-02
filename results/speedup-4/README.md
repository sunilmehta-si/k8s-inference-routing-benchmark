## speedup-4 (chat-rag-mix): 1,672 requests on 4 simulated vLLM pods, TTFT objective 1,000 ms

Each cell is the median of 8 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 1,096 <sub>(858–1,943)</sub> | 134 <sub>(114–211)</sub> | **132 <sub>(113–151)</sub>** | 166 <sub>(135–203)</sub> | 150 <sub>(120–352)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 4,532 <sub>(2,993–5,680)</sub> | 929 <sub>(803–1,615)</sub> | 846 <sub>(716–950)</sub> | 995 <sub>(858–1,083)</sub> | **827 <sub>(716–1,368)</sub>** |
| TTFT p99 (ms) <sub>lower is better</sub> | 5,487 <sub>(3,513–8,900)</sub> | 1,389 <sub>(1,202–2,283)</sub> | **1,168 <sub>(1,002–1,507)</sub>** | 1,418 <sub>(1,231–1,585)</sub> | 1,212 <sub>(965–1,793)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 5,802 <sub>(4,434–7,010)</sub> | **3,007 <sub>(2,915–3,340)</sub>** | 3,015 <sub>(2,856–3,130)</sub> | 3,116 <sub>(3,000–3,161)</sub> | 3,074 <sub>(2,831–3,425)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | 26 | 24 <sub>(23–24)</sub> | **23 <sub>(23–24)</sub>** | 24 | 24 <sub>(23–25)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 46.8% <sub>(34.5%–56.2%)</sub> | 96.3% <sub>(81.4%–97.5%)</sub> | 97.6% <sub>(95.5%–99.0%)</sub> | 95.0% <sub>(93.7%–97.1%)</sub> | **97.7% <sub>(85.9%–99.1%)</sub>** |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.0% <sub>(63.5%–64.8%)</sub> | 81.3% <sub>(80.5%–82.0%)</sub> | 81.9% <sub>(81.1%–82.3%)</sub> | 82.0% <sub>(80.3%–82.4%)</sub> | **82.3% <sub>(80.5%–83.0%)</sub>** |
| Load balance across pods <sub>higher is better</sub> | 0.956 <sub>(0.919–0.981)</sub> | 0.960 <sub>(0.941–0.970)</sub> | **0.966 <sub>(0.915–0.981)</sub>** | 0.935 <sub>(0.895–0.979)</sub> | 0.946 <sub>(0.903–0.961)</sub> |
| Output tokens per second <sub>higher is better</sub> | 815.4 <sub>(788.8–847.7)</sub> | 856.6 <sub>(846.2–888.3)</sub> | 863.0 <sub>(856.3–884.5)</sub> | 865.2 <sub>(844.1–885.8)</sub> | **867.8 <sub>(839.7–891.0)</sub>** |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | prefix-active | precise-active | prefix-active-p2 | precise-active-p2 |
|---|---|---|---|---|---|
| chat | 4,454 <sub>(2,891–5,680)</sub> | 709 <sub>(441–1,578)</sub> | **653 <sub>(430–857)</sub>** | 948 <sub>(692–1,016)</sub> | 788 <sub>(484–1,324)</sub> |
| rag | 4,505 <sub>(2,950–5,847)</sub> | 916 <sub>(793–1,552)</sub> | **804 <sub>(694–905)</sub>** | 960 <sub>(820–1,068)</sub> | 809 <sub>(707–1,304)</sub> |
| single | 4,693 <sub>(3,267–5,856)</sub> | 1,028 <sub>(850–1,818)</sub> | 1,033 <sub>(762–1,277)</sub> | 1,115 <sub>(972–1,251)</sub> | **966 <sub>(763–1,657)</sub>** |

**Differences that held in every run both routers had**

| Metric | Routers | Better in (runs) | Ties | Held by |
|---|---|---|---|---|
| TTFT p50 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p50 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p50 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p50 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p50 | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| TTFT p99 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| TTFT p99 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| TTFT p99 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| TTFT p99 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Goodput | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Goodput | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Goodput | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Goodput | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Prefix-cache hit rate | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Prefix-cache hit rate | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Prefix-cache hit rate | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Prefix-cache hit rate | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| Chat TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| Chat TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| Chat TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| Chat TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| RAG TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| RAG TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| RAG TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
| RAG TTFT p95 | precise-active vs prefix-active-p2 | precise-active 8, prefix-active-p2 0 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active | round-robin 0, prefix-active 8 of 8 | 0 | prefix-active |
| One-off TTFT p95 | round-robin vs precise-active | round-robin 0, precise-active 8 of 8 | 0 | precise-active |
| One-off TTFT p95 | round-robin vs prefix-active-p2 | round-robin 0, prefix-active-p2 8 of 8 | 0 | prefix-active-p2 |
| One-off TTFT p95 | round-robin vs precise-active-p2 | round-robin 0, precise-active-p2 8 of 8 | 0 | precise-active-p2 |
