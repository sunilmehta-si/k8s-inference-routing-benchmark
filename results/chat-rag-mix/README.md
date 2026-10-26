## chat-rag-mix: 1,672 requests, TTFT objective 1,000 ms

| Metric | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| TTFT p50 (ms) <sub>lower is better</sub> | 132 | 123 | 89 | **81** |
| TTFT p95 (ms) <sub>lower is better</sub> | 717 | 684 | 718 | **630** |
| TTFT p99 (ms) <sub>lower is better</sub> | 967 | **857** | 1,315 | 1,048 |
| End-to-end p95 (ms) <sub>lower is better</sub> | 2,388 | **2,334** | 2,600 | 2,355 |
| Time per output token p50 (ms) <sub>lower is better</sub> | **17** | **17** | 18 | 18 |
| Goodput (TTFT within objective) <sub>higher is better</sub> | 99.1% | **99.8%** | 98.1% | 98.9% |
| Prefix-cache hit rate (from the pods) <sub>higher is better</sub> | 64.3% | 64.4% | 80.0% | **82.3%** |
| Load balance across pods <sub>higher is better</sub> | **0.970** | 0.952 | 0.655 | 0.697 |
| Output tokens per second <sub>higher is better</sub> | 443.5 | 450.2 | 430.5 | **458.6** |
| Errors <sub>lower is better</sub> | 0 | 0 | 0 | 0 |

**TTFT p95 by kind of traffic (ms)**

| Kind | round-robin | load-aware | prefix-aware | prefix-load-aware |
|---|---|---|---|---|
| chat | 334 | 387 | 281 | **195** |
| rag | 748 | 718 | 747 | **660** |
| single | **622** | 640 | 707 | 626 |
