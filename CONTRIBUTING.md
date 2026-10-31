# Contributing

Thanks for the interest. The repository is small and tested end to end, so most changes fall into one of these.

## Set up

```bash
python -m venv .venv && . .venv/bin/activate
pip install -e .
python -m unittest discover -s tests -t .       # about 15 s; also checks every committed result and claim
```

## Add a router configuration

A router is a file in `deploy/router/`, Helm values for the llm-d Router chart with one scoring change from
`prefix-load-aware.yaml`; `common.yaml` holds everything the routers share. Then register it where the modes are listed:
the `modes` default in `.github/workflows/cluster.yml` (both places), the chart loop in `.github/workflows/ci.yml`,
`KNOWN_PLUGINS` and the scorers table in `tests/test_deploy.py`, and the router table in the README. CI renders every
configuration with the pinned chart and fails on a plugin type the pinned router does not register, so a typo is caught
before a cluster run, not forty minutes into one.

A mode that reads the pods' real caches rather than the picker's estimate adds the `token-producer`,
`endpoint-notification-source` and `precise-prefix-cache-producer` plugins and a `dataLayer` section, as the
`precise-*` files do; keep its profile identical to the approximate mode it mirrors and add the pair to
`PRECISE_COUNTERPARTS` in `tests/test_deploy.py`, which checks exactly that.

## Add a workload

A workload is a spec in `workloads/`; `irb trace generate` turns it into a seeded trace. Pin the trace's sha256 in
`tests/test_reproducible.py` (`FINGERPRINTS`) and say in a test what the trace is for, in numbers (`irb trace stats`).
Traces are not committed; the fingerprint is what makes a run reproducible.

## Run an experiment

Dispatch the `cluster` workflow with the routers, repeats, workload and pod count you want; eight repeats of six
routers take about 35 minutes. A push never cancels a dispatched run. Download the `comparison` artifact, copy the
`*-rN.json` files into a new `results/<name>/`, set `run_url` on each (`inference_routing_bench.results.load`/`save`),
and generate its `README.md` and `chart.svg` with `irb report` and `irb chart`. Add a `_OneRunDataset` subclass in
`tests/test_committed_results.py`: it checks the runs are clean, from one CI run, and regenerate the report exactly.

## State a result

Print `irb compare` for the pairs you want to talk about before writing a word. The README states a difference only
when it held in every run both routers had; "in seven of eight" is said as such. Every claim gets an assertion in the
dataset's test class against `held()` or `pairs()`, so a claim that stops holding fails CI. A superlative across
datasets ("most of any router") is a lead to test in one run, not a result.

## Bump a pinned release

Everything the cluster runs is pinned in `deploy/versions.env`; `irb versions` (or `make versions`) says which pins
have a newer release upstream and from which date it counts as adoptable (14 days after publication, so a withdrawn
release is never measured). The router moves as one: `ROUTER_VERSION`, `ROUTER_COMMIT` and `EPP_IMAGE` change
together, and the CI chart job checks the chart's default scoring still matches `router-default.yaml`. Bump in its own
pull request and wait for the `cluster` workflow on it: a result that moved is the release changing behaviour, and
the pull request should say so.

## Before you open a pull request

- `python -m unittest discover -s tests -t .` passes.
- Commits are small and say why, not only what. Sign-off is not required.
- Pull requests are reviewed by agentic-code-review-tool on their changed lines; a high finding blocks.

Security issues: see [SECURITY.md](SECURITY.md).
