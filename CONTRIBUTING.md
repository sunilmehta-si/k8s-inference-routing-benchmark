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
`*-rN.json` files into a new `results/<name>/` (the workflow has already set `run_url` on each),
and generate its `README.md` and `chart.svg` with `irb report` and `irb chart`. If the repeats came from more than one
dispatch of the same commit, set `CI_RUNS` on the class to how many. Add a `_OneRunDataset` subclass in
`tests/test_committed_results.py`: it checks the runs are clean, from one CI run, and regenerate the report exactly.

Besides `modes`, `repeats` and `replicas`, a dispatch takes `render_cpu`, the CPU request of the render server the
precise routers tokenize on (default 500m). A dataset from a different value is a different server configuration and
gets its own `results/` directory, as does one from a different `speedup`: a result records the rate it was replayed
at under `replay.speedup`, and `irb report` refuses results whose recorded rates differ.

## State a result

Download the run's `comparison` artifact and let `irb dataset` turn it into `results/<name>/`:

```bash
irb dataset precise-p2 --from ~/Downloads/comparison --modes prefix-active-p2,precise-active-p2 \
  --title "The best approximate router with the real cache picture: 4 simulated vLLM pods, 1,672 requests"
```

It copies each router's eight `*-rN.json` files in the stated order (the column order of the report and the mode order
the dataset test will use), refuses a router with the wrong number of runs, a file holding another router's run, or
runs that are not comparable, and writes `README.md` and `chart.svg` exactly as the tests regenerate them. The workflow
stamps `run_url` into each result; pass `--run-url` for an artifact from before it did. Then add a `_OneRunDataset`
subclass in `tests/test_committed_results.py` with the same mode order and titles, and a test for every sentence the
README will say about the runs.

Print `irb compare` for the pairs you want to talk about before writing a word. The README states a difference only
when it held in every run; say "seven of eight" when it did not.

## Bump a pinned release

Everything the cluster runs is pinned in `deploy/versions.env`; `irb versions` (or `make versions`) says which pins
have a newer release upstream and from which date it counts as adoptable (14 days after publication, so a withdrawn
release is never measured). When the newest release is too new, it names the highest earlier one that is already old
enough, and `--strict` fails on it. The router moves as one: `ROUTER_VERSION`, `ROUTER_COMMIT` and `EPP_IMAGE` change
together, and the CI chart job checks the chart's default scoring still matches `router-default.yaml`. Bump in its own
pull request and wait for the `cluster` workflow on it: a result that moved is the release changing behaviour, and
the pull request should say so.

The release a pin is compared with is the newest stable one: a release candidate is skipped even when upstream marks it
latest, as vLLM does. Dependabot's pull requests for the actions and PyYAML wait the same 14 days (`cooldown` in
`.github/dependabot.yml`, held by `tests/test_dependabot.py`); security updates are not delayed.

## Before you open a pull request

- `python -m unittest discover -s tests -t .` passes.
- Commits are small and say why, not only what. Sign-off is not required.
- Pull requests are reviewed by agentic-code-review-tool on their changed lines; a high finding blocks.

Security issues: see [SECURITY.md](SECURITY.md).
