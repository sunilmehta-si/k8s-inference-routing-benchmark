## chat-rag-mix: 1,672 requests, TTFT objective 1,000 ms

Each cell is the median of 5 runs per router, with the range in brackets; every run had its own cluster and fresh model servers.

| Metric | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 122 <sub>(116–140)</sub> | 105 <sub>(99–126)</sub> | **89 <sub>(84–95)</sub>** | 94 <sub>(81–122)</sub> |
| TTFT p95 (ms) <sub>lower is better</sub> | 717 <sub>(704–731)</sub> | **684 <sub>(679–693)</sub>** | 720 <sub>(670–954)</sub> | 699 <sub>(630–862)</sub> |
| TTFT p99 (ms) <sub>lower is better</sub> | 967 <sub>(850–1,179)</sub> | **868 <sub>(825–892)</sub>** | 1,281 <sub>(1,114–1,475)</sub> | 1,089 <sub>(982–1,322)</sub> |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,392 <sub>(2,286–2,520)</sub> | **2,334 <sub>(2,265–2,349)</sub>** | 2,597 <sub>(2,475–2,603)</sub> | 2,543 <sub>(2,355–2,836)</sub> |
| Time per output token p50 (ms) <sub>lower is better</sub> | **17** | **17** | 19 <sub>(18–20)</sub> | 19 <sub>(18–22)</sub> |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.1% <sub>(98.6%–99.5%)</sub> | **99.5% <sub>(99.4%–99.8%)</sub>** | 98.1% <sub>(95.8%–98.7%)</sub> | 98.6% <sub>(97.0%–99.1%)</sub> |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.3% <sub>(63.3%–64.6%)</sub> | 64.4% <sub>(63.3%–65.0%)</sub> | **80.0% <sub>(78.9%–82.4%)</sub>** | 79.9% <sub>(78.9%–82.3%)</sub> |
| Load balance across pods <sub>higher is better</sub> | 0.965 <sub>(0.950–0.970)</sub> | **0.974 <sub>(0.952–0.993)</sub>** | 0.604 <sub>(0.532–0.655)</sub> | 0.613 <sub>(0.511–0.697)</sub> |
| Output tokens per second <sub>higher is better</sub> | **443.5 <sub>(431.5–451.9)</sub>** | 436.6 <sub>(431.2–450.2)</sub> | 431.1 <sub>(428.1–436.2)</sub> | 437.9 <sub>(431.4–458.6)</sub> |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| chat | 369 <sub>(334–413)</sub> | 368 <sub>(358–387)</sub> | 456 <sub>(281–652)</sub> | **326 <sub>(195–661)</sub>** |
| rag | 746 <sub>(730–756)</sub> | **718 <sub>(698–724)</sub>** | 747 <sub>(656–1,004)</sub> | 756 <sub>(660–965)</sub> |
| single | 635 <sub>(587–717)</sub> | **625 <sub>(614–640)</sub>** | 817 <sub>(707–954)</sub> | 640 <sub>(626–694)</sub> |
