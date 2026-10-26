# Security policy

## Reporting a vulnerability

Please report security issues privately through GitHub's
[security advisory form](https://github.com/sunilmehta-si/k8s-inference-routing-benchmark/security/advisories/new)
rather than in a public issue. You will get an answer within a week.

## What this project runs

- Every container image is pinned by digest and every downloaded binary or manifest by sha256, in
  [`deploy/versions.env`](deploy/versions.env); CI verifies the checksums before use.
- Workflows start with a read-only token, pin third-party actions to commit SHAs, and run bash with pipefail.
- The cluster scripts act only on the `kind-irb` context and refuse any other, so a machine whose kubectl points at
  a real cluster cannot be touched by mistake.
- The model servers and the load client run as non-root users with every capability dropped.
- No credentials are used: the simulator needs none, and the tokenizer is a public Hugging Face model.

## Scope

Vulnerabilities in the projects this benchmark runs (the llm-d Router, the simulator, vLLM, Envoy, kind) belong to
those projects; please report them upstream.
